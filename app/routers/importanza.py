# GET /api/importanza, restituisce i dati grezzi di importanza economica filtrati per anno.
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Importanza, Regione
from app.schemas import DatoRegionaleOut

router = APIRouter(prefix="/api/importanza", tags=["importanza economica"])


@router.get("", response_model=list[DatoRegionaleOut])
def list_importanza(
    da_anno: int = Query(..., ge=1900, le=2100, description="Anno iniziale (incluso)"),
    a_anno: int = Query(..., ge=1900, le=2100, description="Anno finale (incluso)"),
    db: Session = Depends(get_db),
):
    if a_anno < da_anno:
        raise HTTPException(status_code=400, detail="a_anno deve essere >= da_anno")
    q = (
        db.query(Importanza, Regione)
        .join(Regione, Regione.id == Importanza.regione_id)
        .filter(Importanza.anno >= da_anno, Importanza.anno <= a_anno)
        .order_by(Regione.nome, Importanza.anno)
    )
    return [
        DatoRegionaleOut(
            regione=r.nome,
            area=r.area,
            anno=x.anno,
            valore=x.valore,
            interpolato=x.interpolato,
        )
        for x, r in q.all()
    ]
