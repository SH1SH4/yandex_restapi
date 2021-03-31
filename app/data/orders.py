from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, \
    ForeignKey
from datetime import datetime
from json import dumps
from sqlalchemy.orm import validates, relationship
from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, unique=True)
    weight = Column(Float, nullable=False)
    region = Column(Integer, nullable=False)
    delivery_hours = relationship("DeliveryHours")
    deliver = Column(String, nullable=True)
    complete = Column(Boolean, nullable=True, default=False)
    cost = Column(Integer, nullable=True)
    assign_time = Column(DateTime, nullable=True)
    complete_time = Column(DateTime, nullable=True)
    keys = ("order_id", "weight", "region", "delivery_hours")

    @validates('order_id')
    def validate_id(self, key, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"Invalid id {value}, id must be an integer")
        return value

    @validates('weight')
    def validate_weight(self, key, value):
        float(value)
        if not 0.01 <= value <= 50:
            raise ValueError("Allowed weight from 0.01 kg to 50kg")
        return value

    @validates('region')
    def validate_region(self, key, value):
        if (not isinstance(value, int)) or value <= 0:
            raise ValueError(
                f"Invalid region {value}, region must be an integer")
        return value

    def add_delivery_time_to_order(self, values, db_sess):
        for time in values:
            start, end = time.split('-')
            work_hours = {
                'order_id': self.order_id,
                'start': datetime.strptime(start, '%H:%M'),
                'end': datetime.strptime(end, '%H:%M')
            }
            if work_hours['start'] > work_hours['end']:
                raise ValueError('Incorrect time format')
            deliv_hours = DeliveryHours(**work_hours)
            db_sess.add(deliv_hours)


class DeliveryHours(SqlAlchemyBase):
    __tablename__ = 'delivery_hours'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
