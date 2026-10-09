import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, subfolder='items'):
    """Saves an uploaded FileStorage object; returns relative path or None."""
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, unique_name))
    return f"{subfolder}/{unique_name}"


def log_activity(action, details=None, user_id=None):
    """Log an activity to the ActivityLog table."""
    from flask import request
    from app import db
    from app.models import ActivityLog
    try:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr if request else None
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()


def create_notification(user_id, notif_type, message, link=None):
    """Create a notification for a user."""
    from app import db
    from app.models import Notification
    try:
        notif = Notification(
            user_id=user_id,
            notif_type=notif_type,
            message=message,
            link=link
        )
        db.session.add(notif)
        db.session.commit()
    except Exception:
        db.session.rollback()


def format_date(dt):
    if dt is None:
        return ''
    return dt.strftime('%d %b %Y')


def time_ago(dt):
    """Return human-readable relative time string."""
    from datetime import datetime
    if dt is None:
        return ''
    now = datetime.utcnow()
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        m = seconds // 60
        return f'{m} minute{"s" if m > 1 else ""} ago'
    elif seconds < 86400:
        h = seconds // 3600
        return f'{h} hour{"s" if h > 1 else ""} ago'
    elif seconds < 604800:
        d = seconds // 86400
        return f'{d} day{"s" if d > 1 else ""} ago'
    else:
        return format_date(dt)
