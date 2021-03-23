from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float
from datetime import datetime
from json import dumps
from sqlalchemy.orm import validates
from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, unique=True)
    weight = Column(Float, nullable=False)
    region = Column(Integer, nullable=False)
    delivery_hours = Column(String, nullable=False)
    deliver = Column(String, nullable=True)
    complete = Column(Boolean, nullable=True, default=False)
    assign_time = Column(String, nullable=True)
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

    @validates('delivery_hours')
    def validate_delivery_hours(self, key, value):
        for time in value:
            start, end = time.split('-')
            start = datetime.strptime(start, '%H:%M')
            end = datetime.strptime(end, '%H:%M')
            if start > end:
                raise ValueError("Incorrect time format")
        return dumps(value)
