import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Optional
from app import db
from app.models import Item, Category, Claim, LocationCountry, LocationRegion, LocationCity, LocationArea
from app.utils import save_uploaded_file, create_notification, log_activity

items_bp = Blueprint('items', __name__)


# ---------------------------------------------------------------------------
# Form
# ---------------------------------------------------------------------------

class ItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    category_id = SelectField('Category', coerce=int)
    date_occurred = DateField('Date Occurred', validators=[DataRequired()])
    country_id = SelectField('Country', coerce=int, choices=[(0, '-- Select Country --')])
    region_id = SelectField('Region / State', coerce=int, choices=[(0, '-- Select Region --')])
    city_id = SelectField('City', coerce=int, choices=[(0, '-- Select City --')])
    area_id = SelectField('Area / Locality', coerce=int, choices=[(0, '-- Select Area --')])
    location_text = StringField('Specific Address / Landmark', validators=[Optional(), Length(max=300)])
    brand = StringField('Brand', validators=[Optional(), Length(max=100)])
    color = StringField('Color', validators=[Optional(), Length(max=80)])
    identifying_details = TextAreaField('Identifying Details', validators=[Optional()])
    image = FileField('Image (optional)')
    contact_preference = SelectField(
        'Contact Preference',
        choices=[
            ('message', 'Internal Message'),
            ('phone', 'Phone Call'),
        ]
    )


def _populate_form_choices(form, item=None):
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    form.category_id.choices = [(0, '-- Select Category --')] + [(c.id, c.name) for c in categories]

    countries = LocationCountry.query.order_by(LocationCountry.name).all()
    form.country_id.choices = [(0, '-- Select Country --')] + [(c.id, c.name) for c in countries]

    # For regions, cities, areas: populate all valid options so WTForms validation passes on submit
    regions = LocationRegion.query.order_by(LocationRegion.name).all()
    form.region_id.choices = [(0, '-- Select Region --')] + [(r.id, r.name) for r in regions]

    cities = LocationCity.query.order_by(LocationCity.name).all()
    form.city_id.choices = [(0, '-- Select City --')] + [(ct.id, ct.name) for ct in cities]

    areas = LocationArea.query.order_by(LocationArea.name).all()
    form.area_id.choices = [(0, '-- Select Area --')] + [(a.id, a.name) for a in areas]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@items_bp.route('/lost/new', methods=['GET', 'POST'])
@login_required
def post_lost():
    form = ItemForm()
    _populate_form_choices(form)

    if form.validate_on_submit():
        image_path = None
        if form.image.data and hasattr(form.image.data, 'filename') and form.image.data.filename:
            image_path = save_uploaded_file(form.image.data, subfolder='items')

        item = Item(
            item_type='lost',
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else '',
            category_id=form.category_id.data if form.category_id.data and form.category_id.data > 0 else None,
            date_occurred=form.date_occurred.data,
            country_id=form.country_id.data if form.country_id.data and form.country_id.data > 0 else None,
            region_id=form.region_id.data if form.region_id.data and form.region_id.data > 0 else None,
            city_id=form.city_id.data if form.city_id.data and form.city_id.data > 0 else None,
            area_id=form.area_id.data if form.area_id.data and form.area_id.data > 0 else None,
            location_text=form.location_text.data.strip() if form.location_text.data else '',
            brand=form.brand.data.strip() if form.brand.data else '',
            color=form.color.data.strip() if form.color.data else '',
            identifying_details=form.identifying_details.data.strip() if form.identifying_details.data else '',
            image_path=image_path,
            contact_preference=form.contact_preference.data,
            user_id=current_user.id,
            status='active',
        )
        db.session.add(item)
        db.session.commit()

        try:
            from app.services.matching import run_matching_for_item
            run_matching_for_item(item)
        except Exception:
            pass

        log_activity('post_lost', f'Posted lost item: {item.title}', user_id=current_user.id)
        flash('Your lost item report has been published successfully.', 'success')
        return redirect(url_for('items.detail', item_id=item.id))

    return render_template('items/post_item.html', form=form, item_type='lost')


