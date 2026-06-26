from datetime import datetime
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_hex
from sqlalchemy import (
    Column, Integer, String, Text, DECIMAL, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base


def hash_password(password: str, salt: str = None) -> str:
    """Return 'salt:hash' using PBKDF2-HMAC-SHA256. Stdlib, no deps."""
    if not salt:
        salt = token_hex(16)
    h = pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return f"{salt}:{h.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, _ = stored.split(":", 1)
    return compare_digest(hash_password(password, salt), stored)


class ReturnReason(Base):
    __tablename__ = "return_reasons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    returns = relationship("ReturnMaterial", back_populates="reason")


class ReturnMaterial(Base):
    __tablename__ = "return_materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_ref = Column(String(100), nullable=False, index=True)
    qty = Column(DECIMAL(10, 2), nullable=False)
    reason_id = Column(Integer, ForeignKey("return_reasons.id"), nullable=False)
    condition = Column(String(50), nullable=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    destination = Column(String(20), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reason = relationship("ReturnReason", back_populates="returns")
    attachments = relationship(
        "ReturnAttachment", back_populates="return_material", cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="return_material", cascade="all, delete-orphan"
    )


class ReturnAttachment(Base):
    __tablename__ = "return_attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    return_id = Column(
        Integer, ForeignKey("return_materials.id", ondelete="CASCADE"), nullable=False
    )
    file_path = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    return_material = relationship("ReturnMaterial", back_populates="attachments")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    return_id = Column(
        Integer, ForeignKey("return_materials.id", ondelete="CASCADE"), nullable=False
    )
    action = Column(String(100), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    return_material = relationship("ReturnMaterial", back_populates="audit_logs")


class BeritaAcara(Base):
    __tablename__ = "berita_acara"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nomor_bap = Column(String(50), nullable=False)
    tanggal = Column(DateTime, nullable=False, default=datetime.utcnow)
    hal = Column(String(200), default="Broke / Return / Damage Product / Out Spec / Etc")
    ditujukan_kepada = Column(String(100), default="QC")
    cc = Column(String(100), nullable=True)
    no_sj = Column(String(100), nullable=True)
    tanggal_sj = Column(DateTime, nullable=True)
    no_sj_return = Column(String(100), nullable=True)
    customer_name = Column(String(200), nullable=False)
    customer_address = Column(Text, nullable=True)
    admin_delivery = Column(String(100), nullable=True)
    karu_delivery = Column(String(100), nullable=True)
    kabag_scm = Column(String(100), nullable=True)
    sopir_nopol = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship(
        "BeritaAcaraItem", back_populates="berita_acara", cascade="all, delete-orphan"
    )


class BeritaAcaraItem(Base):
    __tablename__ = "berita_acara_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    berita_acara_id = Column(
        Integer, ForeignKey("berita_acara.id", ondelete="CASCADE"), nullable=False
    )
    return_id = Column(
        Integer, ForeignKey("return_materials.id", ondelete="SET NULL"), nullable=True
    )
    lot_id = Column(String(100), nullable=True)
    qty = Column(DECIMAL(10, 2), nullable=True)
    jenis_barang = Column(String(200), nullable=True)
    rew_id = Column(String(100), nullable=True)
    keterangan = Column(Text, nullable=True)

    berita_acara = relationship("BeritaAcara", back_populates="items")
    return_material = relationship("ReturnMaterial")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
