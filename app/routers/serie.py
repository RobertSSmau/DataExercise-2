# Endpoint per le 5 serie statistiche calcolate (produttività, importanza, occupazione).
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SerieCalcolata
from app.schemas import SerieAreaOut, SerieNazionaleOut

router = APIRouter(prefix="/api/serie", tags=["serie calcolate"])


def _valida_range(da_anno: int, a_anno: int) -> None:
    if a_anno < da_anno:
        raise HTTPException(status_code=400, detail="a_anno deve essere >= da_anno")


def _query_area(db: Session, tipo: str, da_anno: int, a_anno: int):
    return (
        db.query(SerieCalcolata)
        .filter(
            SerieCalcolata.tipo_serie == tipo,
            SerieCalcolata.area.isnot(None),
            SerieCalcolata.anno >= da_anno,
            SerieCalcolata.anno <= a_anno,
        )
        .order_by(SerieCalcolata.area, SerieCalcolata.anno)
        .all()
    )


def _query_naz(db: Session, tipo: str, da_anno: int, a_anno: int):
    return (
        db.query(SerieCalcolata)
        .filter(
            SerieCalcolata.tipo_serie == tipo,
            SerieCalcolata.area.is_(None),
            SerieCalcolata.anno >= da_anno,
            SerieCalcolata.anno <= a_anno,
        )
        .order_by(SerieCalcolata.anno)
        .all()
    )


@router.get("/produttivita/aree", response_model=list[SerieAreaOut])
def serie_produttivita_aree(
    da_anno: int = Query(..., ge=1900, le=2100, description="Anno iniziale (incluso)"),
    a_anno: int = Query(..., ge=1900, le=2100, description="Anno finale (incluso)"),
    db: Session = Depends(get_db),
):
    _valida_range(da_anno, a_anno)
    return [
        SerieAreaOut(area=r.area, anno=r.anno, valore=r.valore)
        for r in _query_area(db, "PROD_AREA", da_anno, a_anno)
    ]


@router.get("/produttivita/nazionale", response_model=list[SerieNazionaleOut])
def serie_produttivita_nazionale(
    da_anno: int = Query(..., ge=1900, le=2100, description="Anno iniziale (incluso)"),
    a_anno: int = Query(..., ge=1900, le=2100, description="Anno finale (incluso)"),
    db: Session = Depends(get_db),
):
    _valida_range(da_anno, a_anno)
    return [
        SerieNazionaleOut(anno=r.anno, valore=r.valore)
        for r in _query_naz(db, "PROD_NAZ", da_anno, a_anno)
    ]


@router.get("/importanza/aree", response_model=list[SerieAreaOut])
def serie_importanza_aree(
    da_anno: int = Query(..., ge=1900, le=2100, description="Anno iniziale (incluso)"),
    a_anno: int = Query(..., ge=1900, le=2100, description="Anno finale (incluso)"),
    db: Session = Depends(get_db),
):
    _valida_range(da_anno, a_anno)
    return [
        SerieAreaOut(area=r.area, anno=r.anno, valore=r.valore)
        for r in _query_area(db, "IMP_AREA", da_anno, a_anno)
    ]


@router.get("/occupazione/nazionale", response_model=list[SerieNazionaleOut])
def serie_occupazione_nazionale(
    da_anno: int = Query(..., ge=1900, le=2100, description="Anno iniziale (incluso)"),
    a_anno: int = Query(..., ge=1900, le=2100, description="Anno finale (incluso)"),
    db: Session = Depends(get_db),
):
    _valida_range(da_anno, a_anno)
    return [
        SerieNazionaleOut(anno=r.anno, valore=r.valore)
        for r in _query_naz(db, "OCC_NAZ", da_anno, a_anno)
    ]


@router.get("/occupazione/aree", response_model=list[SerieAreaOut])
def serie_occupazione_aree(
    da_anno: int = Query(..., ge=1900, le=2100, description="Anno iniziale (incluso)"),
    a_anno: int = Query(..., ge=1900, le=2100, description="Anno finale (incluso)"),
    db: Session = Depends(get_db),
):
    _valida_range(da_anno, a_anno)
    return [
        SerieAreaOut(area=r.area, anno=r.anno, valore=r.valore)
        for r in _query_area(db, "OCC_AREA", da_anno, a_anno)
    ]
