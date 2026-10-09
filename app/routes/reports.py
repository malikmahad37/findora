from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

from app import db
from app.models import Item, Report

reports_bp = Blueprint("reports", __name__)


# ── Form ──────────────────────────────────────────────────────────────────────

class ReportForm(FlaskForm):
    reason = SelectField(
        "Reason",
        choices=[
            ("fake_post",     "Fake Post"),
            ("wrong_info",    "Wrong Information"),
            ("spam",          "Spam"),
            ("inappropriate", "Inappropriate Content"),
            ("suspicious",    "Suspicious Activity"),
            ("other",         "Other"),
        ],
        validators=[DataRequired()],
    )
    details = TextAreaField("Additional Details", validators=[Optional()])
    submit = SubmitField("Submit Report")


# ── Routes ────────────────────────────────────────────────────────────────────

@reports_bp.route("/submit/<int:item_id>", methods=["GET", "POST"])
@login_required
def submit_report(item_id):
    """Allow a user to report a lost/found item post."""
    item = Item.query.get_or_404(item_id)

    # Cannot report own item
    if item.user_id == current_user.id:
        flash("You cannot report your own post.", "warning")
        return redirect(url_for("items.detail", item_id=item.id))

    # Cannot report the same item twice
    existing = Report.query.filter_by(
        reporter_id=current_user.id, item_id=item.id
    ).first()
    if existing:
        flash("You have already submitted a report for this post.", "warning")
        return redirect(url_for("items.detail", item_id=item.id))

    form = ReportForm()
    if form.validate_on_submit():
        report = Report(
            reporter_id=current_user.id,
            item_id=item.id,
            reason=form.reason.data,
            details=form.details.data or None,
            status="pending",
        )
        db.session.add(report)
        db.session.commit()
        flash(
            "Your report has been submitted. Our team will review it shortly.",
            "success",
        )
        return redirect(url_for("items.detail", item_id=item.id))

    return render_template("reports/submit.html", form=form, item=item)
