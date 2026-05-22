# GET /api/occupazione, restituisce i dati grezzi di occupazione filtrati per anno.
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Occupazione, Regione
from app.schemas import DatoRegionaleOut

router = APIRouter(prefix="/api/occupazione", tags=["occupazione"])


@router.get("", response_model=list[DatoRegionaleOut])
def list_occupazione(
    da_anno: int = Query(..., ge=1900, le=2100, description="Anno iniziale (incluso)"),
    a_anno: int = Query(..., ge=1900, le=2100, description="Anno finale (incluso)"),
    db: Session = Depends(get_db),
):
    if a_anno < da_anno:
        raise HTTPException(status_code=400, detail="a_anno deve essere >= da_anno")
    q = (
        db.query(Occupazione, Regione)
        .join(Regione, Regione.id == Occupazione.regione_id)
        .filter(Occupazione.anno >= da_anno, Occupazione.anno <= a_anno)
        .order_by(Regione.nome, Occupazione.anno)
    )
    return [
        DatoRegionaleOut(
            regione=r.nome,
            area=r.area,
            anno=o.anno,
            valore=o.valore,
            interpolato=o.interpolato,
        )
        for o, r in q.all()
    ]
