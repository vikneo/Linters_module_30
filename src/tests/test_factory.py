from src.parking.models import Client, Parking

from .factories import ClientFactory, ParkingFactory


def test_create_client(client, db):
    """Testing created client"""

    then_clients = db.session.query(Client).all()
    client = ClientFactory()
    db.session.commit()
    now_clients = db.session.query(Client).all()

    assert client.id == 3
    assert client.name == now_clients[-1].name
    assert len(then_clients) < len(now_clients)
    assert len(now_clients) == 3


def test_create_parking(client, db):
    """Testing created parking"""

    then_parkings = db.session.query(Parking).all()
    parking = ParkingFactory()
    db.session.commit()
    now_parkings = db.session.query(Parking).all()

    assert now_parkings[-1].id == parking.id
    assert parking.name == now_parkings[-1].name
    assert len(then_parkings) < len(now_parkings)
    assert len(now_parkings) == 3
