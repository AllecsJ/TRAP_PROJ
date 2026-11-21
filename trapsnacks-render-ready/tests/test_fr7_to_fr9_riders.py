# FR 7 Add a Rider, FR 8 Edit a Rider, FR 9 Remove a Rider
import pytest
from conftest import delivery_data
from models import User
from services.edit_rider_service import EditRiderService
from services.new_rider_service import NewRiderService
from services.order_service import OrderService
from services.order_status_service import OrderStatusService
from services.remove_rider_service import RemoveRiderService
from services.request_rider import RequestRider

GOOD = {'name': 'Damion Clarke', 'phone': '876-555-0104', 'address': '22 Red Hills Road',
        'trn': '456-789-123', 'email': 'damion@example.com', 'username': 'damion', 'password': 'secret1'}


def test_fr7_missing_field_is_named(app):
    data = dict(GOOD, trn='')
    with pytest.raises(ValueError, match='TRN'):
        NewRiderService.add_rider(data)


def test_fr7_complete_form_saves_rider_with_id_and_login(app):
    rider = NewRiderService.add_rider(GOOD)
    assert rider.id is not None
    assert User.query.filter_by(username='damion', rider_id=rider.id).first() is not None


def test_fr8_edit_saves_changes_and_checks_fields(app):
    rider = NewRiderService.add_rider(GOOD)
    EditRiderService.edit_rider(rider.id, dict(GOOD, phone='876-555-7777'))
    assert rider.phone == '876-555-7777'
    with pytest.raises(ValueError, match='Name'):
        EditRiderService.edit_rider(rider.id, dict(GOOD, name=''))


def test_fr9_rider_with_active_delivery_cannot_be_removed(cashier, chef, patty, rider_a):
    order = OrderService.create_order(delivery_data(patty.id), cashier)
    OrderStatusService.change_status(order.id, 'Preparing', chef)
    RequestRider.accept_delivery(order.delivery.id, rider_a)
    with pytest.raises(ValueError, match='active delivery'):
        RemoveRiderService.remove_rider(rider_a.id)


def test_fr9_removed_rider_is_hidden_and_cannot_log_in(rider_a):
    RemoveRiderService.remove_rider(rider_a.id)
    assert rider_a.removed is True
    assert User.query.filter_by(rider_id=rider_a.id).first() is None
