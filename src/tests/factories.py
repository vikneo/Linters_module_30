import factory
import factory.fuzzy as fuzzy
from faker import Faker

from src.parking.models import db, Client, Parking

_faker = Faker("ru_RU")


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = _faker.first_name()
    surname = _faker.last_name()
    credit_card = fuzzy.FuzzyChoice(choices = [_faker.credit_card_number(), None])
    car_number = _faker.license_plate()


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = _faker.address()
    name = fuzzy.FuzzyText(prefix = 'Стоянка у ')
    opened = fuzzy.FuzzyChoice(choices = [True, False])
    count_places = _faker.random_int(10, 50)
    count_available_places = factory.LazyAttribute(lambda obj: obj.count_places)
