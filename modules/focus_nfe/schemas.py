from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class Endereco(BaseModel):
    logradouro: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    codigo_municipio: str
    uf: str
    cep: str

class Prestador(BaseModel):
    cnpj: str
    inscricao_municipal: Optional[str] = None
    codigo_municipio: str

class Tomador(BaseModel):
    cnpj: Optional[str] = None
    cpf: Optional[str] = None
    razao_social: str
    email: Optional[EmailStr] = None
    endereco: Endereco

class Servico(BaseModel):
    aliquota: float
    discriminacao: str
    iss_retido: bool = False
    item_lista_servico: str
    codigo_tributacao_municipio: Optional[str] = None
    valor_servicos: float

class NFSeCreate(BaseModel):
    data_emissao: Optional[datetime] = None
    prestador: Prestador
    tomador: Tomador
    servico: Servico

class NFSeResponse(BaseModel):
    status: str
    referencia: str
    id_unico: Optional[str] = Field(None, alias="id")
    pdf_url: Optional[str] = None
    xml_url: Optional[str] = None
    mensagem: Optional[str] = None

# --- NFe (Produtos) ---

class NFeItem(BaseModel):
    numero_item: str
    codigo_produto: str
    descricao: str
    cfop: str
    unidade_comercial: str
    quantidade_comercial: float
    valor_unitario_comercial: float
    valor_bruto: float
    valor_total: float
    ncm: str
    icms_origem: str
    icms_situacao_tributaria: str
    pis_situacao_tributaria: str
    cofins_situacao_tributaria: str

class NFeCreate(BaseModel):
    natureza_operacao: str
    data_emissao: Optional[datetime] = None
    tipo_documento: int = 1 # 0-entrada, 1-saida
    presenca_comprador: int = 1
    items: List[NFeItem]
    prestador: Prestador # Reuso do Prestador (CNPJ/Endereço)
    tomador: Tomador # Reuso do Tomador

class NFeResponse(BaseModel):
    status: str
    referencia: str
    id_unico: Optional[str] = Field(None, alias="id")
    pdf_url: Optional[str] = None
    xml_url: Optional[str] = None
    chave_nfe: Optional[str] = None
    modelo: str = "55"
    serie: str = "1"

# --- MDe & Recebidos ---

class MDeRequest(BaseModel):
    tipo: str = Field(..., description="ciencia, confirmacao, desconhecimento, operacao_nao_realizada")
    justificativa: Optional[str] = None

# --- NFCe (Varejo) ---

class NFCeCreate(NFeCreate):
    """NFCe herda muito da NFe, mas com campos específicos de varejo."""
    pagamentos: List[dict] = Field(..., description="Meios de pagamento (dinheiro, cartão, etc)")

class NFCeResponse(NFeResponse):
    qrcode_url: Optional[str] = None
    url_consulta_nfce: Optional[str] = None

# --- CTe (Transporte) ---

class CTeCreate(BaseModel):
    # Simplificado: CTe tem centenas de campos
    natureza_operacao: str
    cfop: str
    valor_total_servico: float
    remetente: dict
    destinatario: dict
    expedidor: Optional[dict] = None
    recebedor: Optional[dict] = None
    informacoes_carga: dict

class CTeResponse(BaseModel):
    status: str
    referencia: str
    id_unico: Optional[str] = Field(None, alias="id")
    pdf_url: Optional[str] = None
    xml_url: Optional[str] = None

# --- MDFe (Manifesto) ---

class MDFeCreate(BaseModel):
    # Simplificado
    uf_inicio: str
    uf_fim: str
    veiculo: dict
    motorista: dict
    inf_documentos: dict # Chaves de NFe/CTe relacionadas

class MDFeResponse(BaseModel):
    status: str
    referencia: str
    id_unico: Optional[str] = Field(None, alias="id")
    pdf_url: Optional[str] = None
    xml_url: Optional[str] = None
