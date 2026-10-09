from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField
from wtforms.validators import DataRequired, Optional, Length
from app import db
from app.models import Claim, Item
from app.utils import create_notification, log_activity

claims_bp = Blueprint('claims', __name__)


class ClaimForm(FlaskForm):
    details = TextAreaField(
        'Verification Details (e.g. unique scratches, serial numbers, wallpaper, contents)',
        validators=[DataRequired(message='Please provide detailed identifying information.')]
    )
    where_lost = StringField('Where do you believe you lost it?', validators=[Optional(), Length(max=300)])
    approx_date = StringField('Approximate Date & Time', validators=[Optional(), Length(max=100)])


@claims_bp.route('/submit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def submit_claim(item_id):
    item = Item.query.get_or_404(item_id)

    if item.item_type != 'found':
        flash('Claims can only be filed against found items.', 'warning')
        return redirect(url_for('items.detail', item_id=item.id))

    if item.user_id == current_user.id:
        flash('You cannot claim an item you reported.', 'danger')
        return redirect(url_for('items.detail', item_id=item.id))

    existing = Claim.query.filter_by(item_id=item.id, claimant_id=current_user.id).first()
    if existing:
        flash(f'You already submitted a claim for this item (Status: {existing.status.capitalize()}).', 'info')
        return redirect(url_for('items.detail', item_id=item.id))

    form = ClaimForm()
    if form.validate_on_submit():
        claim = Claim(
            item_id=item.id,
            claimant_id=current_user.id,
            details=form.details.data.strip(),
            where_lost=form.where_lost.data.strip() if form.where_lost.data else '',
            approx_date=form.approx_date.data.strip() if form.approx_date.data else '',
            status='pending'
        )
        db.session.add(claim)

        if item.status == 'active':
            item.status = 'claim_pending'

        db.session.commit()

        create_notification(
            user_id=item.user_id,
            notif_type='claim_submitted',
            message=f'New claim submitted by {current_user.full_name} for "{item.title}".',
            link=url_for('claims.received_claims')
        )

        log_activity('submit_claim', f'Claim submitted on item #{item.id}', user_id=current_user.id)
        flash('Your ownership claim has been submitted for verification.', 'success')
        return redirect(url_for('claims.my_claims'))

    return render_template('claims/submit.html', form=form, item=item)


@claims_bp.route('/my-claims')
@login_required
def my_claims():
    claims = (
        Claim.query
        .filter_by(claimant_id=current_user.id)
        .order_by(Claim.created_at.desc())
        .all()
    )
    return render_template('claims/my_claims.html', claims=claims)


@claims_bp.route('/received')
@login_required
def received_claims():
    owned_item_ids = [i.id for i in Item.query.filter_by(user_id=current_user.id).all()]
    claims = []
    if owned_item_ids:
        claims = (
            Claim.query
            .filter(Claim.item_id.in_(owned_item_ids))
            .order_by(Claim.created_at.desc())
            .all()
        )
    return render_template('claims/received.html', claims=claims)


@claims_bp.route('/<int:claim_id>/accept', methods=['POST'])
@login_required
def accept_claim(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    item = claim.item

    if item.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    claim.status = 'accepted'
    item.status = 'returned'
    db.session.commit()

    create_notification(
        user_id=claim.claimant_id,
        notif_type='claim_accepted',
        message=f'Congratulations! Your claim for "{item.title}" was accepted. Please arrange collection.',
        link=url_for('items.detail', item_id=item.id)
    )

    log_activity('accept_claim', f'Accepted claim #{claim.id} for item #{item.id}', user_id=current_user.id)
    flash('Claim accepted! Item has been marked as Returned.', 'success')
    return redirect(request.referrer or url_for('claims.received_claims'))


@claims_bp.route('/<int:claim_id>/reject', methods=['POST'])
@login_required
def reject_claim(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    item = claim.item

    if item.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    claim.status = 'rejected'

    # Check if there are other pending claims
    remaining_pending = Claim.query.filter_by(item_id=item.id, status='pending').count()
    if remaining_pending == 0 and item.status == 'claim_pending':
        item.status = 'active'

    db.session.commit()

    create_notification(
        user_id=claim.claimant_id,
        notif_type='claim_rejected',
        message=f'Your claim for "{item.title}" was not verified.',
        link=url_for('items.detail', item_id=item.id)
    )

    log_activity('reject_claim', f'Rejected claim #{claim.id} for item #{item.id}', user_id=current_user.id)
    flash('Claim has been rejected.', 'info')
    return redirect(request.referrer or url_for('claims.received_claims'))
