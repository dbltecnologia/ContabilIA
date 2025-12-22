from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    referencia = Column(String(50), unique=True, index=True, nullable=False)
    external_id = Column(String(100), index=True)
    type = Column(String(20), default="nfse", index=True) # nfse, nfe, nfce, cte, mdfe
    status = Column(String(20), default="processing")
    payload = Column(JSON)
    response_data = Column(JSON)
    pdf_url = Column(String(255))
    xml_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), default="focusnfe")
    payload = Column(JSON)
    received_at = Column(DateTime, default=datetime.utcnow)
