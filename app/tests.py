from data import db_session
from datetime import datetime, timedelta
import pytest
import os
from json import dumps
from app import app

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
# creating db
try:
    os.remove('db/test.db')
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
    js = {
        "data":
            [{
                "courier_id": 0,
                "regions": [1, 100],
                "courier_type": "foot",
                "working_hours": ["12:00-18:00"]
            }]
    }
    rv = client.post('/couriers', data=dumps(js))
    print(rv.get_json())
    print(rv)
    print(rv.status_code)
    assert rv.status_code == 201
    assert rv.data == b'{"couriers": [{"id": 0}]}'


def test_post_courier_id_already_in_db(client):
    js = dumps({
        "data":
            [{
                "courier_id": 0,
                "regions": [1],
                "courier_type": "foot",
                "working_hours": ["12:00-18:00"]
            }]
    })
    rv = client.post('/couriers', data=js)
    print(rv.get_json())
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
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error':
                                 {'couriers':
                                      [{'id': 0.1,
                                        'error_description':
                                            "0.1 is not of type 'integer'"}]}}


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
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error':
        {'couriers': [
            {'id': 1,
             'error_description':
                 "1 is not of type 'array'"}]}}

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
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error': {
        'couriers': [
            {'id': 1,
             'error_description':
                 "1.5 is not of type 'integer'"}]}}


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
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error': {
        'couriers': [
            {'id': 2,
             'error_description':
                 "'helicopter' is not one of ['foot', 'car', 'bike']"}]}}


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
    print(rv.get_json())
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
    print(rv.get_json())
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
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error': {
        'couriers': [
            {'id': 3,
             'error_description':
                 "'09:00-18:00' is not of type 'array'"}]}}


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
    assert rv.get_json() == {'error_description': 'Invalid JSON'}


def test_post_courier_extra_key_json(client):
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
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error': {
        'couriers': [
            {'id': 3,
             'error_description':
                 "Additional properties are not allowed ('extra_key' was unexpected)"}]}}


def test_post_courier_json_not_dict(client):
    js = dumps('Invalid Json')
    rv = client.post('/couriers', data=js)
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description': 'Invalid JSON'}


# Tests patch couriers/<id>
def test_patch_courier(client):
    js = dumps({
        "courier_type": "car",
        "working_hours": ["08:00-22:00"]
    })
    rv = client.patch('/couriers/0', data=js)
    print(rv.get_json())
    assert rv.status_code == 201
    assert rv.get_json() == {'courier_id': 0,
                             'courier_type': 'car',
                             'regions': [1, 100],
                             'working_hours': ['08:00-22:00']}


def test_patch_courier_unknown_key(client):
    js = dumps({
        "key": "car",
        "working_hours": ["08:00-22:00"]
    })
    rv = client.patch('/couriers/0', data=js)
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description':
                                 "Additional properties are not allowed ('key' was unexpected)"}


def test_patch_courier_empty_data(client):
    js = dumps({})
    rv = client.patch('/couriers/0', data=js)
    print(rv.get_json())
    assert rv.status_code == 201
    assert rv.get_json() == {'courier_id': 0,
                             'courier_type': 'car',
                             'regions': [1, 100],
                             'working_hours': ['08:00-22:00']
                             }


def test_patch_courier_unknown_courier(client):
    js = dumps({
        "courier_type": "car",
        "working_hours": ["08:00-22:00"]
    })
    rv = client.patch('/couriers/101', data=js)
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description': 'Invalid courier_id'}


def test_patch_string_courier_id(client):
    js = dumps({
        "key": "car",
        "working_hours": ["08:00-22:00"]
    })
    rv = client.patch('/couriers/courier', data=js)
    print(rv.get_json())
    assert rv.status_code == 404


def test_patch_invalid_value(client):
    js = dumps({
        "key": "tank"
    })
    rv = client.patch('/couriers/0', data=js)
    print(rv.data)
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description':
                                 "Additional properties are not allowed ('key' was unexpected)"}


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
    print(rv.get_json())
    assert rv.status_code == 201


def test_post_orders_invalid_id(client):
    js = {"data": [
        {
            "order_id": 1.5,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        }]}
    rv = client.post('/orders', data=dumps(js))
    print(rv.data)
    assert rv.status_code == 400
    assert rv.get_json() == {"error_description":
                                 "1.5 is not of type 'integer'"}

    js['data'][0]['order_id'] = -1
    rv = client.post('/orders', data=dumps(js))
    print(rv.data)
    assert rv.status_code == 400
    assert rv.get_json() == {"error_description":
                                 "-1 is less than the minimum of 0"}


def test_post_orders_id_already_in_db(client):
    js = dumps({"data": [
        {
            "order_id": 0,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        }]})
    rv = client.post('/orders', data=js)
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'validation_error':
        {'orders': [{
            'id': 0,
            'error_description':
                'id0 is already in the database'}]}}


