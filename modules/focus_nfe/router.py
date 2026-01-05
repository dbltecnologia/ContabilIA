from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import List, Optional
from sqlalchemy.orm import Session
from .focus_client import FocusNFeClient
from .schemas import (
    NFSeCreate, NFSeResponse,
    NFeCreate, NFeResponse,
    MDeRequest,
    NFCeCreate, NFCeResponse,
    CTeCreate, CTeResponse,
    MDFeCreate, MDFeResponse
)
from .database import get_db
from .models import Invoice, InvoiceEvent
import os

nfse_router = APIRouter(prefix="/nfse", tags=["NFSe"])
nfe_router = APIRouter(prefix="/nfe", tags=["NFe"])
nfce_router = APIRouter(prefix="/nfce", tags=["NFCe"])
cte_router = APIRouter(prefix="/cte", tags=["CTe"])
mdfe_router = APIRouter(prefix="/mdfe", tags=["MDFe"])
received_router = APIRouter(prefix="/recebidos", tags=["Recebidos"])
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
local_data_router = APIRouter(prefix="/local", tags=["Local Data"])

# Main router for this module
router = APIRouter()

def _save_invoice(db: Session, ref: str, doc_type: str, payload: dict, response: dict) -> Invoice:
    """Cria a nota e o primeiro evento no banco de dados."""
    db_invoice = Invoice(
        referencia=ref,
        external_id=str(response.get("id")) if response.get("id") else None,
        type=doc_type,
        status=response.get("status", "processing"),
        payload=payload,
        response_data=response
    )
    db.add(db_invoice)
    db.flush()
    
    # Registrar evento inicial na timeline
    db.add(InvoiceEvent(
        invoice_id=db_invoice.id,
        status="enviado",
        message=f"{doc_type.upper()} enviada para a FocusNFE",
        data=response
    ))
    db.commit()
    return db_invoice


def get_focus_client(x_focus_token: Optional[str] = Header(None, description="Token da Focus NFe para multi-clientes")):
    """
    Injeta o cliente FocusNFE. 
    Se o header X-Focus-Token for enviado, usa ele para autenticação.
    Caso contrário, usa o token padrão do .env.
    """
    client = FocusNFeClient(token=x_focus_token)
    try:
        yield client
    finally:
        client.close()

# --- NFSe (Serviço) ---

@nfse_router.post("/", response_model=NFSeResponse)
async def emit_invoice(
    nfse: NFSeCreate,
    ref: str,
    client: FocusNFeClient = Depends(get_focus_client),
    db: Session = Depends(get_db)
):
    """Emite uma nova NFSe."""
    payload = nfse.dict(exclude_unset=True)
    response = client.emitir_nfse(ref, payload)
    
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    
    _save_invoice(db, ref, "nfse", payload, response.body)
    
    return response.body

@nfse_router.get("/", response_model=List[NFSeResponse])
async def list_invoices(
    status: Optional[str] = Query(None),
    cnpj_prestador: Optional[str] = Query(None),
    client: FocusNFeClient = Depends(get_focus_client)
):
    """Lista as últimas NFSe."""
    response = client.listar_nfse(cnpj_prestador=cnpj_prestador, status=status)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

@nfse_router.get("/municipio/{ibge}")
async def check_city_requirements(ibge: str, client: FocusNFeClient = Depends(get_focus_client)):
    """
    Consulta requisitos municipais para emissão.
    """
    response = client.consultar_municipio(ibge)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

# --- NFe (Produtos) ---

@nfe_router.post("/", response_model=NFeResponse)
async def emit_nfe(
    nfe: NFeCreate,
    ref: str,
    client: FocusNFeClient = Depends(get_focus_client),
    db: Session = Depends(get_db)
):
    """Emite uma nova NFe."""
    payload = nfe.dict(exclude_unset=True)
    response = client.emitir_nfe(ref, payload)
    
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    
    _save_invoice(db, ref, "nfe", payload, response.body)
    
    return response.body

@nfe_router.get("/{ref}", response_model=NFeResponse)
async def get_nfe(ref: str, client: FocusNFeClient = Depends(get_focus_client)):
    """Consulta detalhes de uma NFe."""
    response = client.consultar_nfe(ref)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

@nfe_router.delete("/{ref}")
async def cancel_nfe(ref: str, justificativa: str, client: FocusNFeClient = Depends(get_focus_client)):
    """Cancela uma NFe."""
    response = client.cancelar_nfe(ref, justificativa)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

