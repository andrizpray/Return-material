from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import ReturnMaterial, ReturnReason
from fastapi.templating import Jinja2Templates
from app.templates import TEMPLATE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATE_DIR)


@router.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    total = db.query(func.count(ReturnMaterial.id)).scalar() or 0
    pending = db.query(func.count(ReturnMaterial.id)).filter(
        ReturnMaterial.status == "pending"
    ).scalar() or 0
    approved = db.query(func.count(ReturnMaterial.id)).filter(
        ReturnMaterial.status == "approved"
    ).scalar() or 0
    processed = db.query(func.count(ReturnMaterial.id)).filter(
        ReturnMaterial.status == "processed"
    ).scalar() or 0

    recent = (
        db.query(ReturnMaterial)
        .order_by(ReturnMaterial.created_at.desc())
        .limit(10)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "pages/dashboard.html",
        {
            "active_page": "dashboard",
            "stats": {
                "total": total,
                "pending": pending,
                "approved": approved,
                "processed": processed,
            },
            "recent_returns": recent,
        },
    )