@items_bp.route('/found/new', methods=['GET', 'POST'])
@login_required
def post_found():
    form = ItemForm()
    _populate_form_choices(form)

    if form.validate_on_submit():
        image_path = None
        if form.image.data and hasattr(form.image.data, 'filename') and form.image.data.filename:
            image_path = save_uploaded_file(form.image.data, subfolder='items')

        item = Item(
            item_type='found',
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else '',
            category_id=form.category_id.data if form.category_id.data and form.category_id.data > 0 else None,
            date_occurred=form.date_occurred.data,
            country_id=form.country_id.data if form.country_id.data and form.country_id.data > 0 else None,
            region_id=form.region_id.data if form.region_id.data and form.region_id.data > 0 else None,
            city_id=form.city_id.data if form.city_id.data and form.city_id.data > 0 else None,
            area_id=form.area_id.data if form.area_id.data and form.area_id.data > 0 else None,
            location_text=form.location_text.data.strip() if form.location_text.data else '',
            brand=form.brand.data.strip() if form.brand.data else '',
            color=form.color.data.strip() if form.color.data else '',
            identifying_details=form.identifying_details.data.strip() if form.identifying_details.data else '',
            image_path=image_path,
            contact_preference=form.contact_preference.data,
            user_id=current_user.id,
            status='active',
        )
        db.session.add(item)
        db.session.commit()

        try:
            from app.services.matching import run_matching_for_item
            run_matching_for_item(item)
        except Exception:
            pass

        log_activity('post_found', f'Posted found item: {item.title}', user_id=current_user.id)
        flash('Your found item report has been published successfully.', 'success')
        return redirect(url_for('items.detail', item_id=item.id))

    return render_template('items/post_item.html', form=form, item_type='found')


@items_bp.route('/<int:item_id>')
def detail(item_id):
    item = Item.query.get_or_404(item_id)

    matches = []
    claims = []
    is_owner = current_user.is_authenticated and current_user.id == item.user_id

    if is_owner:
        try:
            from app.services.matching import find_matches
            matches = find_matches(item, threshold=40)
        except Exception:
            matches = []
        claims = Claim.query.filter_by(item_id=item.id).order_by(Claim.created_at.desc()).all()

    return render_template(
        'items/detail.html',
        item=item,
        matches=matches,
        claims=claims,
        is_owner=is_owner,
    )


@items_bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    item = Item.query.get_or_404(item_id)

    if item.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    form = ItemForm(obj=item)
    _populate_form_choices(form)

    if form.validate_on_submit():
        item.title = form.title.data.strip()
        item.description = form.description.data.strip() if form.description.data else ''
        item.category_id = form.category_id.data if form.category_id.data and form.category_id.data > 0 else None
        item.date_occurred = form.date_occurred.data
        item.country_id = form.country_id.data if form.country_id.data and form.country_id.data > 0 else None
        item.region_id = form.region_id.data if form.region_id.data and form.region_id.data > 0 else None
        item.city_id = form.city_id.data if form.city_id.data and form.city_id.data > 0 else None
        item.area_id = form.area_id.data if form.area_id.data and form.area_id.data > 0 else None
        item.location_text = form.location_text.data.strip() if form.location_text.data else ''
        item.brand = form.brand.data.strip() if form.brand.data else ''
        item.color = form.color.data.strip() if form.color.data else ''
        item.identifying_details = form.identifying_details.data.strip() if form.identifying_details.data else ''
        item.contact_preference = form.contact_preference.data

        if form.image.data and hasattr(form.image.data, 'filename') and form.image.data.filename:
            saved = save_uploaded_file(form.image.data, subfolder='items')
            if saved:
                item.image_path = saved

        db.session.commit()
        flash('Item post updated successfully.', 'success')
        return redirect(url_for('items.detail', item_id=item.id))

    return render_template('items/edit.html', form=form, item=item)


@items_bp.route('/<int:item_id>/delete', methods=['POST'])
@login_required
def delete(item_id):
    item = Item.query.get_or_404(item_id)

    if item.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    db.session.delete(item)
    db.session.commit()
    log_activity('delete_item', f'Deleted item: {item.title}', user_id=current_user.id)
    flash('Item post has been deleted successfully.', 'success')
    return redirect(url_for('items.my_posts'))


@items_bp.route('/<int:item_id>/status', methods=['POST'])
@login_required
def update_status(item_id):
    item = Item.query.get_or_404(item_id)

    if item.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    allowed_statuses = ['active', 'possible_match', 'claim_pending', 'resolved', 'returned', 'closed']
    new_status = request.form.get('new_status', '').strip()

    if new_status not in allowed_statuses:
        flash('Invalid status value provided.', 'danger')
        return redirect(request.referrer or url_for('items.detail', item_id=item.id))

    item.status = new_status
    db.session.commit()
    flash(f'Item status updated to "{new_status.replace("_", " ").title()}".', 'success')
    return redirect(request.referrer or url_for('items.detail', item_id=item.id))


@items_bp.route('/my-posts')
@login_required
def my_posts():
    page = request.args.get('page', 1, type=int)
    type_filter = request.args.get('type', '').strip()

    query = Item.query.filter_by(user_id=current_user.id)
    if type_filter in ('lost', 'found'):
        query = query.filter_by(item_type=type_filter)

    pagination = query.order_by(Item.created_at.desc()).paginate(page=page, per_page=12, error_out=False)

    return render_template(
        'items/my_posts.html',
        items=pagination,
        type_filter=type_filter,
    )