def test_post_orders_bad_weight(client):
    js = dumps({"data": [
        {
            "order_id": 1,
            "weight": -100,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        }]})
    rv = client.post('/orders', data=js)
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description':
                                 '-100 is less than the minimum of 0.01'}

    js = dumps({"data": [
        {
            "order_id": 1,
            "weight": 500,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        }]})
    rv = client.post('/orders', data=js)
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description':
                                 '500 is greater than the maximum of 50'}


def test_post_orders_bad_region(client):
    js = dumps({"data": [
        {
            "order_id": 2,
            "weight": 25,
            "region": -12,
            "delivery_hours": ["09:00-18:00"]
        }]})
    rv = client.post('/orders', data=js)
    print(rv.get_json())
    assert rv.status_code == 400
    assert rv.get_json() == {'error_description':
                                 '-12 is less than the minimum of 0'}


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
    print(rv.get_json())
    assert rv.status_code == 200
    collected_id = rv.get_json()['orders'][0]['id']
    assert collected_id == 0


def test_orders_assign_empty_data(client):
    js = dumps({})
    rv = client.post('/orders/assign', data=js)
    print(rv.get_json())
    assert rv.status_code == 400


def test_orders_assign_invalid_data(client):
    js = dumps({'focus': 'json crashed'})
    rv = client.post('/orders/assign', data=js)
    print(rv.get_json())
    assert rv.status_code == 400


def test_orders_assign_invalid_courier(client):
    js = dumps({'courier_id': 'invalid'})
    rv = client.post('/orders/assign', data=js)
    print(rv.get_json())
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
    print(rv.get_json())
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
    print(rv.get_json())
    assert rv.status_code == 400


def test_orders_complete_invalid_order(client):
    time = datetime.now() + timedelta(minutes=30)
    js = dumps({
        "courier_id": 0,
        "order_id": 5,
        "complete_time": time.strftime(TIME_FORMAT)
    })
    rv = client.post('/orders/complete', data=js)
    print(rv.get_json())
    assert rv.status_code == 400


def test_orders_complete_invalid_time(client):
    js = dumps({
        "courier_id": 0,
        "order_id": 0,
        "complete_time": 'вчера'
    })
    rv = client.post('/orders/complete', data=js)
    print(rv.get_json())
    assert rv.status_code == 400

    js = dumps({
        "courier_id": 0,
        "order_id": 0,
        "complete_time": '10:30'
    })
    rv = client.post('/orders/complete', data=js)
    print(rv.get_json())
    assert rv.status_code == 400


# couriers/<int>
def test_courier_info(client):
    rv = client.get('/couriers/0')
    assert rv.status_code == 200
    assert rv.get_json() == {
        'courier_id': 0,
        'courier_type': 'car',
        'regions': [1, 100],
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


# Полный тест основных функций

# Добавляем курьеров
def test_full_post_couriers(client):
    rv = client.post("/couriers", data=dumps({
        "data": [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [5, 6],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 2,
                "courier_type": "foot",
                "regions": [4, 8, 3],
                "working_hours": ["07:00-10:00"]
            },
            {
                "courier_id": 3,
                "courier_type": "foot",
                "regions": [1, 5],
                "working_hours": ["14:00-16:35", "16:50-18:00"]
            },
            {
                "courier_id": 4,
                "courier_type": "foot",
                "regions": [7],
                "working_hours": ["14:00-16:35", "16:50-18:00"]
            }
        ]
    }))
    assert rv.status_code == 201


# Добавляем заказы
def test_full_post_orders(client):
    rv = client.post("/orders", data=dumps({
        "data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 5,
                "delivery_hours": ["08:00-10:00"]
            },
            {
                "order_id": 2,
                "weight": 15,
                "region": 5,
                "delivery_hours": ["14:00-18:00"]
            },
            {
                "order_id": 3,
                "weight": 0.01,
                "region": 4,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            },
            {
                "order_id": 4,
                "weight": 0.23,
                "region": 6,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 5,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 6,
                "weight": 0.01,
                "region": 5,
                "delivery_hours": ["16:00-21:30"]
            },
            {
                "order_id": 7,
                "weight": 0.23,
                "region": 5,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 8,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 9,
                "weight": 0.01,
                "region": 4,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            },
            {
                "order_id": 10,
                "weight": 15,
                "region": 2,
                "delivery_hours": ["08:00-10:00"]
            }
        ]
    }))

    assert rv.status_code == 201


# Принимаем заказы
def test_full_orders_assign(client):
    rv = client.post('/orders/assign', data=dumps({"courier_id": 1}))
    assert rv.status_code == 200
    assert rv.get_json()['orders'] == [
        {'id': 1}, {'id': 2}, {'id': 4}, {'id': 7}
    ]

    rv = client.post('/orders/assign', data=dumps({"courier_id": 2}))
    assert rv.status_code == 200
    assert rv.get_json()['orders'] == [
        {'id': 3}, {'id': 9}
    ]

    rv = client.post('/orders/assign', data=dumps({"courier_id": 3}))
    assert rv.status_code == 200
    assert rv.get_json()['orders'] == [
        {'id': 5}, {'id': 6}, {'id': 8}
    ]

    rv = client.post('/orders/assign', data=dumps({"courier_id": 4}))
    assert rv.status_code == 200
    assert rv.get_json()['orders'] == []


