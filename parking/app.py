import datetime

from flask import Flask, render_template, jsonify, request
from sqlalchemy import inspect, select, update
from config import SECRET_KEY, database


def create_app(test_config = None):
    """
    Создание приложения Flask с помощью "Фабрика приложений" (Application Factory)
    """
    if test_config is None:
        db = database
    else:
        db = "sqlite://"

    app = Flask(__name__, instance_relative_config = True)
    app.secret_key = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = db

    from models import db, Client, Parking, ClientParking
    db.init_app(app)

    @app.before_request
    def before_request():
        """
        Проверка существуют ли таблицы в базе данных и создаются таблицы,
        если они отсутствуют.
        """
        tables = inspect(db.engine).get_table_names()
        if not tables:
            db.create_all()

    @app.context_processor
    def get_parking():
        """
        Добавлен контекст процессор для отображения всех парковок
        """
        parking_all = db.session.execute(select(Parking)).scalars().all()
        _parkings = [parking.to_json() for parking in parking_all]
        return dict(parkings = _parkings)

    @app.route('/')
    def index():
        """

        """
        return render_template('index.html', parking = True, parking_count = 10)

    # =======================================================================
    # =                     Routes for API                                  =
    # =======================================================================

    @app.route('/clients', methods = ["GET", "POST"])
    def clients():
        """
        Display all clients
        """

        if request.method == 'POST':
            data = request.json
            client = Client(
                name = data['name'],
                surname = data['surname'],
                credit_card = data['credit_card'],
                car_number = data['car_number']
            )

            db.session.add(client)
            db.session.commit()

            return jsonify(client = client.to_json(), clients = Client.all() if test_config else ''), 201
        else:
            clients = Client.all()
            return jsonify(clients = clients)

    @app.route('/clients/<int:client_id>', methods = ['GET'])
    def client_by_id(client_id: int):
        """
        Display client by ID
        """
        client = db.session.execute(select(Client).where(Client.id == client_id)).scalar()
        if not client:
            return {"Not found": 404}, 404

        return jsonify(client = client.to_json())

    @app.route("/parkings", methods = ["GET", "POST"])
    def parkings():
        """
        Method GET:
        Displaying the entire parking list.
        Method POST:
        Creating a new parking lot.
        """

        if request.method == 'POST':
            data = request.json
            parking = Parking(
                name = data['name'],
                address = data['address'],
                opened = data['opened'],
                count_places = data['count_places'],
                count_available_places = data['count_available_places']
            )
            db.session.add(parking)
            db.session.commit()

            parkings = Parking.all()
            return jsonify(parking = parking.to_json(), parkings = parkings if test_config else ''), 201
        else:
            parkings = Parking.all()
            return jsonify(parkings = parkings)

    @app.route("/parkings/<int:parking_id>", methods = ["GET"])
    def get_parking_by_id(parking_id: int):
        parking = db.session.execute(select(Parking).where(Parking.id == parking_id)).scalar()
        if not parking:
            return {"Not found": 404}, 404

        return jsonify(parking = parking.to_json()), 200

    def check_count_available_place(parking_id: int) -> int | bool:
        count_available_place = db.session.execute(
            select(Parking.count_available_places).where(Parking.id == parking_id)
        ).scalar()
        if count_available_place:
            return count_available_place
        return False

    @app.route("/client_parkings", methods = ["POST", "DELETE"])
    def get_client_parkings():
        """ Business logic for the arrival and departure of the customer to the parking lot.
        Using the "POST" method, the client enters the parking lot
        (we pass the client_id and parking_id, and reduce the available space by 1),
        if there are no available spaces, then we close the parking lot: opened=False.
        Using the "DELETE" method, the client leaves the parking lot
        (we pass the client_id and parking_id, and increase the free space by 1)
        """
        data = request.json
        client_id: int = data['client_id']
        parking_id: int = data['parking_id']
        parking_opened = db.session.execute(
            select(Parking.opened).where(Parking.id == parking_id)
        ).scalar()
        client_card = db.session.execute(
            select(Client.credit_card).where(Client.id == client_id)
        ).scalar()

        if request.method == 'POST':
            if not parking_opened:
                return {"No place": 404}, 404
            if not client_card:
                return {"Link the card to your account": 404}, 404
            arrival = ClientParking(
                client_id = client_id,
                parking_id = parking_id,
                time_in = datetime.datetime.now()
            )
            db.session.add(arrival)

            db.session.execute(
                update(Parking)
                .values(count_available_places = Parking.count_available_places - 1)
                .where(Parking.id == parking_id)
            )
            count_available_place = check_count_available_place(parking_id = parking_id)
            if count_available_place == 0:
                db.session.execute(update(Parking)
                                   .values(opened = False)
                                   .where(Parking.id == parking_id))
            db.session.commit()
            parking = db.session.execute(select(Parking).where(Parking.id == parking_id)).scalar()
            client_info = {
                "parking": parking.to_json(),
                "card": client_card,
            }
            return jsonify(arrival = arrival.to_json(), client = client_info if test_config else ''), 201

        elif request.method == 'DELETE':
            try:
                departure = db.session.execute(
                    select(ClientParking)
                    .where(ClientParking.client_id == client_id, ClientParking.parking_id == parking_id)
                ).scalar()
                if not departure.time_in:
                    return {"The client did not enter the parking lot": 404}, 404
            except TypeError:
                return {"Not available": 404}, 404
            departure.time_out = datetime.datetime.now()

            db.session.execute(update(Parking)
                               .values(count_available_places = Parking.count_available_places + 1)
                               .where(Parking.id == parking_id)
                               )
            count_available_place = check_count_available_place(parking_id = parking_id)

            if count_available_place > 0:
                db.session.execute(update(Parking).values(opened = True).where(Parking.id == parking_id))
            db.session.commit()

            parking = db.session.execute(select(Parking).where(Parking.id == parking_id)).scalar()
            departure_info = {
                "departure": departure.to_json(),
                "payment": True,
                "parking": parking.to_json(),
            }
            return jsonify(departure = departure_info), 201
        else:
            return {"Contact the administrator": 404}, 404

    return app
