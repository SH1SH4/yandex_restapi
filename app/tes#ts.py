import app
import unittest
from data import db_session
from data.couriers import Courier
from json import dumps
import os

try:
    os.remove("db/test.db")
except Exception:
    pass
db_session.global_init('db/test.db')

class TestCouriersResource(unittest.TestCase):
    def setUp(self):
        self.db_sess = db_session.create_session()
        self.app = app.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_post_courier(self):
        js = dumps({
            "data":
                [{
                    "courier_id": 0,
                    "regions": [1],
                    "courier_type": 'foot',
                    "working_hours": ["12:00-18:00"]
                }]
        })
        rv = self.client.post('/couriers', data=js)
        self.assertEqual(rv.status_code, 201)

    # def test_post_courier_id_already_in_db(self):
    #     js = dumps({
    #         "data":
    #             [{
    #                 "courier_id": 0,
    #                 "regions": [1],
    #                 "courier_type": 'foot',
    #                 "working_hours": ["12:00-18:00"]
    #             }]
    #     })
    #     rv = self.client.post('/couriers', data=js)
    #     self.assertEqual(rv.status_code, 400)
    #
    # def test_post_courier_id_already_in_db2(self):
    #     js = dumps({
    #         "data":
    #             [{
    #                 "courier_id": 0,
    #                 "regions": [1],
    #                 "courier_type": 'foot',
    #                 "working_hours": ["12:00-18:00"]
    #             }]
    #     })
    #     rv = self.client.post('/couriers', data=js)
    #     self.assertEqual(rv.status_code, 400)
    #
    # def test_post_courier_id_error(self):
    #     js = dumps({
    #         "data":
    #             [{
    #                 "courier_id": 0.1,
    #                 "regions": [1],
    #                 "courier_type": 'foot',
    #                 "working_hours": ["12:00-18:00"]
    #             }]
    #     })
    #     rv = self.client.post('/couriers', data=js)
    #     self.assertEqual(rv.status_code, 400)
    #
    # def test_post_courier_region_error(self):
    #     js = dumps({
    #         "data":
    #             [{
    #                 "courier_id": 1,
    #                 "regions": 1,
    #                 "courier_type": "foot",
    #                 "working_hours": ["12:00-18:00"]
    #             }]
    #     })
    #     rv = self.client.post('/couriers', data=js)
    #     self.assertEqual(rv.status_code, 400)
    #
    #     js = dumps({
    #         "data":
    #             [{
    #                 "courier_id": 1,
    #                 "regions": [22, 1.5],
    #                 "courier_type": 'foot',
    #                 "working_hours": ["12:00-18:00"]
    #             }]
    #     })
    #     rv = self.client.post('/couriers', data=js)
    #     self.assertEqual(rv.status_code, 400)
    #
    # def test_post_courier_type_error(self):
    #     js = dumps({
    #         "data":
    #             [{
    #                 "courier_id": 2,
    #                 "regions": [1],
    #                 "courier_type": 'helicopter',
    #                 "working_hours": ["12:00-18:00"]
    #             }]
    #     })
    #     rv = self.client.post('/couriers', data=js)
    #     self.assertEqual(rv.status_code, 400)
    #
    # def test_post_courier_time_error(self):
    #     js = dumps({
    #         "data":
    #             [{
    #                 "courier_id": 3,
    #                 "regions": [1],
    #                 "courier_type": 'foot',
    #                 "working_hours": ["morning-18:00"]
    #             }]
    #     })
    #     rv = self.client.post('/couriers', data=js)
    #     self.assertEqual(rv.status_code, 400)
    #
    #     js = dumps({
    #         "data":
    #             [{
    #                 "courier_id": 3,
    #                 "regions": [1],
    #                 "courier_type": 'foot',
    #                 "working_hours": ["22:00-18:00"]
    #             }]
    #     })
    #     rv = self.client.post('/couriers', data=js)
    #     self.assertEqual(rv.status_code, 400)
    #
    #     js = dumps({
    #         "data":
    #             [{
    #                 "courier_id": 3,
    #                 "regions": [1],
    #                 "courier_type": 'foot',
    #                 "working_hours": "09:00-18:00"
    #             }]
    #     })
    #     rv = self.client.post('/couriers', data=js)
    #     self.assertEqual(rv.status_code, 400)
    #
    # def test_post_courier_invalid_json(self):
    #     js = dumps({
    #         "not_data":
    #             [{
    #                 "courier_id": 3,
    #                 "regions": [1],
    #                 "courier_type": 'foot',
    #                 "working_hours": ["morning-18:00"]
    #             }]
    #     })
    #     rv = self.client.post('/couriers', data=js)
    #     self.assertEqual(rv.status_code, 400)
    #
    #     js = dumps({
    #         "data":
    #             [{
    #                 "extra_key": "error",
    #                 "courier_id": 3,
    #                 "regions": [1],
    #                 "courier_type": 'foot',
    #                 "working_hours": ["08:00-18:00"]
    #             }]
    #     })
    #     rv = self.client.post('/couriers', data=js)
    #     self.assertEqual(rv.status_code, 400)
    #
    #     js = dumps('''{
    #         "data":
    #             [{,
    #                 "courier_id": 3,
    #                 "regions": [1],
    #                 "courier_type": 'foot',
    #                 "working_hours": ["morning-18:00"]
    #             }]
    #     }''')
    #     rv = self.client.post('/couriers', data=js)
    #     print(self.db_sess.query(Courier).get(0), 0)
    #     self.assertEqual(rv.status_code, 400)

    def test_patch_courier(self):
        js = dumps({
            "courier_type": "car",
            "working_hours": ["08:00-22:00"]
        })
        print(self.db_sess.query(Courier).get(0), 1)
        rv = self.client.patch('/couriers/0', data=js)
        self.assertEqual(rv.status_code, 201)


if __name__ == "__main__":
    unittest.main()
