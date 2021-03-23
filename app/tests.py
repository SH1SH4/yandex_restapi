from data import db_session
from datetime import datetime, timedelta
import pytest
import os
from modules.globals import TIME_FORMAT
from json import dumps
from app import app


# creating db
try:
    os.remove('test.db')
except:
    pass
db_session.global_init('db/test.db')


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Tests post couriers
def test_post_courier(client):
    js = dumps({
        "data":
            [{
                "courier_id": 0,
                "regions": [1],
                "courier_type": 'foot',
                "working_hours": ["12:00-18:00"]
            }]
    })
    rv = client.post('/couriers', data=js)
    assert rv.status_code == 201
    assert rv.data == b'{"couriers": [{"id": 0}]}'


def test_post_courier_id_already_in_db(client):
    js = dumps({
        "data":
            [{
                "courier_id": 0,
                "regions": [1],
                "courier_type": 'foot',
                "working_hours": ["12:00-18:00"]
            }]
    })
    rv = client.post('/couriers', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {"validation_error":
        {"couriers": [
            {"id": 0,
             "error_description":
                 "id0 is already in the database"}
        ]
        }
    }


def test_post_courier_id_error(client):
    js = dumps({
        "data":
            [{
                "courier_id": 0.1,
                "regions": [1],
                "courier_type": 'foot',
                "working_hours": ["12:00-18:00"]
            }]
    })
    rv = client.post('/couriers', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {"validation_error": {"couriers": [
        {"id": 0.1,
         "error_description": "Invalid id 0.1, id must be an integer"}
    ]
    }
    }


def test_post_courier_region_error(client):
    js = dumps({
        "data":
            [{
                "courier_id": 1,
                "regions": 1,
                "courier_type": "foot",
                "working_hours": ["12:00-18:00"]
            }]
    })
    rv = client.post('/couriers', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {"validation_error": {"couriers": [
        {"id": 1, "error_description": "Regions must be list type"}]}}

    js = dumps({
        "data":
            [{
                "courier_id": 1,
                "regions": [22, 1.5],
                "courier_type": 'foot',
                "working_hours": ["12:00-18:00"]
            }]
    })
    rv = client.post('/couriers', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {"validation_error": {"couriers": [
        {"id": 1,
         "error_description":
             "Invalid region 1.5, region must be an integer"}]}}


def test_post_courier_type_error(client):
    js = dumps({
        "data":
            [{
                "courier_id": 2,
                "regions": [1],
                "courier_type": 'helicopter',
                "working_hours": ["12:00-18:00"]
            }]
    })
    rv = client.post('/couriers', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {"validation_error": {
        "couriers": [{"id": 2, "error_description": "Invalid courier type"}]}}


def test_post_courier_time_error(client):
    js = dumps({
        "data":
            [{
                "courier_id": 3,
                "regions": [1],
                "courier_type": 'foot',
                "working_hours": ["morning-18:00"]
            }]
    })
    rv = client.post('/couriers', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error':
        {'couriers': [
            {'id': 3,
             'error_description':
                 "time data 'morning' does not match format '%H:%M'"}]}}

    js = dumps({
        "data":
            [{
                "courier_id": 3,
                "regions": [1],
                "courier_type": 'foot',
                "working_hours": ["22:00-18:00"]
            }]
    })
    rv = client.post('/couriers', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {"validation_error":
        {"couriers": [
            {"id": 3,
             "error_description": "End of work before start"}]}}

    js = dumps({
        "data":
            [{
                "courier_id": 3,
                "regions": [1],
                "courier_type": 'foot',
                "working_hours": "09:00-18:00"
            }]
    })
    rv = client.post('/couriers', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error':
        {'couriers': [
            {'error_description': 'Working_hours must be list',
             'id': 3}]}}


def test_post_courier_invalid_json(client):
    js = dumps({
        "not_data":
            [{
                "courier_id": 3,
                "regions": [1],
                "courier_type": 'foot',
                "working_hours": ["morning-18:00"]
            }]
    })
    rv = client.post('/couriers', data=js)
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description':
                                 'Invalid data format'}

    js = dumps({
        "data":
            [{
                "extra_key": "error",
                "courier_id": 3,
                "regions": [1],
                "courier_type": 'foot',
                "working_hours": ["08:00-18:00"]
            }]
    })
    rv = client.post('/couriers', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {
        "error_description":
            "'extra_key' is an invalid keyword argument for Courier"
    }

    js = dumps('Invalid Json')
    rv = client.post('/couriers', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description': 'Invalid JSON'}


# Tests patch couriers/<id>
def test_patch_courier(client):
    js = dumps({
        "courier_type": "car",
        "working_hours": ["08:00-22:00"]
    })
    rv = client.patch('/couriers/0', data=js)
    assert rv.status_code == 201
    assert rv.get_json() == {'courier_id': 0,
                             'courier_type': 'car',
                             'regions': [1],
                             'working_hours': ['08:00-22:00']}


def test_patch_courier_unknown_key(client):
    js = dumps({
        "key": "car",
        "working_hours": ["08:00-22:00"]
    })
    rv = client.patch('/couriers/0', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description': 'Unknown key in data'}


def test_patch_courier_empty_data(client):
    js = dumps({})
    rv = client.patch('/couriers/0', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description': 'Invalid JSON'}


def test_patch_courier_unknown_courier(client):
    js = dumps({
        "courier_type": "car",
        "working_hours": ["08:00-22:00"]
    })
    rv = client.patch('/couriers/101', data=js)
    assert rv.status_code == 404


def test_patch_string_courier_id(client):
    js = dumps({
        "key": "car",
        "working_hours": ["08:00-22:00"]
    })
    rv = client.patch('/couriers/courier', data=js)
    assert rv.status_code == 404


def test_patch_invalid_value(client):
    js = dumps({
        "key": "tank"
    })
    rv = client.patch('/couriers/0', data=js)
    print(rv.data)
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description': 'Unknown key in data'}


#  Tests post /orders
def test_post_orders(client):
    js = dumps({"data": [
        {
            "order_id": 0,
            "weight": 0.23,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        }]})
    rv = client.post('/orders', data=js)
    print(rv.data)
    assert rv.status_code == 201


def test_post_orders_invalid_id(client):
    id = 1.5
    js = {"data": [
        {
            "order_id": id,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        }]}
    rv = client.post('/orders', data=dumps(js))
    print(rv.data)
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error':
        {'orders': [
                    {'error_description':
                        'Invalid id 1.5, id must be an integer',
                     'id': 1.5}]}}

    js['data'][0]['order_id'] = -1
    rv = client.post('/orders', data=dumps(js))
    print(rv.data)
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error':
        {'orders': [
                    {'error_description':
                        'Invalid id -1, id must be an integer',
                     'id': -1}]}}


def test_post_orders_id_already_in_db(client):
    js = dumps({"data": [
        {
            "order_id": 0,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        }]})
    rv = client.post('/orders', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error': {'orders':
        [{'error_description': 'id0 is already in the database', 'id': 0}]}}


def test_post_orders_bad_weight(client):
    js = dumps({"data": [
        {
            "order_id": 1,
            "weight": -100,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        }]})
    rv = client.post('/orders', data=js)
    print(rv.data)
    assert rv.status_code == 400
    assert rv.get_json() == {"validation_error": {"orders": [
                                {"id": 1,
                                 "error_description":
                                    "Allowed weight from 0.01 kg to 50kg"}]}}

    js = dumps({"data": [
        {
            "order_id": 1,
            "weight": 500,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        }]})
    rv = client.post('/orders', data=js)
    print(rv.data)
    assert rv.status_code == 400
    assert rv.get_json() == {"validation_error": {"orders": [
                                {"id": 1,
                                 "error_description":
                                    "Allowed weight from 0.01 kg to 50kg"}]}}


def test_post_orders_bad_region(client):
    js = dumps({"data": [
        {
            "order_id": 2,
            "weight": 25,
            "region": -12,
            "delivery_hours": ["09:00-18:00"]
        }]})
    rv = client.post('/orders', data=js)
    print(rv.data)
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error':
        {'orders':
             [{'id': 2,
               'error_description':
                 'Invalid region -12, region must be an integer'}]}}


def test_post_orders_string_in_time(client):
    js = dumps({"data": [
        {
            "order_id": 2,
            "weight": 25,
            "region": 12,
            "delivery_hours": ["morning-18:00"]
        }]})
    rv = client.post('/orders', data=js)
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error':
        {'orders': [{
            'id': 2,
            'error_description':
                "time data 'morning' does not match format '%H:%M'"}
                   ]
        }
    }


def test_post_orders_bad_time(client):
    js = dumps({"data": [
        {
            "order_id": 2,
            "weight": 25,
            "region": 12,
            "delivery_hours": ["18:00-9:00"]
        }]})
    rv = client.post('/orders', data=js)
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error':
        {'orders': [{
            'id': 2,
            'error_description':
                'Incorrect time format'}
        ]
        }
    }


# Tests post /orders/assign
def test_orders_assign(client):
    js = dumps({'courier_id': 0})
    rv = client.post('/orders/assign', data=js)
    assert rv.status_code == 200
    collected_id = rv.get_json()['orders'][0]['id']
    assert collected_id == 0


def test_orders_assign_empty_data(client):
    js = dumps({})
    rv = client.post('/orders/assign', data=js)
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description': 'Invalid JSON'}


def test_orders_assign_invalid_data(client):
    js = dumps({'focus': 'json crashed'})
    rv = client.post('/orders/assign', data=js)
    assert rv.status_code == 400


def test_orders_assign_invalid_courier(client):
    js = dumps({'courier_id': 'invalid'})
    rv = client.post('/orders/assign', data=js)
    assert rv.status_code == 400


# Tests post /orders/complete
def test_orders_complete(client):
    time = datetime.now() + timedelta(minutes=30)
    js = dumps({
        "courier_id": 0,
        "order_id": 0,
        "complete_time": time.strftime(TIME_FORMAT)
    })
    rv = client.post('/orders/complete', data=js)
    assert rv.status_code == 200
    assert rv.get_json() == {'order_id': 0}


def test_orders_complete_invalid_courier(client):
    time = datetime.now() + timedelta(minutes=30)
    js = dumps({
        "courier_id": 5,
        "order_id": 0,
        "complete_time": time.strftime(TIME_FORMAT)
    })
    rv = client.post('/orders/complete', data=js)
    assert rv.status_code == 400


def test_orders_complete_invalid_order(client):
    time = datetime.now() + timedelta(minutes=30)
    js = dumps({
        "courier_id": 0,
        "order_id": 5,
        "complete_time": time.strftime(TIME_FORMAT)
    })
    rv = client.post('/orders/complete', data=js)
    assert rv.status_code == 400


def test_orders_complete_invalid_time(client):
    js = dumps({
        "courier_id": 0,
        "order_id": 0,
        "complete_time": 'вчера'
    })
    rv = client.post('/orders/complete', data=js)
    assert rv.status_code == 400

    js = dumps({
        "courier_id": 0,
        "order_id": 0,
        "complete_time": '10:30'
    })
    rv = client.post('/orders/complete', data=js)
    assert rv.status_code == 400


# couriers/<int>
def test_courier_info(client):
    rv = client.get('/couriers/0')
    assert rv.status_code == 200
    assert rv.get_json() == {
        'courier_id': 0,
        'courier_type': 'car',
        'regions': [1],
        'working_hours': ['08:00-22:00'],
        'earnings': 4500,
        'rating': 2.5
    }


def test_courier_info_string_id(client):
    rv = client.get('/couriers/bababoi')
    assert rv.status_code == 404


def test_courier_info_invalid_id(client):
    rv = client.get('/couriers/5')
    assert rv.status_code == 404



