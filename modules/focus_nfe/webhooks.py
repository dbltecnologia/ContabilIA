from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import WebhookLog, Invoice
from .focus_client import FocusNFSeClient
import os
import httpx

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

STORAGE_PATH = "storage/invoices"

def save_document(ref: str, ext: str, content: bytes):
    """Salva o arquivo localmente em uma estrutura organizada."""
    path = os.path.join(STORAGE_PATH, ref)
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, f"{ref}.{ext}")
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path

async def process_focusnfe_webhook(payload: dict, db: Session):
    """
    Processa o webhook da FocusNFE:
    1. Atualiza o status da nota no banco.
    2. Se autorizada, baixa PDF e XML.
    """
    ref = payload.get("ref")
    status = payload.get("status")
    
    # 1. Atualizar Invoice
    invoice = db.query(Invoice).filter(Invoice.referencia == ref).first()
    if invoice:
        invoice.status = status
        invoice.response_data = payload
        
        # 2. Se autorizada, disparar downloads
        if status in ["autorizado", "authorized"]:
            with FocusNFSeClient() as client:
                # PDF
                pdf_res = client.download_document("nfse" if "nfse" in ref.lower() else "nfe", ref, "pdf")
                if pdf_res.status_code == 200:
                    invoice.pdf_url = save_document(ref, "pdf", pdf_res.content)
                
                # XML
                xml_res = client.download_document("nfse" if "nfse" in ref.lower() else "nfe", ref, "xml")
                if xml_res.status_code == 200:
                    invoice.xml_url = save_document(ref, "xml", xml_res.content)
        
        db.commit()

@router.post("/focusnfe")
async def focusnfe_webhook(
    request: Request, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Recebe e processa notificações de status da FocusNFE.
    """
    payload = await request.json()
    
    # Log imediato
    new_log = WebhookLog(payload=payload)
    db.add(new_log)
    db.commit()
    
    # Processamento pesado em background
    background_tasks.add_task(process_focusnfe_webhook, payload, db)
    
    return {"status": "received"}
