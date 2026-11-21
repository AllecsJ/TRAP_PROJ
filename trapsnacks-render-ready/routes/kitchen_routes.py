# routes/kitchen_routes.py
# KitchenRoutes - FR 6 Item Availability (and shows the kitchen screen used by FR 1).

from flask import Blueprint, render_template, request
from routes.auth_routes import roles_required, run_service
from services.kitchen_service import KitchenService

kitchen_routes = Blueprint('kitchen_routes', __name__)


@kitchen_routes.get('/kitchen')
@roles_required('chef', 'owner')
def kitchen_page():
    return render_template('kitchen.html')


@kitchen_routes.post('/api/menu/<int:item_id>/availability')
@roles_required('chef', 'owner')
def set_availability(item_id):
    available = bool((request.get_json(silent=True) or {}).get('available'))
    return run_service(lambda: KitchenService.set_availability(item_id, available).to_dict())
