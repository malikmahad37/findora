from flask import Blueprint, render_template, request
from app import db
from app.models import Item, Category, LocationCountry, User

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    total_lost = Item.query.filter_by(item_type='lost').count()
    total_found = Item.query.filter_by(item_type='found').count()
    total_resolved = Item.query.filter(
        Item.status.in_(('resolved', 'returned'))
    ).count()
    total_users = User.query.filter_by(is_active=True).count()

    recent_items = (
        Item.query
        .filter(Item.status.in_(('active', 'possible_match', 'claim_pending')))
        .order_by(Item.created_at.desc())
        .limit(6)
        .all()
    )

    return render_template(
        'index.html',
        total_lost=total_lost,
        total_found=total_found,
        total_resolved=total_resolved,
        total_users=total_users,
        recent_items=recent_items,
    )


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/browse')
def browse():
    item_type   = request.args.get('type', '').strip()
    category_id = request.args.get('category_id', type=int)
    country_id  = request.args.get('country_id',  type=int)
    region_id   = request.args.get('region_id',   type=int)
    city_id     = request.args.get('city_id',     type=int)
    sort        = request.args.get('sort', 'newest').strip()
    page        = request.args.get('page', 1, type=int)

    query = Item.query.filter(
        Item.status.in_(('active', 'possible_match', 'claim_pending'))
    )

    if item_type in ('lost', 'found'):
        query = query.filter_by(item_type=item_type)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if country_id:
        query = query.filter_by(country_id=country_id)
    if region_id:
        query = query.filter_by(region_id=region_id)
    if city_id:
        query = query.filter_by(city_id=city_id)

    if sort == 'oldest':
        query = query.order_by(Item.created_at.asc())
    else:
        query = query.order_by(Item.created_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    countries  = LocationCountry.query.order_by(LocationCountry.name).all()

    return render_template(
        'items/browse.html',
        items=pagination,
        categories=categories,
        countries=countries,
        selected_type=item_type,
        selected_category_id=category_id,
        selected_country_id=country_id,
        selected_region_id=region_id,
        selected_city_id=city_id,
        sort=sort,
    )


@main_bp.route('/search')
def search():
    q           = request.args.get('q', '').strip()
    item_type   = request.args.get('type', '').strip()
    category_id = request.args.get('category_id', type=int)
    city_id     = request.args.get('city_id',     type=int)
    status      = request.args.get('status', '').strip()
    date_from   = request.args.get('date_from', '').strip()
    date_to     = request.args.get('date_to', '').strip()
    sort        = request.args.get('sort', 'newest').strip()
    page        = request.args.get('page', 1, type=int)

    query = Item.query

    if q:
        like_q = f'%{q}%'
        query = query.filter(
            db.or_(
                Item.title.ilike(like_q),
                Item.description.ilike(like_q),
                Item.brand.ilike(like_q),
                Item.color.ilike(like_q),
            )
        )

    if item_type in ('lost', 'found'):
        query = query.filter_by(item_type=item_type)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if city_id:
        query = query.filter_by(city_id=city_id)

    valid_statuses = ('active', 'possible_match', 'claim_pending', 'resolved', 'returned', 'closed')
    if status and status in valid_statuses:
        query = query.filter_by(status=status)

    if date_from:
        try:
            from datetime import datetime as dt
            query = query.filter(Item.date_occurred >= dt.strptime(date_from, '%Y-%m-%d').date())
        except ValueError:
            pass

    if date_to:
        try:
            from datetime import datetime as dt
            query = query.filter(Item.date_occurred <= dt.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            pass

    if sort == 'oldest':
        query = query.order_by(Item.created_at.asc())
    else:
        query = query.order_by(Item.created_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()

    return render_template(
        'items/search.html',
        items=pagination,
        categories=categories,
        q=q,
        selected_type=item_type,
        selected_category_id=category_id,
        selected_city_id=city_id,
        selected_status=status,
        date_from=date_from,
        date_to=date_to,
        sort=sort,
    )


def page_not_found(e):
    return render_template('errors/404.html'), 404


def forbidden(e):
    return render_template('errors/403.html'), 403


def internal_error(e):
    db.session.rollback()
    return render_template('errors/500.html'), 500
