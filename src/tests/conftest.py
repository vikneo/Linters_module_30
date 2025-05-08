from datetime import datetime, timedelta

import pytest

from src.parking.app import create_app
from src.parking.models import Client, ClientParking, Parking
from src.parking.models import db as _db


@pytest.fixture()
def app():
    _app = create_app(test_config=True)
    _app.config["TESTING"] = True
    time_in = datetime.now()

    with _app.app_context():
        _db.create_all()

        client_1 = Client(
            name="Alex",
            surname="Minnesota",
            credit_card="1234-5678",
            car_number="X123OO42",
        )
        client_2 = Client(
            name="Bob",
            surname="Teilor",
            credit_card="",  # 5678-1234
            car_number="X153BB142",
        )
        parking = Parking(
            address="Новосибирск, Площадь Карла Маркса, 7",
            name="Сан Сити",
            opened=True,
            count_places=20,
            count_available_places=8,
        )
        parking_2 = Parking(
            address="Новосибирск, Ватутина, 27",
            name="На Горской",
            opened=False,
            count_places=13,
            count_available_places=3,
        )

        client_parking = ClientParking(
            client_id=1,
            parking_id=1,
            time_in=time_in,
            time_out=(time_in + timedelta(4)),
        )
        client_parking_2 = ClientParking(
            client_id=1,
            parking_id=2,
        )
        _db.session.add_all(
            [client_1, client_2, parking, parking_2, client_parking, client_parking_2]
        )
        _db.session.commit()
        yield _app
        _db.session.close()
        _db.drop_all()


@pytest.fixture()
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture()
def runner(app):
    client = app.test_cli_runner()
    yield client


@pytest.fixture()
def db(app):
    with app.app_context():
        yield _db
