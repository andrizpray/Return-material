from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import ReturnMaterial, ReturnReason, ReturnAttachment, AuditLog
from app.config import get_settings
from fastapi.templating import Jinja2Templates
from app.templates import TEMPLATE_DIR
import os, uuid

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATE_DIR)
settings = get_settings()


@router.get("/")
async def list_returns(
    request: Request,
    status: str = None,
    reason_id: int = None,
    search: str = None,
    page: int = 1,
    db: Session = Depends(get_db),
):
    query = db.query(ReturnMaterial)
    if status:
        query = query.filter(ReturnMaterial.status == status)
    if reason_id:
        query = query.filter(ReturnMaterial.reason_id == reason_id)
    if search:
        query = query.filter(ReturnMaterial.lot_ref.ilike(f"%{search}%"))

    total = query.count()
    per_page = 20
    returns_list = (
        query.order_by(ReturnMaterial.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    reasons = db.query(ReturnReason).all()
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse(
        request,
        "pages/returns.html",
        {
            "active_page": "returns",
            "returns": returns_list,
            "reasons": reasons,
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "status_filter": status,
            "reason_filter": reason_id,
            "search": search,
        },
    )


@router.get("/{return_id}")
async def detail_return(request: Request, return_id: int, db: Session = Depends(get_db)):
    ret = db.query(ReturnMaterial).filter(ReturnMaterial.id == return_id).first()
    if not ret:
        return RedirectResponse("/returns/", status_code=303)
    reasons = db.query(ReturnReason).all()
    return templates.TemplateResponse(
        request,
        "pages/return_detail.html",
        {"active_page": "returns", "return": ret, "reasons": reasons},
    )


@router.post("/create")
async def create_return(
    lot_ref: str = Form(...),
    qty: float = Form(...),
    reason_id: int = Form(...),
    condition: str = Form(""),
    note: str = Form(""),
    db: Session = Depends(get_db),
):
    ret = ReturnMaterial(
        lot_ref=lot_ref, qty=qty, reason_id=reason_id,
        condition=condition, note=note, status="pending",
    )
    db.add(ret)
    db.flush()
    log = AuditLog(return_id=ret.id, action="created", note="Return submitted")
    db.add(log)
    db.commit()
    return RedirectResponse("/returns/", status_code=303)


@router.post("/{return_id}/status")
async def update_status(
    return_id: int,
    action: str = Form(...),
    destination: str = Form(""),
    note: str = Form(""),
    db: Session = Depends(get_db),
):
    ret = db.query(ReturnMaterial).filter(ReturnMaterial.id == return_id).first()
    if not ret:
        return RedirectResponse("/returns/", status_code=303)

    transitions = {"approve": "approved", "reject": "rejected", "process": "processed"}
    new_status = transitions.get(action)
    if new_status:
        ret.status = new_status
        if new_status == "approved" and destination:
            ret.destination = destination
        log = AuditLog(
            return_id=ret.id,
            action=f"status_{new_status}",
            note=note or f"Status changed to {new_status}",
        )
        db.add(log)
        db.commit()
    return RedirectResponse("/returns/", status_code=303)


@router.post("/{return_id}/upload")
async def upload_attachment(
    return_id: int, file: UploadFile = File(...), db: Session = Depends(get_db),
):
    ret = db.query(ReturnMaterial).filter(ReturnMaterial.id == return_id).first()
    if not ret:
        return RedirectResponse("/returns/", status_code=303)

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    att = ReturnAttachment(return_id=ret.id, file_path=filename, original_name=file.filename)
    db.add(att)
    db.commit()
    return RedirectResponse(f"/returns/{return_id}", status_code=303)
