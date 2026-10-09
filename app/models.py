from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


# ─────────────────────────────────────────────
#  USER
# ─────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' | 'admin'
    phone = db.Column(db.String(30))
    avatar = db.Column(db.String(200))  # path to uploaded avatar
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    items = db.relationship('Item', backref='poster', lazy='dynamic', foreign_keys='Item.user_id')
    sent_messages = db.relationship('Message', backref='sender', lazy='dynamic', foreign_keys='Message.sender_id')
    received_messages = db.relationship('Message', backref='receiver', lazy='dynamic', foreign_keys='Message.receiver_id')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    claims = db.relationship('Claim', backref='claimant', lazy='dynamic', foreign_keys='Claim.claimant_id')
    reports = db.relationship('Report', backref='reporter', lazy='dynamic', foreign_keys='Report.reporter_id')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def initials(self):
        parts = self.full_name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.full_name[:2].upper()

    def __repr__(self):
        return f'<User {self.email}>'


# ─────────────────────────────────────────────
#  LOCATION HIERARCHY
# ─────────────────────────────────────────────
class LocationCountry(db.Model):
    __tablename__ = 'location_countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10))
    regions = db.relationship('LocationRegion', backref='country', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Country {self.name}>'


class LocationRegion(db.Model):
    __tablename__ = 'location_regions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('location_countries.id'), nullable=False)
    cities = db.relationship('LocationCity', backref='region', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Region {self.name}>'


class LocationCity(db.Model):
    __tablename__ = 'location_cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('location_regions.id'), nullable=False)
    areas = db.relationship('LocationArea', backref='city', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<City {self.name}>'


class LocationArea(db.Model):
    __tablename__ = 'location_areas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('location_cities.id'), nullable=False)

    def __repr__(self):
        return f'<Area {self.name}>'


# ─────────────────────────────────────────────
#  CATEGORY
# ─────────────────────────────────────────────
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='📦')
    is_active = db.Column(db.Boolean, default=True)
    items = db.relationship('Item', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


# ─────────────────────────────────────────────
#  ITEM (Lost / Found)
# ─────────────────────────────────────────────
class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_type = db.Column(db.String(10), nullable=False)  # 'lost' | 'found'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    date_occurred = db.Column(db.Date, nullable=False)

    # Location
    country_id = db.Column(db.Integer, db.ForeignKey('location_countries.id'))
    region_id = db.Column(db.Integer, db.ForeignKey('location_regions.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('location_cities.id'))
    area_id = db.Column(db.Integer, db.ForeignKey('location_areas.id'))
    location_text = db.Column(db.String(300))  # free-text fallback / combined label

    brand = db.Column(db.String(100))
    color = db.Column(db.String(80))
    identifying_details = db.Column(db.Text)
    image_path = db.Column(db.String(300))
    contact_preference = db.Column(db.String(20), default='message')  # 'message' | 'phone'

    status = db.Column(db.String(30), default='active')
    # active | possible_match | claim_pending | resolved | returned | closed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    country = db.relationship('LocationCountry', foreign_keys=[country_id])
    region = db.relationship('LocationRegion', foreign_keys=[region_id])
    city = db.relationship('LocationCity', foreign_keys=[city_id])
    area = db.relationship('LocationArea', foreign_keys=[area_id])
    messages = db.relationship('Message', backref='item', lazy='dynamic')
    claims = db.relationship('Claim', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='item', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def full_location(self):
        parts = []
        if self.area:
            parts.append(self.area.name)
        if self.city:
            parts.append(self.city.name)
        if self.region:
            parts.append(self.region.name)
        if self.country:
            parts.append(self.country.name)
        return ', '.join(parts) if parts else (self.location_text or 'Unknown')

    @property
    def is_active_status(self):
        return self.status in ('active', 'possible_match')

    def __repr__(self):
        return f'<Item [{self.item_type}] {self.title}>'


# ─────────────────────────────────────────────
#  MESSAGE
# ─────────────────────────────────────────────
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.sender_id}→{self.receiver_id}>'


# ─────────────────────────────────────────────
#  NOTIFICATION
# ─────────────────────────────────────────────
class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notif_type = db.Column(db.String(40))
    # Types: new_message | match_found | claim_submitted | claim_accepted |
    #        claim_rejected | post_moderated | item_resolved
    message = db.Column(db.String(300))
    link = db.Column(db.String(300))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.user_id} {self.notif_type}>'


# ─────────────────────────────────────────────
#  CLAIM
# ─────────────────────────────────────────────
class Claim(db.Model):
    __tablename__ = 'claims'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    details = db.Column(db.Text, nullable=False)
    where_lost = db.Column(db.String(300))
    approx_date = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending | accepted | rejected
    admin_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Claim item={self.item_id} by={self.claimant_id}>'


# ─────────────────────────────────────────────
#  REPORT
# ─────────────────────────────────────────────
class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    reason = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending | reviewed | resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Report item={self.item_id}>'


# ─────────────────────────────────────────────
#  ACTIVITY LOG
# ─────────────────────────────────────────────
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ActivityLog {self.action}>'
