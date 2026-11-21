# Integration tests: pages, role checks (Security 2) and live updates (Socket.IO)
from conftest import delivery_data, login
from extensions import socketio


def test_login_redirects_each_role_to_its_page(client, cashier):
    response = login(client, 'cashier')
    assert response.status_code == 302 and response.headers['Location'].endswith('/cashier')


def test_rider_cannot_open_owner_pages(client, rider_a):
    login(client, 'andre')
    assert client.get('/riders').status_code == 403


def test_every_page_loads_for_its_role(client, owner, patty):
    login(client, 'owner')
    for url in ['/cashier', '/kitchen', '/deliveries', '/riders', '/riders/new']:
        assert client.get(url).status_code == 200, url


def test_cashier_creates_order_through_the_api(client, cashier, patty):
    login(client, 'cashier')
    response = client.post('/api/orders', json=delivery_data(patty.id))
    assert response.status_code == 201 and response.get_json()['ok'] is True
    bad = client.post('/api/orders', json={'order_type': 'pickup', 'items': []})
    assert bad.status_code == 400 and 'at least one item' in bad.get_json()['error']


def test_kitchen_receives_new_order_live(app, client, cashier, chef, patty):
    chef_client = app.test_client()
    login(chef_client, 'chef')
    chef_socket = socketio.test_client(app, flask_test_client=chef_client)
    login(client, 'cashier')
    client.post('/api/orders', json=delivery_data(patty.id))
    events = [e['name'] for e in chef_socket.get_received()]
    assert 'order_created' in events


def test_offer_reaches_available_rider_live(app, client, cashier, chef, patty, rider_a):
    rider_client = app.test_client()
    login(rider_client, 'andre')
    rider_socket = socketio.test_client(app, flask_test_client=rider_client)
    login(client, 'cashier')
    order_id = client.post('/api/orders', json=delivery_data(patty.id)).get_json()['data']['id']
    chef_client = app.test_client()
    login(chef_client, 'chef')
    chef_client.post(f'/api/orders/{order_id}/status', json={'status': 'Preparing'})
    events = [e['name'] for e in rider_socket.get_received()]
    assert 'delivery_offer' in events
