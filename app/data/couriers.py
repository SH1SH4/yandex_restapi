from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import validates, relationship
from datetime import datetime
from json import loads, dumps
from .db_session import SqlAlchemyBase


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = Column(Integer, primary_key=True, unique=True)
    courier_type = Column(String, nullable=False)
    regions = Column(String, nullable=False)
    working_hours = relationship("WorkingHours")
    earnings = Column(Integer, default=0)

    keys = ('courier_id', 'courier_type', 'regions', 'working_hours')
    coefficient = {'foot': 2, 'bike': 5, 'car': 9}
    capacity = {'foot': 10, 'bike': 15, 'car': 50}

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
                raise ValueError(
                    f"Invalid region {region}, region must be an integer")
        return dumps(value)

    def get_capacity(self):
        return self.capacity[self.courier_type]

    def to_dict(self):
        data = {
            'courier_id': self.courier_id,
            'courier_type': self.courier_type,
            'regions': loads(self.regions),
        }
        working_hours = list()
        for i in self.working_hours:
            work_hour = f'{i.start.strftime("%H:%M")}-{i.end.strftime("%H:%M")}'
            working_hours.append(work_hour)
        data['working_hours'] = working_hours
        return data

    def add_working_time_to_courier(self, values, db_sess):
        for time in values:
            start, end = time.split('-')
            work_hours = {
                'courier_id': self.courier_id,
                'start': datetime.strptime(start, '%H:%M'),
                'end': datetime.strptime(end, '%H:%M')
            }
            if work_hours['start'] > work_hours['end']:
                raise ValueError('End of work before start')
            courier_hours = WorkingHours(**work_hours)
            db_sess.add(courier_hours)

    def update(self, db_sess, **kwargs):
        print(kwargs)
        for key, value in kwargs.items():
            if key == 'courier_type':
                self.courier_type = value
            elif key == 'regions':
                self.regions = value
            elif key == 'working_hours':
                working_hours = value
                for i in db_sess.query(WorkingHours).filter(
                        WorkingHours.courier_id == self.courier_id
                ):
                    self.working_hours.remove(i)
                self.add_working_time_to_courier(working_hours, db_sess)
            else:
                raise ValueError('Unknown key in data')

    def check_order_time(self, order):
        # Перебираем времена работы курьера
        for deliv_time in order.delivery_hours:
            for work_time in self.working_hours:
                # Проверка вхождения начала времени получения в промежуток
                # времени доставки, если входит, то
                # прерываем цикл и принимаем заказ
                if deliv_time.start <= work_time.start < deliv_time.end or \
                        work_time.start <= deliv_time.start < work_time.end:
                    return True  # Если входит - возвращаем True
        return False  # Если True не вернули - возвращаем False


class WorkingHours(SqlAlchemyBase):
    __tablename__ = 'working_hours'
    id = Column(Integer, primary_key=True, autoincrement=True)
    courier_id = Column(Integer, ForeignKey('couriers.courier_id'))
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
