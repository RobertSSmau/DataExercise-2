from app.services.calculator import media_per_anno, somma_per_anno


def test_media_per_anno_aggrega():
    valori = [
        (2010, 10.0), (2010, 20.0),
        (2011, 30.0), (2011, 40.0), (2011, 50.0),
        (2012, 100.0),
    ]
    out = media_per_anno(valori)
    assert out == {2010: 15.0, 2011: 40.0, 2012: 100.0}


def test_media_per_anno_vuoto():
    assert media_per_anno([]) == {}


def test_media_per_anno_singolo():
    assert media_per_anno([(2000, 42.0)]) == {2000: 42.0}


def test_somma_per_anno_aggrega():
    valori = [
        (2010, 10.0), (2010, 20.0),
        (2011, 30.0), (2011, 40.0), (2011, 50.0),
        (2012, 100.0),
    ]
    out = somma_per_anno(valori)
    assert out == {2010: 30.0, 2011: 120.0, 2012: 100.0}


def test_somma_per_anno_vuoto():
    assert somma_per_anno([]) == {}


def test_somma_per_anno_singolo():
    assert somma_per_anno([(2000, 42.0)]) == {2000: 42.0}


def test_somma_vs_media_differiscono():
    # con dati multipli, somma e media devono dare risultati diversi
    valori = [(2010, 10.0), (2010, 20.0)]
    assert somma_per_anno(valori)[2010] == 30.0
    assert media_per_anno(valori)[2010] == 15.0
