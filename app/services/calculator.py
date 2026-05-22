# Calcola le 5 serie statistiche aggregate e le salva nella tabella serie_calcolate.
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from app.constants import AREE
from app.database import SessionLocal
from app.models import Importanza, Occupazione, Produttivita, Regione, SerieCalcolata


def media_per_anno(coppie: Iterable[tuple[int, float]]) -> dict[int, float]:
    # media aritmetica semplice, non ponderata (come da nota metodologica della commessa)
    accum: dict[int, list[float]] = defaultdict(list)
    for anno, valore in coppie:
        accum[anno].append(valore)
    return {anno: sum(vs) / len(vs) for anno, vs in accum.items() if vs}


def somma_per_anno(coppie: Iterable[tuple[int, float]]) -> dict[int, float]:
    # somma totale per anno (usata per la produttività in migliaia di euro)
    accum: dict[int, float] = defaultdict(float)
    conteggio: dict[int, int] = defaultdict(int)
    for anno, valore in coppie:
        accum[anno] += valore
        conteggio[anno] += 1
    return {anno: accum[anno] for anno in accum if conteggio[anno] > 0}


def _persisti_serie(db, tipo_serie: str, dati: dict[int, float], area: str | None = None) -> int:
    n = 0
    for anno, valore in dati.items():
        esiste = (
            db.query(SerieCalcolata)
            .filter_by(tipo_serie=tipo_serie, area=area, anno=anno)
            .first()
        )
        if esiste:
            esiste.valore = valore
        else:
            db.add(SerieCalcolata(tipo_serie=tipo_serie, area=area, anno=anno, valore=valore))
            n += 1
    db.commit()
    return n


def _serie_per_area_somma(db, ModelCls, tipo_serie: str) -> int:
    totale = 0
    for area in AREE:
        coppie = (
            db.query(ModelCls.anno, ModelCls.valore)
            .join(Regione, Regione.id == ModelCls.regione_id)
            .filter(Regione.area == area)
            .all()
        )
        dati = somma_per_anno(coppie)
        totale += _persisti_serie(db, tipo_serie, dati, area=area)
    return totale


def _serie_nazionale_somma(db, ModelCls, tipo_serie: str) -> int:
    coppie = db.query(ModelCls.anno, ModelCls.valore).all()
    dati = somma_per_anno(coppie)
    return _persisti_serie(db, tipo_serie, dati, area=None)


def _serie_per_area_media(db, ModelCls, tipo_serie: str) -> int:
    totale = 0
    for area in AREE:
        coppie = (
            db.query(ModelCls.anno, ModelCls.valore)
            .join(Regione, Regione.id == ModelCls.regione_id)
            .filter(Regione.area == area)
            .all()
        )
        dati = media_per_anno(coppie)
        totale += _persisti_serie(db, tipo_serie, dati, area=area)
    return totale


def _serie_nazionale_media(db, ModelCls, tipo_serie: str) -> int:
    coppie = db.query(ModelCls.anno, ModelCls.valore).all()
    dati = media_per_anno(coppie)
    return _persisti_serie(db, tipo_serie, dati, area=None)


def run_calculate() -> None:
    with SessionLocal() as db:
        db.query(SerieCalcolata).delete()
        db.commit()

        n1 = _serie_per_area_somma(db, Produttivita, "PROD_AREA")
        n2 = _serie_nazionale_somma(db, Produttivita, "PROD_NAZ")
        n3 = _serie_per_area_media(db, Importanza, "IMP_AREA")
        n4 = _serie_nazionale_media(db, Occupazione, "OCC_NAZ")
        n5 = _serie_per_area_media(db, Occupazione, "OCC_AREA")

        print(f"Serie calcolate:")
        print(f"  PROD_AREA  (produttività per area, somma)  : {n1} righe")
        print(f"  PROD_NAZ   (produttività nazionale, somma) : {n2} righe")
        print(f"  IMP_AREA   (importanza per area, media)    : {n3} righe")
        print(f"  OCC_NAZ    (occupazione nazionale, media)  : {n4} righe")
        print(f"  OCC_AREA   (occupazione per area, media)   : {n5} righe")
