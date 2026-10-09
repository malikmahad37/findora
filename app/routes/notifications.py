from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Notification

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/")
@login_required
def index():
    """List all notifications for the current user, newest first, paginated."""
    page = request.args.get("page", 1, type=int)
    pagination = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    notifications = pagination.items
    return render_template(
        "notifications/index.html",
        notifications=notifications,
        pagination=pagination,
    )


@notifications_bp.route("/mark-read/<int:notif_id>", methods=["POST"])
@login_required
def mark_read(notif_id):
    """Mark a single notification as read."""
    notif = Notification.query.filter_by(
        id=notif_id, user_id=current_user.id
    ).first_or_404()
    notif.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for("notifications.index"))


@notifications_bp.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all_read():
    """Mark every unread notification for the current user as read."""
    Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).update({"is_read": True})
    db.session.commit()
    flash("All notifications marked as read.", "success")
    return redirect(request.referrer or url_for("notifications.index"))
