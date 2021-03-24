from flask_restful import Resource, request
from flask import Flask
from json import loads, dumps, JSONDecodeError
from data import db_session
from data.couriers import Courier
from data.orders import Order

app = Flask(__name__)


class CouriersResource(Resource):
    def post(self):
        db_sess = db_session.create_session()
        not_validate_couriers = list()
        unvalidate = {
            'validation_error': {
                'couriers': not_validate_couriers
            }
        }  # Словарь для преобразования в json для ответа

        validate = list()
        try:
            data = loads(request.get_data())
            assert isinstance(data, dict)
            data = data['data']
        except KeyError:
            response = Flask.response_class(
                status=400,
                response=dumps({"error_description": "Invalid data format"}),
                mimetype='application/json')
            return response

        except Exception:
            response = Flask.response_class(
                status=400,
                response=dumps({"error_description": "Invalid JSON"}),
                mimetype='application/json')
            return response
        #  Блок проверки данных
        for current in data:  # Перебор полученных значений
            try:
                cour_id = current['courier_id']
                if db_sess.query(Courier).get(cour_id):
                    raise ValueError(
                        f'id{cour_id} is already in the database')
                courier = Courier(**current)
                db_sess.add(courier)
                validate.append(cour_id)

            except ValueError as e:
                validate_error = {
                    'id': current['courier_id'],
                    'error_description': str(e)
                }
                not_validate_couriers.append(validate_error)
                print(not_validate_couriers)

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
        courier = db_sess.query(Courier).get(courier_id)
        try:
            data = loads(request.get_data())
            assert isinstance(data, dict)
        except Exception:
            response = Flask.response_class(
                status=400,
                response=dumps({"error_description": "Invalid JSON"}),
                mimetype='application/json')
            return response

        try:
            # Если не нашли курьера - выкидываем ошибку
            if not courier:
                raise ValueError('Invalid courier_id')
            courier.update(**data)
            # Блок для проверки доступности заказа с новыми данными
            orders = db_sess.query(Order).filter(Order.deliver == courier_id,
                                                 not Order.complete).all()
            for order in orders:
                if not courier.check_order_time(order) or \
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


class CourierInfo(Resource):
    def get(self, courier_id):
        try:
            db_sess = db_session.create_session()
            courier = db_sess.query(Courier).get(courier_id)
            assert courier
            data = {
                "courier_id": courier_id,
                "courier_type": courier.courier_type,
                "regions": loads(courier.regions),
                "working_hours": loads(courier.working_hours),
                "earnings": courier.earnings
            }
            # Считаем рейтинг
            if courier.completed_orders > 0:
                td = list()
                for region in loads(courier.regions):
                    orders = db_sess.query(Order).filter(
                        Order.deliver == courier_id,
                        Order.region == region,
                        Order.complete == True,
                    ).order_by(Order.complete_time).all()
                    if orders:
                        times = [orders[0].assign_time]
                        for i in orders:
                            times.append(i.complete_time)
                        differences = list()
                        for i in range(len(times) - 1):
                            last_order = times[i]
                            now_order = times[i + 1]
                            diff = (now_order - last_order)
                            differences.append(diff.total_seconds())
                        average = sum(differences) / len(differences)
                        td.append(average)
                t = min(td)
                rating = (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5
                data['rating'] = round(rating, 2)
            response = app.response_class(
                status=200,
                response=dumps(data),
                mimetype='application/json'
            )
            return response
        except AssertionError:
            return app.response_class(status=404)
