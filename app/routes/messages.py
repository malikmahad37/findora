from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Message, User, Item
from app.utils import create_notification, log_activity

messages_bp = Blueprint('messages', __name__)


def _build_conversation_list(messages):
    """
    Given messages involving current_user, build a list of unique partner conversations
    with their most recent message.
    """
    conversations = {}
    for msg in messages:
        other_id = msg.sender_id if msg.receiver_id == current_user.id else msg.receiver_id
        if other_id not in conversations:
            conversations[other_id] = msg
        else:
            if msg.created_at > conversations[other_id].created_at:
                conversations[other_id] = msg
    return list(conversations.values())


@messages_bp.route('/')
@login_required
def inbox():
    all_msgs = (
        Message.query
        .filter(
            db.or_(
                Message.receiver_id == current_user.id,
                Message.sender_id == current_user.id
            )
        )
        .order_by(Message.created_at.desc())
        .all()
    )
    conversations = _build_conversation_list(all_msgs)
    unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()

    return render_template(
        'messages/inbox.html',
        conversations=conversations,
        unread_count=unread_count,
    )


@messages_bp.route('/sent')
@login_required
def sent():
    sent_messages = (
        Message.query
        .filter_by(sender_id=current_user.id)
        .order_by(Message.created_at.desc())
        .all()
    )
    return render_template('messages/sent.html', sent_messages=sent_messages)


@messages_bp.route('/conversation/<int:other_user_id>', methods=['GET', 'POST'])
@login_required
def conversation(other_user_id):
    if other_user_id == current_user.id:
        flash('You cannot message yourself.', 'warning')
        return redirect(url_for('messages.inbox'))

    other_user = User.query.get_or_404(other_user_id)
    item_id = request.args.get('item_id', type=int)
    item = Item.query.get(item_id) if item_id else None

    if request.method == 'POST':
        body = request.form.get('body', '').strip()
        item_id_form = request.form.get('item_id', type=int) or item_id

        if not body:
            flash('Message body cannot be empty.', 'warning')
            return redirect(url_for('messages.conversation', other_user_id=other_user_id, item_id=item_id))

        new_msg = Message(
            sender_id=current_user.id,
            receiver_id=other_user_id,
            body=body,
            item_id=item_id_form,
            is_read=False
        )
        db.session.add(new_msg)
        db.session.commit()

        create_notification(
            user_id=other_user_id,
            notif_type='new_message',
            message=f'New message from {current_user.full_name}.',
            link=url_for('messages.conversation', other_user_id=current_user.id, item_id=item_id_form)
        )

        return redirect(url_for('messages.conversation', other_user_id=other_user_id, item_id=item_id_form))

    # Mark all incoming messages from this user as read
    incoming_unread = Message.query.filter_by(
        sender_id=other_user_id,
        receiver_id=current_user.id,
        is_read=False
    ).all()
    for m in incoming_unread:
        m.is_read = True
    if incoming_unread:
        db.session.commit()

    thread = (
        Message.query
        .filter(
            db.or_(
                db.and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
                db.and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id)
            )
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    return render_template(
        'messages/conversation.html',
        thread=thread,
        other_user=other_user,
        item=item,
    )


@messages_bp.route('/send', methods=['POST'])
@login_required
def send_message_post():
    receiver_id = request.form.get('receiver_id', type=int)
    item_id = request.form.get('item_id', type=int)
    body = request.form.get('body', '').strip()

    if not receiver_id or not body:
        flash('Recipient and message text are required.', 'danger')
        return redirect(request.referrer or url_for('messages.inbox'))

    if receiver_id == current_user.id:
        flash('You cannot message yourself.', 'warning')
        return redirect(request.referrer or url_for('messages.inbox'))

    receiver = User.query.get_or_404(receiver_id)

    msg = Message(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        item_id=item_id,
        body=body,
        is_read=False
    )
    db.session.add(msg)
    db.session.commit()

    create_notification(
        user_id=receiver.id,
        notif_type='new_message',
        message=f'New message from {current_user.full_name}.',
        link=url_for('messages.conversation', other_user_id=current_user.id, item_id=item_id)
    )

    flash('Message sent successfully!', 'success')
    return redirect(url_for('messages.conversation', other_user_id=receiver.id, item_id=item_id))
