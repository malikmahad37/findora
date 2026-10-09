from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Item, Message, Notification

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    uid = current_user.id

    my_lost_count  = Item.query.filter_by(user_id=uid, item_type='lost').count()
    my_found_count = Item.query.filter_by(user_id=uid, item_type='found').count()

    my_active_items = (
        Item.query
        .filter(
            Item.user_id == uid,
            Item.status.in_(('active', 'possible_match', 'claim_pending'))
        )
        .order_by(Item.created_at.desc())
        .all()
    )

    my_resolved_items = (
        Item.query
        .filter(
            Item.user_id == uid,
            Item.status.in_(('resolved', 'returned', 'closed'))
        )
        .order_by(Item.updated_at.desc())
        .all()
    )

    possible_matches_count = (
        Item.query
        .filter_by(user_id=uid, status='possible_match')
        .count()
    )

    unread_messages_count = (
        Message.query
        .filter_by(receiver_id=uid, is_read=False)
        .count()
    )

    recent_notifications = (
        Notification.query
        .filter_by(user_id=uid, is_read=False)
        .order_by(Notification.created_at.desc())
        .limit(5)
        .all()
    )

    recent_my_items = (
        Item.query
        .filter_by(user_id=uid)
        .order_by(Item.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        'dashboard/index.html',
        my_lost_count=my_lost_count,
        my_found_count=my_found_count,
        my_active_items=my_active_items,
        my_resolved_items=my_resolved_items,
        possible_matches_count=possible_matches_count,
        unread_messages_count=unread_messages_count,
        recent_notifications=recent_notifications,
        recent_my_items=recent_my_items,
    )
