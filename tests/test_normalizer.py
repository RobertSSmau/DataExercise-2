from app.services.normalizer import interpola_per_regione


def test_interpolazione_due_buchi_consecutivi():
    # 2001->10, 2004->16; mancano 2002 e 2003
    # passo = (16-10)/3 = 2 => 2002=12, 2003=14
    serie = {2001: 10.0, 2004: 16.0}
    out = interpola_per_regione(serie)
    assert out[2001] == (10.0, False)
    assert abs(out[2002][0] - 12.0) < 1e-9
    assert out[2002][1] is True
    assert abs(out[2003][0] - 14.0) < 1e-9
    assert out[2003][1] is True
    assert out[2004] == (16.0, False)


def test_nessun_buco():
    serie = {2010: 5.0, 2011: 6.0, 2012: 7.0}
    out = interpola_per_regione(serie)
    assert all(not flag for _, flag in out.values())


def test_meno_di_due_punti_no_op():
    assert interpola_per_regione({2020: 1.0}) == {2020: (1.0, False)}
    assert interpola_per_regione({}) == {}


def test_buco_singolo():
    serie = {2000: 0.0, 2002: 4.0}
    out = interpola_per_regione(serie)
    assert abs(out[2001][0] - 2.0) < 1e-9
    assert out[2001][1] is True
