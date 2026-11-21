# FR 4 Accept a Delivery
from datetime import timedelta

import pytest
from conftest import delivery_data, make_rider
from services.order_service import OrderService
from services.order_status_service import OrderStatusService
from services.request_rider import RequestRider


def offered_delivery(cashier, chef, item):
    order = OrderService.create_order(delivery_data(item.id), cashier)
    OrderStatusService.change_status(order.id, 'Preparing', chef)
    return order.delivery


def test_fr4_ac3_ts1_only_first_rider_gets_the_delivery(cashier, chef, patty, rider_a, rider_b):
    delivery = offered_delivery(cashier, chef, patty)
    RequestRider.accept_delivery(delivery.id, rider_a)
    with pytest.raises(ValueError, match='already been taken'):
        RequestRider.accept_delivery(delivery.id, rider_b)
    assert delivery.rider_id == rider_a.id
    assert rider_a.status == 'reserved' and rider_b.status == 'available'


def test_fr4_ac4_rider_gets_12_minutes_to_pick_up(cashier, chef, patty, rider_a):
    delivery = offered_delivery(cashier, chef, patty)
    RequestRider.accept_delivery(delivery.id, rider_a)
    assert delivery.pickup_deadline - delivery.accepted_at == timedelta(minutes=12)


def test_fr4_ac1_ts2_unavailable_rider_cannot_accept(app, cashier, chef, patty):
    off_shift = make_rider('Shanice', status='unavailable')
    delivery = offered_delivery(cashier, chef, patty)
    with pytest.raises(ValueError):
        RequestRider.accept_delivery(delivery.id, off_shift)


def test_fr4_ac5_ts2_owner_reassigns_delivery(cashier, chef, patty, rider_a, rider_b):
    delivery = offered_delivery(cashier, chef, patty)
    RequestRider.accept_delivery(delivery.id, rider_a)
    RequestRider.assign_manually(delivery.id, rider_b.id)
    assert delivery.rider_id == rider_b.id
    assert rider_b.status == 'reserved' and rider_a.status == 'available'


def test_fr4_rider_on_delivery_cannot_go_off_shift(cashier, chef, patty, rider_a):
    delivery = offered_delivery(cashier, chef, patty)
    RequestRider.accept_delivery(delivery.id, rider_a)
    with pytest.raises(ValueError):
        RequestRider.set_rider_status(rider_a.id, 'unavailable')
