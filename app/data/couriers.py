from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates
from datetime import datetime
from json import loads, dumps
from .db_session import SqlAlchemyBase


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = Column(Integer, primary_key=True, unique=True)
    courier_type = Column(String, nullable=False)
    regions = Column(String, nullable=False)
    working_hours = Column(String, nullable=False)
    completed_orders = Column(Integer, default=0)
    earnings = Column(Integer, default=0)
    keys = ('courier_id', 'courier_type', 'regions', 'working_hours')

    @validates('courier_id')
    def validate_id(self, key, value):
        if (not isinstance(value, int)) or value < 0:
            raise ValueError(f"Invalid id {value}, id must be an integer")
        return value

    @validates('courier_type')
    def validate_type(self, key, value):
        if not value in ['foot', 'bike', 'car']:
            raise ValueError('Invalid courier type')
        return value

    @validates('regions')
    def validate_regions(self, key, value):
        if not isinstance(value, list):
            raise ValueError(f"Regions must be list type")
        for region in value:
            if (not isinstance(region, int)) or region <= 0:
                raise ValueError(f"Invalid region {region}, region must be an integer")
        return dumps(value)

    @validates('working_hours')
    def validate_wh(self, key, value):
        if not isinstance(value, list):
            raise ValueError('Working_hours must be list')
        for time in value:
            start, end = time.split('-')
            start = datetime.strptime(start, '%H:%M')
            end = datetime.strptime(end, '%H:%M')
            if start > end:
                raise ValueError('End of work before start')
        return dumps(value)

    def to_dict(self):
        return {
            'courier_id': self.courier_id,
            'courier_type': self.courier_type,
            'regions': loads(self.regions),
            'working_hours': loads(self.working_hours)
        }

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'courier_type':
                self.courier_type = value
            elif key == 'regions':
                self.regions = value
            elif key == 'working_hours':
                self.working_hours = value
            else:
                raise ValueError('Unknown key in data')

    def check_order_time(self, order):
        for order_time in loads(order.delivery_hours):
            order_start, order_end = order_time.split('-')
            # Преобразуем в экземпляр datetime
            order_start = datetime.strptime(order_start, '%H:%M')

            # Перебираем времена работы курьера
            for time in loads(self.working_hours):
                # Отделяем начало работы от окончания
                start, end = time.split('-')
                # Преобразуем в экземпляр datetime
                courier_start = datetime.strptime(start, '%H:%M')
                courier_end = datetime.strptime(end, '%H:%M')
                # Проверка вхождения начала времени получения в промежуток
                # времени доставки, если входит, то
                # прерываем цикл и принимаем заказ
                if courier_start <= order_start < courier_end or\
                    order_start <= courier_start < courier_end:
                    return True  # Если входит - возвращаем True
            return False  # Если True не вернули - возвращаем False