from functools import wraps

from flask import Blueprint, render_template, redirect, request, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.models import (
    User, Item, Claim, Report, Notification, ActivityLog,
    Category,
    LocationCountry, LocationRegion, LocationCity, LocationArea,
)

admin_bp = Blueprint("admin", __name__)


# ── Admin guard decorator ─────────────────────────────────────────────────────

def admin_required(f):
    """Decorator that aborts with 403 unless the user is an authenticated admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    """Admin overview with site-wide statistics and recent activity."""
    stats = {
        "total_users":    User.query.count(),
        "total_lost":     Item.query.filter_by(item_type="lost").count(),
        "total_found":    Item.query.filter_by(item_type="found").count(),
        "active_items":   Item.query.filter(
                              Item.status.in_(["active", "possible_match"])
                          ).count(),
        "resolved_items": Item.query.filter(
                              Item.status.in_(["resolved", "returned"])
                          ).count(),
        "pending_claims": Claim.query.filter_by(status="pending").count(),
        "reported_items": Report.query.filter_by(status="pending").count(),
        "total_claims":   Claim.query.count(),
    }
    recent_logs = (
        ActivityLog.query
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_logs=recent_logs,
    )


# ── Users ─────────────────────────────────────────────────────────────────────

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    """Paginated list of all users with optional search by name or email."""
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()

    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            User.full_name.ilike(like) | User.email.ilike(like)
        )
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/users.html",
        users=pagination.items,
        pagination=pagination,
        q=q,
    )


@admin_bp.route("/users/<int:user_id>")
@login_required
@admin_required
def user_detail(user_id):
    """Detail view showing a user's info, their items, and recent activity."""
    user = User.query.get_or_404(user_id)
    items = user.items.order_by(Item.created_at.desc()).limit(20).all()
    recent_activity = (
        ActivityLog.query
        .filter_by(user_id=user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template(
        "admin/user_detail.html",
        user=user,
        items=items,
        recent_activity=recent_activity,
    )


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Activate or deactivate a user account. Cannot disable own account."""
    if user_id == current_user.id:
        flash("You cannot disable your own account.", "danger")
        return redirect(request.referrer or url_for("admin.users"))

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    state = "activated" if user.is_active else "deactivated"
    flash(f"User \"{user.full_name}\" has been {state}.", "success")
    return redirect(request.referrer or url_for("admin.users"))


# ── Posts (Items) ─────────────────────────────────────────────────────────────

@admin_bp.route("/posts")
@login_required
@admin_required
def posts():
    """Paginated list of all items with optional type and status filters."""
    page = request.args.get("page", 1, type=int)
    item_type = request.args.get("type", "").strip()
    status = request.args.get("status", "").strip()

    query = Item.query
    if item_type in ("lost", "found"):
        query = query.filter_by(item_type=item_type)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Item.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/posts.html",
        items=pagination.items,
        pagination=pagination,
        selected_type=item_type,
        selected_status=status,
    )


@admin_bp.route("/posts/<int:item_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_post(item_id):
    """Delete an item and send a notification to its owner."""
    item = Item.query.get_or_404(item_id)
    owner_id = item.user_id
    title = item.title

    db.session.delete(item)

    notif = Notification(
        user_id=owner_id,
        notif_type="post_moderated",
        message=f'Your post "{title}" was removed by an administrator.',
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Post "{title}" has been deleted.', "success")
    return redirect(request.referrer or url_for("admin.posts"))


@admin_bp.route("/posts/<int:item_id>/status", methods=["POST"])
@login_required
@admin_required
def update_post_status(item_id):
    """Update the status field of an item."""
    item = Item.query.get_or_404(item_id)
    new_status = request.form.get("status", "").strip()
    valid_statuses = {
        "active", "possible_match", "claim_pending",
        "resolved", "returned", "closed",
    }
    if new_status not in valid_statuses:
        flash("Invalid status value.", "danger")
        return redirect(request.referrer or url_for("admin.posts"))

    item.status = new_status
    db.session.commit()
    flash(f'Item status updated to "{new_status}".', "success")
    return redirect(request.referrer or url_for("admin.posts"))


# ── Claims ────────────────────────────────────────────────────────────────────

@admin_bp.route("/claims")
@login_required
@admin_required
def claims():
    """Paginated list of all claims with optional status filter."""
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "").strip()

    query = Claim.query
    if status in ("pending", "accepted", "rejected"):
        query = query.filter_by(status=status)

    pagination = query.order_by(Claim.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/claims.html",
        claims=pagination.items,
        pagination=pagination,
        selected_status=status,
    )


# ── Reports ───────────────────────────────────────────────────────────────────

@admin_bp.route("/reports")
@login_required
@admin_required
def reports():
    """Paginated list of all reports with optional status filter."""
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "").strip()

    query = Report.query
    if status in ("pending", "reviewed", "resolved"):
        query = query.filter_by(status=status)

    pagination = query.order_by(Report.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/reports.html",
        reports=pagination.items,
        pagination=pagination,
        selected_status=status,
    )


@admin_bp.route("/reports/<int:report_id>/resolve", methods=["POST"])
@login_required
@admin_required
def resolve_report(report_id):
    """Mark a report as resolved."""
    report = Report.query.get_or_404(report_id)
    report.status = "resolved"
    db.session.commit()
    flash("Report marked as resolved.", "success")
    return redirect(request.referrer or url_for("admin.reports"))


# ── Locations ─────────────────────────────────────────────────────────────────

@admin_bp.route("/locations")
@login_required
@admin_required
def locations():
    """Show the complete location hierarchy (countries → regions → cities → areas)."""
    countries = LocationCountry.query.order_by(LocationCountry.name).all()
    return render_template("admin/locations.html", countries=countries)


@admin_bp.route("/locations/add-country", methods=["POST"])
@login_required
@admin_required
def add_country():
    """Add a new country."""
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip()
    if not name:
        flash("Country name is required.", "danger")
        return redirect(url_for("admin.locations"))
    country = LocationCountry(name=name, code=code or None)
    db.session.add(country)
    db.session.commit()
    flash(f'Country "{name}" added.', "success")
    return redirect(url_for("admin.locations"))


@admin_bp.route("/locations/add-region", methods=["POST"])
@login_required
@admin_required
def add_region():
    """Add a new region inside a country."""
    name = request.form.get("name", "").strip()
    country_id = request.form.get("country_id", type=int)
    if not name or not country_id:
        flash("Region name and country are required.", "danger")
        return redirect(url_for("admin.locations"))
    LocationCountry.query.get_or_404(country_id)
    region = LocationRegion(name=name, country_id=country_id)
    db.session.add(region)
    db.session.commit()
    flash(f'Region "{name}" added.', "success")
    return redirect(url_for("admin.locations"))


@admin_bp.route("/locations/add-city", methods=["POST"])
@login_required
@admin_required
def add_city():
    """Add a new city inside a region."""
    name = request.form.get("name", "").strip()
    region_id = request.form.get("region_id", type=int)
    if not name or not region_id:
        flash("City name and region are required.", "danger")
        return redirect(url_for("admin.locations"))
    LocationRegion.query.get_or_404(region_id)
    city = LocationCity(name=name, region_id=region_id)
    db.session.add(city)
    db.session.commit()
    flash(f'City "{name}" added.', "success")
    return redirect(url_for("admin.locations"))


@admin_bp.route("/locations/add-area", methods=["POST"])
@login_required
@admin_required
def add_area():
    """Add a new area inside a city."""
    name = request.form.get("name", "").strip()
    city_id = request.form.get("city_id", type=int)
    if not name or not city_id:
        flash("Area name and city are required.", "danger")
        return redirect(url_for("admin.locations"))
    LocationCity.query.get_or_404(city_id)
    area = LocationArea(name=name, city_id=city_id)
    db.session.add(area)
    db.session.commit()
    flash(f'Area "{name}" added.', "success")
    return redirect(url_for("admin.locations"))


@admin_bp.route("/locations/delete/<string:loc_type>/<int:loc_id>", methods=["POST"])
@login_required
@admin_required
def delete_location(loc_type, loc_id):
    """Delete a location record by type (country/region/city/area) and id."""
    model_map = {
        "country": LocationCountry,
        "region":  LocationRegion,
        "city":    LocationCity,
        "area":    LocationArea,
    }
    model = model_map.get(loc_type)
    if model is None:
        flash("Invalid location type.", "danger")
        return redirect(url_for("admin.locations"))

    location = model.query.get_or_404(loc_id)
    db.session.delete(location)
    db.session.commit()
    flash(f"{loc_type.capitalize()} deleted successfully.", "success")
    return redirect(url_for("admin.locations"))


# ── Categories ────────────────────────────────────────────────────────────────

@admin_bp.route("/categories")
@login_required
@admin_required
def categories():
    """List all categories."""
    all_categories = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", categories=all_categories)


@admin_bp.route("/categories/add", methods=["POST"])
@login_required
@admin_required
def add_category():
    """Create a new category."""
    name = request.form.get("name", "").strip()
    icon = request.form.get("icon", "").strip() or "📦"
    if not name:
        flash("Category name is required.", "danger")
        return redirect(url_for("admin.categories"))
    existing = Category.query.filter_by(name=name).first()
    if existing:
        flash(f'A category named "{name}" already exists.', "warning")
        return redirect(url_for("admin.categories"))
    category = Category(name=name, icon=icon)
    db.session.add(category)
    db.session.commit()
    flash(f'Category "{name}" added.', "success")
    return redirect(url_for("admin.categories"))


@admin_bp.route("/categories/<int:cat_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_category(cat_id):
    """Toggle the is_active flag of a category."""
    category = Category.query.get_or_404(cat_id)
    category.is_active = not category.is_active
    db.session.commit()
    state = "activated" if category.is_active else "deactivated"
    flash(f'Category "{category.name}" {state}.', "success")
    return redirect(url_for("admin.categories"))


@admin_bp.route("/categories/<int:cat_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_category(cat_id):
    """Delete a category only when it has no associated items."""
    category = Category.query.get_or_404(cat_id)
    if category.items.count() > 0:
        flash(
            f'Cannot delete "{category.name}" because it has associated items.',
            "danger",
        )
        return redirect(url_for("admin.categories"))
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{category.name}" deleted.', "success")
    return redirect(url_for("admin.categories"))