@nfe_router.post("/{ref}/carta_correcao")
async def post_nfe_correcao(ref: str, texto: str, client: FocusNFeClient = Depends(get_focus_client)):
    """Cria uma Carta de Correção Eletrônica para a NFe."""
    response = client.carta_correcao_nfe(ref, texto)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

# --- NFCe (Varejo) ---

@nfce_router.post("/", response_model=NFCeResponse)
async def emit_nfce(
    nfce: NFCeCreate,
    ref: str,
    client: FocusNFeClient = Depends(get_focus_client),
    db: Session = Depends(get_db)
):
    """Emite uma nova NFCe (Varejo)."""
    payload = nfce.dict(exclude_unset=True)
    response = client.create_document("nfce", ref, payload)
    
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    
    _save_invoice(db, ref, "nfce", payload, response.body)
    
    return response.body

# --- CTe (Transporte) ---

@cte_router.post("/", response_model=CTeResponse)
async def emit_cte(
    cte: CTeCreate,
    ref: str,
    client: FocusNFeClient = Depends(get_focus_client),
    db: Session = Depends(get_db)
):
    """Emite um novo CTe."""
    payload = cte.dict(exclude_unset=True)
    response = client.emitir_cte(ref, payload)
    
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    
    _save_invoice(db, ref, "cte", payload, response.body)
    
    return response.body

# --- MDFe (Manifesto) ---

@mdfe_router.post("/", response_model=MDFeResponse)
async def emit_mdfe(
    mdfe: MDFeCreate,
    ref: str,
    client: FocusNFeClient = Depends(get_focus_client),
    db: Session = Depends(get_db)
):
    """Emite um novo MDFe."""
    payload = mdfe.dict(exclude_unset=True)
    response = client.emitir_mdfe(ref, payload)
    
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    
    _save_invoice(db, ref, "mdfe", payload, response.body)
    
    return response.body

# --- Notas Recebidas (Entrada) & MDe ---

@received_router.get("/nfe")
async def list_received_nfe(
    cnpj: str,
    client: FocusNFeClient = Depends(get_focus_client),
    pagina: int = 1
):
    """Consulta NFe emitidas contra o CNPJ (Notas de Entrada)."""
    response = client.consultar_nfe_recebidas(cnpj, pagina=pagina)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

@received_router.post("/nfe/{chave}/manifestar")
async def manifest_received_nfe(
    chave: str,
    req: MDeRequest,
    client: FocusNFeClient = Depends(get_focus_client)
):
    """Realiza a Manifestação do Destinatário (MDe)."""
    response = client.manifestar_nfe(chave, req.tipo, req.justificativa)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

# --- Dashboard & Analytics ---

@dashboard_router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Retorna estatísticas rápidas para o Dashboard."""
    from sqlalchemy import func
    stats = db.query(Invoice.status, func.count(Invoice.id)).group_by(Invoice.status).all()
    return {status: count for status, count in stats}

@dashboard_router.get("/list")
async def list_dashboard_invoices(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Lista as últimas notas com informações básicas para o Dashboard."""
    return db.query(Invoice).order_by(Invoice.created_at.desc()).limit(limit).all()

@dashboard_router.get("/{ref}/timeline")
async def get_invoice_timeline(ref: str, db: Session = Depends(get_db)):
    """Retorna a linha do tempo de eventos de uma nota."""
    invoice = db.query(Invoice).filter(Invoice.referencia == ref).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Nota não encontrada.")
    return invoice.events

# --- Local Data ---

@local_data_router.get("/{ref}")
async def get_local_invoice(ref: str, db: Session = Depends(get_db)):
    """
    Retorna os dados da nota armazenados localmente no banco de dados.
    Útil para aplicações clientes recuperarem status e caminhos de arquivos.
    """
    invoice = db.query(Invoice).filter(Invoice.referencia == ref).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Nota não encontrada localmente.")
    
    return {
        "referencia": invoice.referencia,
        "external_id": invoice.external_id,
        "type": invoice.type,
        "status": invoice.status,
        "pdf_path": invoice.pdf_url,
        "xml_path": invoice.xml_url,
        "created_at": invoice.created_at,
        "payload": invoice.payload,
        "response_data": invoice.response_data
    }

router.include_router(nfse_router)
router.include_router(nfe_router)
router.include_router(nfce_router)
router.include_router(cte_router)
router.include_router(mdfe_router)
router.include_router(received_router)
router.include_router(dashboard_router)
router.include_router(local_data_router)
