# GET /api/produttivita, restituisce i dati grezzi di produttività filtrati per anno.
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Produttivita, Regione
from app.schemas import DatoRegionaleOut

router = APIRouter(prefix="/api/produttivita", tags=["produttività"])


@router.get("", response_model=list[DatoRegionaleOut])
def list_produttivita(
    da_anno: int = Query(..., ge=1900, le=2100, description="Anno iniziale (incluso)"),
    a_anno: int = Query(..., ge=1900, le=2100, description="Anno finale (incluso)"),
    db: Session = Depends(get_db),
):
    if a_anno < da_anno:
        raise HTTPException(status_code=400, detail="a_anno deve essere >= da_anno")
    q = (
        db.query(Produttivita, Regione)
        .join(Regione, Regione.id == Produttivita.regione_id)
        .filter(Produttivita.anno >= da_anno, Produttivita.anno <= a_anno)
        .order_by(Regione.nome, Produttivita.anno)
    )
    return [
        DatoRegionaleOut(
            regione=r.nome,
            area=r.area,
            anno=p.anno,
            valore=p.valore,
            interpolato=p.interpolato,
        )
        for p, r in q.all()
    ]
