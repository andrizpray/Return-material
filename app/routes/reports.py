from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.database import get_db
from app.models import ReturnMaterial, ReturnReason
from fastapi.templating import Jinja2Templates
from app.templates import TEMPLATE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATE_DIR)


@router.get("/")
async def reports_page(request: Request, db: Session = Depends(get_db)):
    monthly = (
        db.query(
            extract("year", ReturnMaterial.created_at).label("year"),
            extract("month", ReturnMaterial.created_at).label("month"),
            func.count(ReturnMaterial.id).label("count"),
        )
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    top_reasons = (
        db.query(ReturnReason.name, func.count(ReturnMaterial.id).label("count"))
        .join(ReturnMaterial, ReturnReason.id == ReturnMaterial.reason_id)
        .group_by(ReturnReason.name)
        .order_by(func.count(ReturnMaterial.id).desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "pages/reports.html",
        {
            "active_page": "reports",
            "monthly": [
                {"year": int(m.year), "month": int(m.month), "count": m.count}
                for m in monthly
            ],
            "top_reasons": [
                {"name": r.name, "count": r.count} for r in top_reasons
            ],
        },
    )
