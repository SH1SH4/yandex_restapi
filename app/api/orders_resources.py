from flask_restful import Resource
from flask import Flask, request
from json import loads, dumps
from jsonschema import validate, ValidationError
from .schemas import POST_ORDER_SCHEMA
from data import db_session
from data.orders import Order, DeliveryHours
from data.couriers import Courier
from datetime import datetime

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

app = Flask(__name__)


class OrdersResources(Resource):
    def post(self):
        try:
            data = loads(request.get_data())
            assert isinstance(data, dict)
            data = data['data']
        except Exception:
            response = Flask.response_class(
                status=400,
                response=dumps({"error_description": "Invalid JSON"}),
                mimetype='application/json')
            return response

        db_sess = db_session.create_session()

        # Список непровалидированных id
        not_validate_orders = list()
        unvalidate = {
            'validation_error':  {
                'orders': not_validate_orders
            }
        }

        valid = list()  # Список провалидированных id
        print(data)
        for current in data:  # Перебор полученных значений
            try:
                validate(instance=current, schema=POST_ORDER_SCHEMA)
                if db_sess.query(Order).get(current['order_id']):
                    raise ValueError(
                        f"id{current['order_id']} is already in the database")
                delivery_hours = current.pop('delivery_hours')
                order = Order(**current)
                order.add_delivery_time_to_order(delivery_hours, db_sess)
                db_sess.add(order)
                valid.append(current['order_id'])

            except ValidationError as e:
                response = app.response_class(
                    status=400,
                    response=dumps(
                        {"error_description": e.message}),
                    mimetype='application/json')
                db_sess.close()
                return response

            except KeyError:
                response = app.response_class(
                    status=400,
                    response=dumps(
                        {"error_description": "invalid data format"}),
                    mimetype='application/json')
                db_sess.close()
                return response

            except ValueError as e:
                validate_error = {
                    'id': current['order_id'],
                    'error_description': str(e)
                }
                not_validate_orders.append(validate_error)

            except TypeError as e:
                response = app.response_class(
                    status=400,
                    response=dumps({"error_description": str(e)}),
                    mimetype='application/json')
                db_sess.close()
                return response

        if not_validate_orders:
            # Если в непровалидированном списке есть значение
            # в ответ кладём ошибку и отправляем
            response = app.response_class(
                response=dumps(unvalidate),
                status=400,
                mimetype='application/json'
            )
            db_sess.close()
            return response
        # Иначе сохраняем базу данных и отправляем ответ
        db_sess.commit()
        response = app.response_class(
            response=dumps(
                {'orders': [{'id': i} for i in valid]}
            ),
            status=201,
            mimetype='application/json'
        )
        db_sess.close()
        return response


class OrdersAssign(Resource):
    def post(self):
        try:
            data = loads(request.get_data())
            assert isinstance(data, dict)
        except Exception:
            response = app.response_class(
                status=400,
                response=dumps({"error_description": "Invalid JSON"}),
                mimetype='application/json')
            return response

        if 'courier_id' not in data or\
                not isinstance(data['courier_id'], int):
            return app.response_class(status=400)
        db_sess = db_session.create_session()
        courier_id = data['courier_id']
        courier = db_sess.query(Courier).get(courier_id)

        if courier:  # Проверяем, есть ли у нас курьер с таким id
            orders = db_sess.query(Order).filter(
                Order.complete == False,
                Order.deliver == courier_id
            ).all()  # Вытаскиваем с БД все невыполненные заказы этого курьера
            if orders:
                # Если они есть - собираем их id в словарь
                # и время получения для ответа
                orders_list = [{'id': i.order_id} for i in orders]
                assigned_time = orders[0].assign_time

            else:
                # Если их нет - вытаскиваем с БД все подходящие заказы
                # без назначеного курьера
                orders = db_sess.query(Order).filter(
                    Order.deliver == None,
                    Order.region.in_(loads(courier.regions)),
                )
                # Сразу проверяем не назначен ли заказ на другого курьера
                # и соовтетствие регионам
                orders_list = list()
                assigned_time = datetime.now()

                for order in orders:  # Перебираем заказы
                    # Получаем начало удобного промежутка получения
                    if courier.check_order_time(order):
                        # Проверяем на соответствие времени
                        order.deliver = courier.courier_id
                        order.assign_time = assigned_time
                        orders_list.append({'id': order.order_id})

                db_sess.commit()
                db_sess.close()

            if orders_list:
                response_data = {
                    'orders': orders_list,
                    'assigned_time': datetime.strftime(assigned_time,
                                                       TIME_FORMAT)
                }
            else:
                response_data = {'orders': orders_list}

            response = app.response_class(
                response=dumps(response_data),
                status=200,
                mimetype='application/json'
            )
            return response
        else:  # Иначе ошибка
            db_sess.close()
            return app.response_class(status=400)


class OrderComplete(Resource):
    def post(self):
        db_sess = db_session.create_session()

        try:
            data = loads(request.get_data())
            assert isinstance(data, dict)
        except Exception:
            response = Flask.response_class(
                status=400,
                response=dumps({"error_description": "Invalid JSON"}),
                mimetype='application/json')
            return response

        if 'courier_id' not in data:
            db_sess.close()
            return app.response_class(status=400)

        courier = db_sess.query(Courier).get(data['courier_id'])
        order = db_sess.query(Order).filter(
            Order.order_id == data['order_id'],
            Order.deliver == data['courier_id']
        ).first()

        if not order:
            # Если у нас нет такого заказа, либо заказ у другого курьера
            db_sess.close()
            return app.response_class(
                status=400,
                response=dumps({"error_description": "Unknown order id"}),
                mimetype='application/json')

        if not courier:  # Проверка наличия курьера
            db_sess.close()
            return app.response_class(
                status=400,
                response=dumps({"error_description": "Unknown courier id"}),
                mimetype='application/json')

        try:  # Проверка формата времени
            datetime.strptime(data["complete_time"], TIME_FORMAT)
            complete_time = data["complete_time"]
        except Exception as e:
            db_sess.close()
            return app.response_class(
                status=400,
                response=dumps({"error_description": str(e)}),
                mimetype='application/json')

        order.complete = True
        for i in db_sess.query(DeliveryHours).filter(
                DeliveryHours.order_id == order.order_id
        ):
            order.delivery_hours.remove(i)
        order.complete_time = datetime.strptime(complete_time, TIME_FORMAT)
        earn = 500
        cour_type = courier.courier_type
        if cour_type == 'foot':
            earn *= 2
        elif cour_type == 'bike':
            earn *= 5
        elif cour_type == 'car':
            earn *= 9
        courier.earnings += earn
        db_sess.commit()

        response = app.response_class(
            status=200,
            response=dumps({'order_id': order.order_id}),
            mimetype='application/json'
        )

        db_sess.close()
        return response
