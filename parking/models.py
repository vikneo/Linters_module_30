import datetime
from typing import Any, Dict, List, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Boolean, ForeignKey, Integer, String, UniqueConstraint,
                        select)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db: SQLAlchemy = SQLAlchemy(
    model_class = Base
)


class Client(Base):
    """
    Класс `Client` описывает модель клиента
    """
    __tablename__ = 'clients'
    __table_args__ = (
        UniqueConstraint("car_number", ),
    )

    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str] = mapped_column(String(50))
    credit_card: Mapped[Optional[str]] = mapped_column(String(50))
    car_number: Mapped[str] = mapped_column(String(10))
    parkings: Mapped[List['Parking']] = relationship(
        secondary = 'client_parking',
        back_populates = 'clients'
    )

    def __repr__(self) -> str:
        return f"Client(name={self.name}; car_number={self.car_number})"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def all(cls):
        query = db.session.execute(select(cls)).scalars().all()
        return [client.to_json() for client in query]


class Parking(Base):
    """
    Класс `Parking` описывает модель парковки
    """
    __tablename__ = 'parkings'
    __table_args__ = (
        UniqueConstraint('address', ),
    )

    id: Mapped[int] = mapped_column(primary_key = True)
    address: Mapped[str] = mapped_column(String(100))
    name: Mapped[Optional[str]] = mapped_column(String(50))
    opened: Mapped[Optional[bool]] = mapped_column(Boolean, default = True)
    count_places: Mapped[int] = mapped_column(Integer)
    count_available_places: Mapped[int] = mapped_column(Integer)
    clients: Mapped[List['Client']] = relationship(
        secondary = 'client_parking',
        back_populates = 'parkings'
    )

    def __repr__(self):
        return f"Parking(address={self.address}; opened={self.opened})"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def all(cls):
        query = db.session.execute(select(cls)).scalars().all()
        return [parking.to_json() for parking in query]


class ClientParking(Base):
    """
    Связывающая таблица клиента и парковки
    """
    __tablename__ = 'client_parking'

    id: Mapped[int] = mapped_column(primary_key = True)
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.id'))
    parking_id: Mapped[int] = mapped_column(ForeignKey('parkings.id'))
    time_in: Mapped[Optional[datetime.datetime]] = mapped_column()
    time_out: Mapped[Optional[datetime.datetime]] = mapped_column()

    def __repr__(self):
        return f"Client(id={self.client_id}); Parking(id={self.parking_id})"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
