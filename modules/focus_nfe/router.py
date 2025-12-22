from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import List, Optional
from sqlalchemy.orm import Session
from .focus_client import FocusNFSeClient
from .schemas import (
    NFSeCreate, NFSeResponse, 
    NFeCreate, NFeResponse, 
    MDeRequest,
    NFCeCreate, NFCeResponse,
    CTeCreate, CTeResponse,
    MDFeCreate, MDFeResponse
)
from .database import get_db
from .models import Invoice
import os

router = APIRouter(prefix="/nfse", tags=["NFSe"])

def get_focus_client(x_focus_token: Optional[str] = Header(None, description="Token da Focus NFe para multi-clientes")):
    """
    Injeta o cliente FocusNFE. 
    Se o header X-Focus-Token for enviado, usa ele para autenticação.
    Caso contrário, usa o token padrão do .env.
    """
    client = FocusNFSeClient(token=x_focus_token)
    try:
        yield client
    finally:
        client.close()

# --- NFSe (Serviço) ---

@router.post("/", response_model=NFSeResponse)
async def emit_invoice(
    nfse: NFSeCreate, 
    ref: str, 
    client: FocusNFSeClient = Depends(get_focus_client),
    db: Session = Depends(get_db)
):
    """Emite uma nova NFSe."""
    payload = nfse.dict(exclude_unset=True)
    response = client.emitir_nfse(ref, payload)
    
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    
    db_invoice = Invoice(
        referencia=ref,
        external_id=str(response.body.get("id")) if response.body.get("id") else None,
        type="nfse",
        status=response.body.get("status", "processing"),
        payload=payload,
        response_data=response.body
    )
    db.add(db_invoice)
    db.commit()
    
    return response.body

@router.get("/", response_model=List[NFSeResponse])
async def list_invoices(
    status: Optional[str] = Query(None),
    cnpj_prestador: Optional[str] = Query(None),
    client: FocusNFSeClient = Depends(get_focus_client)
):
    """Lista as últimas NFSe."""
    response = client.listar_nfse(cnpj_prestador=cnpj_prestador, status=status)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

# --- NFe (Produtos) ---

@router.post("/nfe/", response_model=NFeResponse, tags=["NFe"])
async def emit_nfe(
    nfe: NFeCreate, 
    ref: str, 
    client: FocusNFSeClient = Depends(get_focus_client),
    db: Session = Depends(get_db)
):
    """Emite uma nova NFe."""
    payload = nfe.dict(exclude_unset=True)
    response = client.emitir_nfe(ref, payload)
    
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    
    db_invoice = Invoice(
        referencia=ref,
        external_id=str(response.body.get("id")) if response.body.get("id") else None,
        type="nfe",
        status=response.body.get("status", "processing"),
        payload=payload,
        response_data=response.body
    )
    db.add(db_invoice)
    db.commit()
    
    return response.body

# --- NFCe (Varejo) ---

@router.post("/nfce/", response_model=NFCeResponse, tags=["NFCe"])
async def emit_nfce(
    nfce: NFCeCreate, 
    ref: str, 
    client: FocusNFSeClient = Depends(get_focus_client),
    db: Session = Depends(get_db)
):
    """Emite uma nova NFCe (Varejo)."""
    payload = nfce.dict(exclude_unset=True)
    response = client.create_document("nfce", ref, payload)
    
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    
    db_invoice = Invoice(
        referencia=ref,
        external_id=str(response.body.get("id")) if response.body.get("id") else None,
        type="nfce",
        status=response.body.get("status", "processing"),
        payload=payload,
        response_data=response.body
    )
    db.add(db_invoice)
    db.commit()
    
    return response.body

@router.get("/nfe/{ref}", response_model=NFeResponse, tags=["NFe"])
async def get_nfe(ref: str, client: FocusNFSeClient = Depends(get_focus_client)):
    """Consulta detalhes de uma NFe."""
    response = client.consultar_nfe(ref)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

@router.delete("/nfe/{ref}", tags=["NFe"])
async def cancel_nfe(ref: str, justificativa: str, client: FocusNFSeClient = Depends(get_focus_client)):
    """Cancela uma NFe."""
    response = client.cancelar_nfe(ref, justificativa)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

@router.post("/nfe/{ref}/carta_correcao", tags=["NFe"])
async def post_nfe_correcao(ref: str, texto: str, client: FocusNFSeClient = Depends(get_focus_client)):
    """Cria uma Carta de Correção Eletrônica para a NFe."""
    response = client.carta_correcao_nfe(ref, texto)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

# --- Notas Recebidas (Entrada) & MDe ---

@router.get("/recebidos/nfe", tags=["Recebidos"])
async def list_received_nfe(
    cnpj: str, 
    client: FocusNFSeClient = Depends(get_focus_client),
    pagina: int = 1
):
    """Consulta NFe emitidas contra o CNPJ (Notas de Entrada)."""
    response = client.consultar_nfe_recebidas(cnpj, pagina=pagina)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

@router.post("/recebidos/nfe/{chave}/manifestar", tags=["Recebidos"])
async def manifest_received_nfe(
    chave: str, 
    req: MDeRequest, 
    client: FocusNFSeClient = Depends(get_focus_client)
):
    """Realiza a Manifestação do Destinatário (MDe)."""
    response = client.manifestar_nfe(chave, req.tipo, req.justificativa)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body

    return response.body

# --- CTe (Transporte) ---

@router.post("/cte/", response_model=CTeResponse, tags=["CTe"])
async def emit_cte(
    cte: CTeCreate, 
    ref: str, 
    client: FocusNFSeClient = Depends(get_focus_client),
    db: Session = Depends(get_db)
):
    """Emite um novo CTe."""
    payload = cte.dict(exclude_unset=True)
    response = client.emitir_cte(ref, payload)
    
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    
    db_invoice = Invoice(
        referencia=ref,
        external_id=str(response.body.get("id")) if response.body.get("id") else None,
        type="cte",
        status=response.body.get("status", "processing"),
        payload=payload,
        response_data=response.body
    )
    db.add(db_invoice)
    db.commit()
    
    return response.body

# --- MDFe (Manifesto) ---

@router.post("/mdfe/", response_model=MDFeResponse, tags=["MDFe"])
async def emit_mdfe(
    mdfe: MDFeCreate, 
    ref: str, 
    client: FocusNFSeClient = Depends(get_focus_client),
    db: Session = Depends(get_db)
):
    """Emite um novo MDFe."""
    payload = mdfe.dict(exclude_unset=True)
    response = client.emitir_mdfe(ref, payload)
    
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    
    db_invoice = Invoice(
        referencia=ref,
        external_id=str(response.body.get("id")) if response.body.get("id") else None,
        type="mdfe",
        status=response.body.get("status", "processing"),
        payload=payload,
        response_data=response.body
    )
    db.add(db_invoice)
    db.commit()
    
    return response.body

@router.get("/local/{ref}", tags=["Local Data"])
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

@router.get("/municipio/{ibge}")
async def check_city_requirements(ibge: str, client: FocusNFSeClient = Depends(get_focus_client)):
    """
    Consulta requisitos municipais para emissão.
    """
    response = client.consultar_municipio(ibge)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.body)
    return response.body
