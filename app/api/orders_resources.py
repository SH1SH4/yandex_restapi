from flask_restful import Resource
from flask import Flask, Response
from json import loads, dumps
from modules.functions import json_validator
from modules.globals import TIME_FORMAT
from data import db_session
from data.orders import Order
from data.couriers import Courier
from datetime import datetime

app = Flask(__name__)


class OrdersResources(Resource):
    def post(self):
        data = json_validator()
        if type(data) == Response:
            return data

        db_sess = db_session.create_session()

        # Список непровалидированных id
        not_validate_orders = list()
        unvalidate = {
            'validation_error':  {
                'orders': not_validate_orders
            }
        }

        validate = list()  # Список провалидированных id

        try:
            for current in data:  # Перебор полученных значений
                if db_sess.query(Order).get(current['order_id']):
                    raise ValueError(f"id{current['order_id']} is already in the database")
                order = Order(**current)
                db_sess.add(order)
                validate.append(current['order_id'])

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
                {'orders': [{'id': i} for i in validate]}
            ),
            status=201,
            mimetype='application/json'
        )
        db_sess.close()
        return response


class OrdersAssign(Resource):
    def post(self):
        data = json_validator()
        if type(data) == Response:
            return data

        if 'courier_id' not in data:
            return Response(status=404)
        db_sess = db_session.create_session()
        courier_id = data['courier_id']
        courier = db_sess.query(Courier).get(courier_id)

        if courier:  # Проверяем, есть ли у нас курьер с таким id
            orders = db_sess.query(Order).filter(
                Order.deliver == courier.courier_id,
                not Order.complete,
            ).all()  # Вытаскиваем с БД все невыполненные заказы этого курьера

            if orders:
                # Если они есть - собираем их id в словарь и время получения для ответа
                orders_list = [{'id': i.order_id} for i in orders]
                assigned_time = orders[0].assign_time

            else:
                # Если их нет - вытаскиваем с БД все подходящие заказы без назначеного курьера
                orders = db_sess.query(Order).filter(
                    Order.deliver is None,
                    Order.region.in_(loads(courier.regions)),
                )
                # Сразу проверяем не назначен ли заказ на другого курьера
                # и соовтетствие регионам
                orders_list = list()
                assigned_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

                for order in orders:  # Перебираем заказы
                    # Получаем начало удобного промежутка получения
                    if courier.check_order_time(order):
                        # Проверяем на соответствие времени
                        order.deliver = courier.courier_id
                        order.assign_time = assigned_time
                        orders_list.append({'id': order.order_id})

                db_sess.commit()

            if orders_list:
                response_data = {
                    'orders': orders_list,
                    'assigned_time': assigned_time
                }
            else:
                response_data = {'orders': orders_list}

            response = app.response_class(
                response=dumps(response_data),
                status=200,
                mimetype='application/json'
            )
            db_sess.close()
            return response
        else:  # Иначе ошибка
            db_sess.close()
            return Response(status=400)


class OrderComplete(Resource):
    def post(self):
        db_sess = db_session.create_session()

        data = json_validator()
        if type(data) == Response:
            return data

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
            complete_time = datetime.strptime(data["complete_time"], TIME_FORMAT)
        except Exception as e:
            db_sess.close()
            return app.response_class(
                status=400,
                response=dumps({"error_description": str(e)}),
                mimetype='application/json')

        time = courier.delivered_time
        if not order.complete:
            # Если заказ не выполнен - пропускаем запись в БД
            if time:  # Если в доставках есть записи - загружаем их
                time = loads(time)

            else:  # Если в доставках ещё нет записей - создаём словарь
                time = dict()

            if order.region in time:
                # Если записи по региону есть - добавляем в них время
                time[order.region].append(str(complete_time))

            else:  # Если их нет - создаём
                time[order.region] = [
                    order.assign_time,
                    str(complete_time)]

            order.complete = True
            order.complete_time = complete_time
            courier.completed_orders += 1
            courier.delivered_time = dumps(time)
            db_sess.commit()
            db_sess.close()

        response = app.response_class(
            status=200,
            response=dumps({'order_id': order.order_id}),
            mimetype='application/json'
        )

        db_sess.close()
        return response
