"""Test di integrazione API.

Usa il database reale (data/esame.db). Su un DB vuoto i test di range-check
(400 su a_anno < da_anno) sono sempre significativi; i test di range valido
restituiscono lista vuota ma verificano comunque lo status 200 e il tipo JSON.
Per risultati completi eseguire prima run_import() + run_normalize() + run_calculate().
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_serves_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_produttivita_range_valido():
    r = client.get("/api/produttivita", params={"da_anno": 2010, "a_anno": 2015})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_produttivita_range_invertito():
    r = client.get("/api/produttivita", params={"da_anno": 2020, "a_anno": 2010})
    assert r.status_code == 400


def test_occupazione_range_valido():
    r = client.get("/api/occupazione", params={"da_anno": 2010, "a_anno": 2015})
    assert r.status_code == 200


def test_importanza_range_valido():
    r = client.get("/api/importanza", params={"da_anno": 2010, "a_anno": 2015})
    assert r.status_code == 200


def test_serie_produttivita_aree():
    r = client.get("/api/serie/produttivita/aree", params={"da_anno": 2010, "a_anno": 2020})
    assert r.status_code == 200


def test_serie_produttivita_nazionale():
    r = client.get("/api/serie/produttivita/nazionale", params={"da_anno": 2010, "a_anno": 2020})
    assert r.status_code == 200


def test_serie_importanza_aree():
    r = client.get("/api/serie/importanza/aree", params={"da_anno": 2010, "a_anno": 2020})
    assert r.status_code == 200


def test_serie_occupazione_nazionale():
    r = client.get("/api/serie/occupazione/nazionale", params={"da_anno": 2010, "a_anno": 2020})
    assert r.status_code == 200


def test_serie_occupazione_aree():
    r = client.get("/api/serie/occupazione/aree", params={"da_anno": 2010, "a_anno": 2020})
    assert r.status_code == 200


def test_serie_range_invertito():
    r = client.get("/api/serie/produttivita/aree", params={"da_anno": 2020, "a_anno": 2010})
    assert r.status_code == 400
