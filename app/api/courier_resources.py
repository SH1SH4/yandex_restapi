from flask_restful import Resource
from flask import Flask, Response
from json import loads, dumps
from modules.functions import json_validator
from data import db_session
from data.couriers import Courier
from data.orders import Order
from datetime import datetime

app = Flask(__name__)


class CouriersResource(Resource):
    def post(self):
        data = json_validator()
        if type(data) == Response:
            return data

        db_sess = db_session.create_session()
        not_validate_couriers = list()
        unvalidate = {
            'validation_error': {
                'couriers': not_validate_couriers
            }
        }  # Словарь для преобразования в json для ответа

        validate = list()
        #  Блок проверки данных
        try:
            data = data['data']
            for current in data:  # Перебор полученных значений
                cour_id = current['courier_id']
                if db_sess.query(Courier).get(cour_id):
                    raise ValueError(f'id{cour_id} is already in the database')
                courier = Courier(**current)
                db_sess.add(courier)
                validate.append(cour_id)

        except ValueError as e:
            validate_error = {
                'id': current['courier_id'],
                'error_description': str(e)
            }
            not_validate_couriers.append(validate_error)

        except KeyError:
            response = app.response_class(
                status=400,
                response=dumps({
                    "error_description": "Invalid data format"
                }),
                mimetype='application/json'
            )
            return response

        except TypeError as e:
            response = app.response_class(
                status=400,
                response=dumps({"error_description": str(e)}),
                mimetype='application/json')
            db_sess.close()
            return response

        # Если непровалидировался id возвращаем их список
        if not_validate_couriers:
            response = app.response_class(
                response=dumps(unvalidate),
                status=400,
                mimetype='application/json'
            )
            db_sess.close()
            return response

        db_sess.commit()
        response = app.response_class(
            response=dumps(
                {'couriers': [{'id': i} for i in validate]}
            ),
            status=201,
            mimetype='application/json'
        )
        db_sess.close()
        return response


class CouriersListResource(Resource):
    def patch(self, courier_id):
        db_sess = db_session.create_session()
        data = json_validator()
        if type(data) == Response:
            return data
        courier = db_sess.query(Courier).get(courier_id)

        try:
            assert courier  # Если не нашли курьера - выкидываем ошибку
            courier.update(**data)
            # Блок для проверки доступности заказа с новыми данными
            orders = db_sess.query(Order).filter(Order.deliver == courier_id,
                                                 not Order.complete).all()
            for order in orders:
                if not courier.check_order_time(order) or\
                        order.region not in loads(courier.regions):
                    order.deliver = None
                    order.assign_time = None

            db_sess.commit()
            response = app.response_class(
                response=dumps(courier.to_dict()),
                status=201,
                mimetype='application/json'
            )
            db_sess.close()
            return response

        except ValueError as e:
            response = app.response_class(
                status=400,
                response=dumps({"error_description": str(e)}),
                mimetype='application/json')
            db_sess.close()
            return response

        except AssertionError:
            db_sess.close()
            response = app.response_class(status=404)
            return response


class CourierInfo(Resource):
    def get(self, courier_id):
        try:
            db_sess = db_session.create_session()
            courier = db_sess.query(Courier).get(courier_id)
            assert courier
            earnings = courier.completed_orders * 500
            cour_type = courier.courier_type
            if cour_type == 'foot':
                earnings *= 2
            elif cour_type == 'bike':
                earnings *= 5
            elif cour_type == 'car':
                earnings *= 9
            data = {
                    "courier_id": courier_id,
                    "courier_type": cour_type,
                    "regions": loads(courier.regions),
                    "working_hours": loads(courier.working_hours),
                    "earnings": earnings
                }
            courier.get_rating(data)
            response = app.response_class(
                status=200,
                response=dumps(data),
                mimetype='application/json'
            )
            return response
        except AssertionError:
            return app.response_class(status=404)
