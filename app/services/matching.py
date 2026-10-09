"""
matching.py – Rule-based smart matching service for CampusFind.

Compares lost and found items using weighted heuristic scoring across
category, name, location, brand, color, date, and description fields.
"""

from difflib import SequenceMatcher
from datetime import date

from app import db
from app.models import Item, Notification


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def _ratio(a: str, b: str) -> float:
    """Return SequenceMatcher similarity ratio between two strings (case-insensitive)."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()


# ─────────────────────────────────────────────
#  CORE SCORING
# ─────────────────────────────────────────────

def calculate_match_score(item_a: Item, item_b: Item) -> dict:
    """
    Compare two Item objects and return a match assessment.

    Returns
    -------
    dict
        {
            'score':   int  (0-100),
            'factors': list[str]   (human-readable reasons for the match)
        }

    Scoring breakdown (max 100 points):
        category    25 pts
        name        20 pts
        location    20 pts  (city 12 + region 5 + country 3)
        brand       10 pts
        color       10 pts
        date        10 pts
        description  5 pts
    """
    score = 0
    factors = []

    # ── 1. Category (25 pts) ──────────────────────────────────────────────
    if item_a.category_id and item_b.category_id and item_a.category_id == item_b.category_id:
        score += 25
        factors.append('Same category')

    # ── 2. Name / Title (20 pts) ─────────────────────────────────────────
    name_ratio = _ratio(item_a.title, item_b.title)
    name_score = round(name_ratio * 20)
    if name_score > 0:
        score += name_score
        if name_ratio >= 0.8:
            factors.append('Very similar name')
        elif name_ratio >= 0.5:
            factors.append('Similar name')
        elif name_ratio >= 0.25:
            factors.append('Partially similar name')

    # ── 3. Location (20 pts: city 12 + region 5 + country 3) ─────────────
    location_score = 0
    if item_a.city_id and item_b.city_id and item_a.city_id == item_b.city_id:
        location_score += 12
        factors.append('Same city')
    if item_a.region_id and item_b.region_id and item_a.region_id == item_b.region_id:
        location_score += 5
        factors.append('Same region')
    if item_a.country_id and item_b.country_id and item_a.country_id == item_b.country_id:
        location_score += 3
        factors.append('Same country')
    score += location_score

    # ── 4. Brand (10 pts) ────────────────────────────────────────────────
    if item_a.brand and item_b.brand:
        brand_ratio = _ratio(item_a.brand, item_b.brand)
        if brand_ratio > 0.6:
            score += 10
            factors.append('Same brand')
        elif brand_ratio > 0:
            brand_score = round(brand_ratio * 10)
            score += brand_score
            if brand_score > 0:
                factors.append('Similar brand')

    # ── 5. Color (10 pts) ────────────────────────────────────────────────
    if item_a.color and item_b.color:
        color_ratio = _ratio(item_a.color, item_b.color)
        if color_ratio > 0.6:
            score += 10
            factors.append('Same color')
        elif color_ratio > 0:
            color_score = round(color_ratio * 10)
            score += color_score
            if color_score > 0:
                factors.append('Similar color')

    # ── 6. Date occurred (10 pts) ────────────────────────────────────────
    if item_a.date_occurred and item_b.date_occurred:
        diff_days = abs((item_a.date_occurred - item_b.date_occurred).days)
        if diff_days == 0:
            date_score = 10
            factors.append('Same date')
        elif diff_days <= 7:
            date_score = 8
            factors.append('Date within 1 week')
        elif diff_days <= 30:
            date_score = 5
            factors.append('Date within 1 month')
        elif diff_days <= 90:
            date_score = 2
            factors.append('Date within 3 months')
        else:
            date_score = 0
        score += date_score

    # ── 7. Description (5 pts) ───────────────────────────────────────────
    if item_a.description and item_b.description:
        desc_ratio = _ratio(item_a.description, item_b.description)
        desc_score = round(desc_ratio * 5)
        if desc_score > 0:
            score += desc_score
            factors.append('Similar description')

    # Clamp to [0, 100]
    score = max(0, min(100, score))

    return {'score': score, 'factors': factors}


# ─────────────────────────────────────────────
#  FIND MATCHES FOR AN ITEM
# ─────────────────────────────────────────────

def find_matches(item: Item, threshold: int = 40) -> list:
    """
    Find candidate matching items for *item* from the opposite item_type.

    Parameters
    ----------
    item      : Item  – the reference item (lost or found)
    threshold : int   – minimum score (0-100) to include in results

    Returns
    -------
    list of dicts sorted by score descending:
        [{'item': Item, 'score': int, 'factors': [str]}, ...]
    """
    opposite_type = 'found' if item.item_type == 'lost' else 'lost'

    candidates = (
        Item.query
        .filter(
            Item.item_type == opposite_type,
            Item.status.in_(['active', 'possible_match']),
            Item.user_id != item.user_id,
            Item.id != item.id,
        )
        .all()
    )

    results = []
    for candidate in candidates:
        assessment = calculate_match_score(item, candidate)
        if assessment['score'] >= threshold:
            results.append({
                'item': candidate,
                'score': assessment['score'],
                'factors': assessment['factors'],
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


# ─────────────────────────────────────────────
#  RUN MATCHING & NOTIFY
# ─────────────────────────────────────────────

def run_matching_for_item(item: Item, threshold: int = 40) -> list:
    """
    Run matching for *item*, create notifications for each match found,
    and update the item status to 'possible_match' if it is currently 'active'.

    Parameters
    ----------
    item      : Item  – newly posted or updated item to match against
    threshold : int   – minimum score to consider a valid match

    Returns
    -------
    list – same structure as find_matches()
    """
    matches = find_matches(item, threshold=threshold)

    if matches:
        # Update the poster's item status if it is still 'active'
        if item.status == 'active':
            item.status = 'possible_match'

        # Notify the poster of *item* about each match found
        for match in matches:
            matched_item = match['item']
            notif = Notification(
                user_id=item.user_id,
                notif_type='match_found',
                message='A possible match was found for your item!',
                link=f'/items/{matched_item.id}',
            )
            db.session.add(notif)

            # Also notify the poster of the matched item
            reverse_notif = Notification(
                user_id=matched_item.user_id,
                notif_type='match_found',
                message='A possible match was found for your item!',
                link=f'/items/{item.id}',
            )
            db.session.add(reverse_notif)

            # Update matched item status as well if still 'active'
            if matched_item.status == 'active':
                matched_item.status = 'possible_match'

        db.session.commit()

    return matches
