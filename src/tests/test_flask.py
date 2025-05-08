from datetime import datetime

import pytest
from flask import Flask


def test_create_app(app):
    """Testing a created application is Flask"""

    assert isinstance(app, Flask)
    assert app.config['TESTING']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == "sqlite://"


def test_index_html(client):
    """Testing the template index.html"""

    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.headers[0] == ("Content-Type", "text/html; charset=utf-8")


def test_page_not_found(client):
    """Testing for a non-existent page"""

    resp = client.get("/none_page")
    assert resp.status_code == 404


def test_get_clients(client):
    """Testing the list of clients and the url address /clients"""

    resp = client.get("/clients")
    assert resp.status_code == 200
    assert resp.headers[0] == ("Content-Type", "application/json")
    assert len(resp.json["clients"]) == 2


def test_post_clients(client):
    """Testing creating a client"""

    data = {
        "name": "new name",
        "surname": "new surname",
        "credit_card": "1290-2389",
        "car_number": "C123CC56",
    }
    resp = client.post("/clients", json=data)

    assert resp.status_code == 201
    assert resp.json["client"]["name"] == "new name"
    assert len(resp.json["clients"]) == 3


def test_get_client_by_id(client):
    """Testing the client by "id" and url address /clients/2"""

    resp = client.get("/clients/2")
    assert resp.status_code == 200
    assert resp.headers[0] == ("Content-Type", "application/json")
    assert resp.json["client"]["name"] == "Bob"


def test_get_not_client_by_id(client):
    """Testing a non-existent client"""

    resp = client.get("/clients/4")
    assert resp.status_code == 404
    assert "Not found" in resp.json


def test_get_parking(client):
    """Testing the parking by "id" and url address /parkings"""

    resp = client.get("/parkings")
    assert resp.status_code == 200
    assert len(resp.json["parkings"]) == 2


def test_post_parkings(client):
    """Testing creating a parking"""

    data = {
        "address": "Moscow Arbat st. 78",
        "name": "On Gorskaya st.",
        "opened": False,
        "count_places": 25,
        "count_available_places": 0,
    }
    resp = client.post("/parkings", json=data)
    assert resp.status_code == 201
    assert resp.json["parking"]["name"] == "On Gorskaya st."
    assert len(resp.json["parkings"]) == 3
    # testing on opened parkings
    cnt = [1 if _open["opened"] else 0 for _open in resp.json["parkings"]]
    assert sum(cnt) == 1


def test_parking_by_id(client):
    """Testing the parking by "id" and url address /parkings/1"""

    resp = client.get("/parkings/1")
    assert resp.status_code == 200
    assert resp.json["parking"]["name"] == "Сан Сити"
    assert resp.json["parking"]["count_available_places"] == 8


def test_post_not_parkings(client):
    """Testing the parking by "id" and url address /parkings/3"""

    resp = client.get("/parkings/3")
    assert resp.status_code == 404
    assert "Not found" in resp.json


def test_close_parking(client):
    """Testing of closed parking"""

    data = {"client_id": 1, "parking_id": 2}
    arrival = client.post("/client_parkings", json=data)
    assert arrival.status_code == 404
    assert "No place" in arrival.json


def test_arrival_on_parking(client):
    """
    Method POST
    Testing the arrival parking.
    Initially free parking spaces (Parking.count_available_places) = 8
    """

    data = {"client_id": 1, "parking_id": 1}
    arrival = client.post("/client_parkings", json=data)
    assert arrival.status_code == 201
    assert arrival.json["client"]["parking"]["count_available_places"] == 7
    # сомнительная проверка
    assert arrival.json["arrival"]["time_in"] == datetime.today().strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )


def test_not_client_card(client):
    """The test for the absence of a billing account"""

    data = {"client_id": 2, "parking_id": 1}
    arrival = client.post("/client_parkings", json=data)
    assert arrival.status_code == 404
    assert "Link the card to your account" in arrival.json


def test_departure_on_parking(client):
    """
    Method DELETE
    Testing departure from the parking lot.
    Initially free parking spaces (Parking.count_available_places) = 8
    """

    data = {"client_id": 1, "parking_id": 1}
    departure = client.delete("/client_parkings", json=data)
    assert departure.status_code == 201
    assert departure.json["departure"]["parking"]["count_available_places"] == 9
    assert departure.json["departure"]["payment"]


def test_departure_not_client_parking(client):
    """Checking for errors when paying for parking"""

    data = {"client_id": 2, "parking_id": 1}
    departure = client.delete("/client_parkings", json=data)
    assert departure.status_code == 404
    assert "Not available" in departure.json


def test_check_out_without_check_in_parking(client):
    """Checking the exit from the parking lot without check-in"""

    data = {"client_id": 1, "parking_id": 2}
    departure = client.delete("/client_parkings", json=data)
    assert departure.status_code == 404
    assert "The client did not enter the parking lot" in departure.json


def test_to_another_methods_other_post_delete(client):
    """Checking for methods other than "POST" and "DELETE" """

    data = {"client_id": 1, "parking_id": 1}
    departure = client.get("/client_parkings", json=data)
    assert departure.status_code == 405


@pytest.mark.parametrize("route", ["/", "/clients", "/parkings"])
def test_route_status_method_get(client, route):
    """Checking paths for get requests"""
    route_status = client.get(route)
    assert route_status.status_code == 200
