from flask import Flask
from data import db_session
from api.courier_resources import CouriersResource, CouriersListResource, CourierInfo
from api.orders_resources import OrdersResources, OrdersAssign, OrderComplete
from flask_restful import Api

app = Flask(__name__)
api = Api(app)


def main():
    db_session.global_init('db/delivery.db')
    app.run(host='127.0.0.1', port=5000, threaded=True)


api.add_resource(CouriersResource, '/couriers')
api.add_resource(CouriersListResource, '/couriers/<int:courier_id>')
api.add_resource(CourierInfo, '/couriers/<int:courier_id>')
api.add_resource(OrdersResources, '/orders')
api.add_resource(OrdersAssign, '/orders/assign')
api.add_resource(OrderComplete, '/orders/complete')

if __name__ == '__main__':
    main()