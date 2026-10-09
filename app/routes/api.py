"""
api.py – JSON API Blueprint for CampusFind.

Provides lightweight, unauthenticated endpoints consumed by front-end
JavaScript for cascading location dropdowns and public statistics.
"""

from flask import Blueprint, jsonify, request

from app.models import (
    LocationRegion,
    LocationCity,
    LocationArea,
    Item,
    User,
)
from app import db

api_bp = Blueprint('api', __name__)


# ─────────────────────────────────────────────
#  LOCATION CASCADES
# ─────────────────────────────────────────────

@api_bp.route('/countries')
def get_countries():
    """Return all countries in the system.
    Response JSON: [{id, name, code}, ...]
    """
    from app.models import LocationCountry
    countries = LocationCountry.query.order_by(LocationCountry.name).all()
    return jsonify([{'id': c.id, 'name': c.name, 'code': c.code} for c in countries])


@api_bp.route('/regions/<int:country_id>')
def get_regions(country_id):
    """Return all regions belonging to the given country.

    Response JSON: [{id, name}, ...]
    """
    regions = (
        LocationRegion.query
        .filter_by(country_id=country_id)
        .order_by(LocationRegion.name)
        .all()
    )
    return jsonify([{'id': r.id, 'name': r.name} for r in regions])


@api_bp.route('/cities/<int:region_id>')
def get_cities(region_id):
    """Return all cities belonging to the given region.

    Response JSON: [{id, name}, ...]
    """
    cities = (
        LocationCity.query
        .filter_by(region_id=region_id)
        .order_by(LocationCity.name)
        .all()
    )
    return jsonify([{'id': c.id, 'name': c.name} for c in cities])


@api_bp.route('/areas/<int:city_id>')
def get_areas(city_id):
    """Return all areas belonging to the given city.

    Response JSON: [{id, name}, ...]
    """
    areas = (
        LocationArea.query
        .filter_by(city_id=city_id)
        .order_by(LocationArea.name)
        .all()
    )
    return jsonify([{'id': a.id, 'name': a.name} for a in areas])


# ─────────────────────────────────────────────
#  LOCATION SEARCH (TYPEAHEAD)
# ─────────────────────────────────────────────

@api_bp.route('/location-search')
def location_search():
    """Search cities by name (case-insensitive substring match).

    Query param: q  (search string)

    Response JSON (top 10):
        [{id, name, region, country}, ...]
    """
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    cities = (
        LocationCity.query
        .filter(LocationCity.name.ilike(f'%{query}%'))
        .limit(10)
        .all()
    )

    results = []
    for city in cities:
        results.append({
            'id': city.id,
            'name': city.name,
            'region': city.region.name if city.region else None,
            'country': city.region.country.name if city.region and city.region.country else None,
        })

    return jsonify(results)


# ─────────────────────────────────────────────
#  PUBLIC STATISTICS
# ─────────────────────────────────────────────

@api_bp.route('/stats')
def stats():
    """Return high-level public statistics about the platform.

    Response JSON:
        {
            total_lost:     int,
            total_found:    int,
            total_resolved: int,
            total_users:    int
        }
    """
    total_lost = Item.query.filter_by(item_type='lost').count()
    total_found = Item.query.filter_by(item_type='found').count()
    total_resolved = Item.query.filter(
        Item.status.in_(['resolved', 'returned'])
    ).count()
    total_users = User.query.filter_by(is_active=True).count()

    return jsonify({
        'total_lost': total_lost,
        'total_found': total_found,
        'total_resolved': total_resolved,
        'total_users': total_users,
    })
