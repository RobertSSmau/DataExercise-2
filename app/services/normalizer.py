# Riempie i buchi temporali con interpolazione lineare per ogni regione.
from __future__ import annotations

from app.database import SessionLocal
from app.models import Produttivita, Occupazione, Importanza


def interpola_per_regione(serie: dict[int, float]) -> dict[int, tuple[float, bool]]:
    if len(serie) < 2:
        return {a: (v, False) for a, v in serie.items()}

    anni_noti = sorted(serie)
    out: dict[int, tuple[float, bool]] = {a: (serie[a], False) for a in anni_noti}

    for i in range(len(anni_noti) - 1):
        a0, a1 = anni_noti[i], anni_noti[i + 1]
        gap = a1 - a0
        if gap <= 1:
            continue
        v0, v1 = serie[a0], serie[a1]
        passo = (v1 - v0) / gap
        # aggiunge gli anni mancanti tra a0 e a1 con incremento lineare
        for k in range(1, gap):
            out[a0 + k] = (v0 + passo * k, True)

    return out


def _normalizza_tabella(ModelCls, db) -> int:
    rows = db.query(ModelCls).all()
    per_regione: dict[int, dict[int, float]] = {}
    for r in rows:
        per_regione.setdefault(r.regione_id, {})[r.anno] = r.valore

    inseriti = 0
    for regione_id, serie in per_regione.items():
        interpolata = interpola_per_regione(serie)
        for anno, (valore, flag) in interpolata.items():
            if not flag:
                continue
            esiste = db.query(ModelCls).filter_by(regione_id=regione_id, anno=anno).first()
            if esiste:
                continue
            db.add(ModelCls(regione_id=regione_id, anno=anno, valore=valore, interpolato=True))
            inseriti += 1
    db.commit()
    return inseriti


def run_normalize() -> None:
    with SessionLocal() as db:
        for ModelCls in (Produttivita, Occupazione, Importanza):
            n = _normalizza_tabella(ModelCls, db)
            print(f"{ModelCls.__tablename__}: aggiunti {n} record interpolati")