# Выполнение заказов 1ого курьера
def test_full_courier1_complete_orders(client):
    rv = client.post('orders/complete', data=dumps(
        {
            "courier_id": 1,
            "order_id": 1,
            "complete_time": (
                    datetime.now() + timedelta(minutes=30)
            ).strftime(TIME_FORMAT)
        }))
    assert rv.status_code == 200
    assert rv.get_json() == {"order_id": 1}

    rv = client.post('orders/complete', data=dumps({
        "courier_id": 1,
        "order_id": 2,
        "complete_time": (
                datetime.now() + timedelta(minutes=50)
        ).strftime(TIME_FORMAT)
    }))
    assert rv.status_code == 200
    assert rv.get_json() == {"order_id": 2}

    rv = client.post('orders/complete', data=dumps({
        "courier_id": 1,
        "order_id": 4,
        "complete_time": (
                datetime.now() + timedelta(minutes=25)
        ).strftime(TIME_FORMAT)
    }))
    assert rv.status_code == 200
    assert rv.get_json() == {"order_id": 4}

    rv = client.post('orders/complete', data=dumps({
        "courier_id": 1,
        "order_id": 7,
        "complete_time": (
                datetime.now() + timedelta(minutes=7)
        ).strftime(TIME_FORMAT)
    }))
    assert rv.status_code == 200
    assert rv.get_json() == {"order_id": 7}


# Выполнение заказов 2ого курьера
def test_full_courier2_complete_orders(client):
    rv = client.post('orders/complete', data=dumps(
        {
            "courier_id": 2,
            "order_id": 3,
            "complete_time": (
                    datetime.now() + timedelta(minutes=15)
            ).strftime(TIME_FORMAT)
        }))
    assert rv.status_code == 200
    assert rv.get_json() == {"order_id": 3}

    rv = client.post('orders/complete', data=dumps({
        "courier_id": 2,
        "order_id": 9,
        "complete_time": (
                datetime.now() + timedelta(minutes=25)
        ).strftime(TIME_FORMAT)
    }))
    assert rv.status_code == 200
    assert rv.get_json() == {"order_id": 9}


# Выполнение заказов 3го курьера
def test_full_courier3_complete_orders(client):
    rv = client.post('orders/complete', data=dumps(
        {
            "courier_id": 3,
            "order_id": 5,
            "complete_time": (
                    datetime.now() + timedelta(minutes=30)
            ).strftime(TIME_FORMAT)
        }))
    print(rv.get_json)
    assert rv.status_code == 200
    assert rv.get_json() == {"order_id": 5}

    rv = client.post('orders/complete', data=dumps({
        "courier_id": 3,
        "order_id": 6,
        "complete_time": (
                datetime.now() + timedelta(minutes=50)
        ).strftime(TIME_FORMAT)
    }))
    assert rv.status_code == 200
    print(rv.get_json())
    assert rv.get_json() == {"order_id": 6}

    # Проверяем убрались ли 2 верхних заказа из активных
    rv = client.post('orders/assign', data=dumps({'courier_id': 3}))
    assert rv.get_json()['orders'][0]['id'] == 8
    assert len(rv.get_json()['orders']) == 1

    rv = client.post('orders/complete', data=dumps({
        "courier_id": 3,
        "order_id": 8,
        "complete_time": (
                datetime.now() + timedelta(minutes=25)
        ).strftime(TIME_FORMAT)
    }))
    assert rv.status_code == 200
    assert rv.get_json() == {"order_id": 8}


# Получение информации 1ого курьера
def test_full_get_courier1_info(client):
    rv = client.get('couriers/1')
    assert rv.get_json() == {
        'courier_id': 1,
        'courier_type': 'foot',
        'regions': [5, 6],
        'working_hours': ['11:35-14:05', '09:00-11:00'],
        'earnings': 4000,
        'rating': 3.61
    }


# Получение информации 2ого курьера
def test_full_get_courier2_info(client):
    rv = client.get('couriers/2')
    assert rv.get_json() == {
        'courier_id': 2,
        'courier_type': 'foot',
        'regions': [4, 8, 3],
        'working_hours': ['07:00-10:00'],
        'earnings': 2000,
        'rating': 3.96
    }


# Получение информации 3ого курьера
def test_full_get_courier3_info(client):
    rv = client.get('couriers/3')
    assert rv.get_json() == {
        'courier_id': 3,
        'courier_type': 'foot',
        'regions': [1, 5],
        'working_hours': ['14:00-16:35', '16:50-18:00'],
        'earnings': 3000,
        'rating': 3.75
    }


# Получение информации 4ого курьера
def test_full_get_courier4_info(client):
    rv = client.get('couriers/4')
    print(rv.get_json())
    assert rv.get_json() == {
        'courier_id': 4,
        'courier_type': 'foot',
        'regions': [7],
        'working_hours': ['14:00-16:35', '16:50-18:00'],
        'earnings': 0
    }
