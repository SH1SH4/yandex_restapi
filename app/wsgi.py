from app import app
from data import db_session

db_session.global_init('db/delivery.db')

if __name__ == "__main__":
    app.run()