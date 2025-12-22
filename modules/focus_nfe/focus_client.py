from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Union

import httpx

DEFAULT_BASE_URLS = {
    "producao": "https://api.focusnfe.com.br",
    "homologacao": "https://homologacao.focusnfe.com.br",
}

def _load_dotenv_if_present(path: str = ".env") -> None:
    """
    Loader mínimo de `.env` (sem dependências) para facilitar testes locais.
    - Não sobrescreve variáveis já definidas em `os.environ`.
    - Suporta linhas `KEY=VALUE` com aspas simples/duplas.
    """
    if not os.path.exists(path):
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if not key:
                    continue
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                os.environ.setdefault(key, value)
    except OSError:
        return


@dataclass
class FocusNFSeResponse:
    status_code: int
    body: Union[Dict[str, Any], List[Any], str, None]
    headers: Mapping[str, str]
    ok: bool

    @classmethod
    def from_httpx(cls, response: httpx.Response) -> "FocusNFSeResponse":
        try:
            body = response.json()
        except ValueError:
            body = response.text
        return cls(
            status_code=response.status_code,
            body=body,
            headers=response.headers,
            ok=response.is_success,
        )


class FocusNFSeClient:
    """Cliente base para trabalhar com NFSe na API Focus NFe v2."""

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        environment: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        if token is None and not os.environ.get("FOCUS_NFE_TOKEN"):
            _load_dotenv_if_present(".env")

        self.token = token or os.environ.get("FOCUS_NFE_TOKEN")
        if not self.token:
            raise RuntimeError("FOCUS_NFE_TOKEN must be set for Focus requests.")

        self.base_url = (
            base_url
            or os.environ.get("FOCUS_NFE_BASE_URL")
            or DEFAULT_BASE_URLS.get(
                (environment or os.environ.get("FOCUS_NFE_ENV", "homologacao")).lower(),
                DEFAULT_BASE_URLS["homologacao"],
            )
        )
        self.timeout = timeout
        self._init_client()

    def _init_client(self) -> None:
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            auth=httpx.BasicAuth(self.token, ""),
            headers={"Content-Type": "application/json"},
        )

    def set_token(self, token: str) -> None:
        """Atualiza o token de autenticação para as próximas requisições."""
        self.token = token
        self._client.auth = httpx.BasicAuth(token, "")

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> FocusNFSeResponse:
        response = self._client.request(
            method,
            endpoint,
            params=params,
            json=json,
        )
        return FocusNFSeResponse.from_httpx(response)

    # ----------------------
    # Helpers genéricos (v2)
    # ----------------------
    def create_document(self, doc_type: str, referencia: str, payload: Dict[str, Any]) -> FocusNFSeResponse:
        params = {"ref": referencia}
        return self._request("POST", f"/v2/{doc_type}", params=params, json=payload)

    def get_document(self, doc_type: str, referencia: str, *, completa: Optional[int] = None) -> FocusNFSeResponse:
        params: Dict[str, Any] = {}
        if completa is not None:
            params["completa"] = completa
        return self._request("GET", f"/v2/{doc_type}/{referencia}", params=params or None)

    def download_document(self, doc_type: str, referencia: str, ext: str) -> httpx.Response:
        ext = ext.lstrip(".").lower()
        return self._client.request("GET", f"/v2/{doc_type}/{referencia}.{ext}")

    # ----------------------
    # NFSe (conveniências)
    # ----------------------
    def consultar_municipio(self, codigo_ibge: str) -> FocusNFSeResponse:
        """Retorna os requisitos do município para emissão de NFSe."""
        return self._request("GET", f"/v2/municipios/{codigo_ibge}")

    def emitir_nfse(self, referencia: str, dados_nota: Dict[str, Any]) -> FocusNFSeResponse:
        """Envia a NFSe para a fila da Focus com o ref definido."""
        return self.create_document("nfse", referencia, dados_nota)

    def emitir_nfse_nacional(self, referencia: str, dados: Dict[str, Any]) -> FocusNFSeResponse:
        """Emite NFSe no padrão nacional (nfsen)."""
        return self.create_document("nfsen", referencia, dados)

    def consultar_nfse_nacional(self, referencia: str) -> FocusNFSeResponse:
        """Consulta completa de NFSe Nacional."""
        return self.get_document("nfsen", referencia, completa=1)

    def cancelar_nfse_nacional(self, referencia: str, justificativa: str) -> FocusNFSeResponse:
        """Cancela uma NFSe Nacional."""
        if len(justificativa or "") < 15:
            raise ValueError("Justificativa deve ter no mínimo 15 caracteres.")
        payload = {"justificativa": justificativa}
        return self._request("DELETE", f"/v2/nfsen/{referencia}", json=payload)

    def consultar_nfse(self, referencia: str) -> FocusNFSeResponse:
        """Consulta completa da NFSe (PDF, XML e status)."""
        return self.get_document("nfse", referencia, completa=1)

    def cancelar_nfse(self, referencia: str, justificativa: str) -> FocusNFSeResponse:
        """Cancela uma NFSe com justificativa mínima."""
        if len(justificativa or "") < 15:
            raise ValueError("Justificativa deve ter no mínimo 15 caracteres.")
        payload = {"justificativa": justificativa}
        return self._request("DELETE", f"/v2/nfse/{referencia}", json=payload)

    def enviar_email_nfse(self, referencia: str, emails: List[str]) -> FocusNFSeResponse:
        """Solicita o envio do PDF da NFSe para os e-mails informados."""
        payload = {"emails": emails}
        return self._request("POST", f"/v2/nfse/{referencia}/email", json=payload)

    def consultar_nfses_recebidas(self, cnpj: str) -> FocusNFSeResponse:
        """Retorna as NFSe onde o CNPJ informado é o tomador."""
        params = {"cnpj": cnpj}
        return self._request("GET", "/v2/nfses_recebidas", params=params)

    def enviar_lote_rps(self, referencia: str, lote_dados: Dict[str, Any]) -> FocusNFSeResponse:
        """Envia lote de RPS para prefeituras que usam envio por arquivo."""
        return self.create_document("lotes_rps", referencia, lote_dados)

    def consultar_lote_rps(self, referencia: str) -> FocusNFSeResponse:
        """Consulta o retorno do lote de RPS enviado à Focus."""
        return self._request("GET", f"/v2/lotes_rps/{referencia}")

    def registrar_webhook(self, event: str, url: str) -> FocusNFSeResponse:
        """Registra um hook que notifica nossa API quando o status mudar."""
        payload = {"event": event, "url": url}
        return self._request("POST", "/v2/hooks", json=payload)

    def list_documents(self, doc_type: str, params: Optional[Dict[str, Any]] = None) -> FocusNFSeResponse:
        """Lista os documentos de um determinado tipo com filtros opcionais."""
        return self._request("GET", f"/v2/{doc_type}", params=params)

    def listar_nfse(
        self,
        cnpj_prestador: Optional[str] = None,
        data_inicial: Optional[str] = None,
        data_final: Optional[str] = None,
        status: Optional[str] = None,
    ) -> FocusNFSeResponse:
        """Lista as NFSe emitidas com filtros de busca."""
        params = {}
        if cnpj_prestador: params["cnpj_prestador"] = cnpj_prestador
        if data_inicial: params["data_inicial"] = data_inicial
        if data_final: params["data_final"] = data_final
        if status: params["status"] = status
        return self.list_documents("nfse", params=params)

    # ----------------------
    # NFe (Produtos)
    # ----------------------
    def emitir_nfe(self, referencia: str, dados_nfe: Dict[str, Any]) -> FocusNFSeResponse:
        """Envia a NFe para processamento."""
        return self.create_document("nfe", referencia, dados_nfe)

    def consultar_nfe(self, referencia: str) -> FocusNFSeResponse:
        """Consulta completa da NFe."""
        return self.get_document("nfe", referencia, completa=1)

    def cancelar_nfe(self, referencia: str, justificativa: str) -> FocusNFSeResponse:
        """Cancela uma NFe autorizada."""
        if len(justificativa or "") < 15:
            raise ValueError("Justificativa deve ter no mínimo 15 caracteres.")
        payload = {"justificativa": justificativa}
        return self._request("DELETE", f"/v2/nfe/{referencia}", json=payload)

    def enviar_email_nfe(self, referencia: str, emails: List[str]) -> FocusNFSeResponse:
        """Envia DANFe e XML da NFe por e-mail."""
        payload = {"emails": emails}
        return self._request("POST", f"/v2/nfe/{referencia}/email", json=payload)

    def carta_correcao_nfe(self, referencia: str, texto_correcao: str) -> FocusNFSeResponse:
        """Envia uma Carta de Correção Eletrônica (CC-e) para a NFe."""
        if len(texto_correcao or "") < 15:
            raise ValueError("Correção deve ter no mínimo 15 caracteres.")
        payload = {"correcao": texto_correcao}
        return self._request("POST", f"/v2/nfe/{referencia}/carta_correcao", json=payload)

    # ----------------------
    # Documentos Recebidos (Entrada) & MDe
    # ----------------------
    def consultar_nfe_recebidas(self, cnpj: str, **kwargs) -> FocusNFSeResponse:
        """Consulta as NFe emitidas contra o CNPJ informado."""
        params = {"cnpj": cnpj, **kwargs}
        return self._request("GET", "/v2/nfe_recebidas", params=params)

    def manifestar_nfe(self, chave_nfe: str, tipo: str, justificativa: Optional[str] = None) -> FocusNFSeResponse:
        """
        Realiza a Manifestação do Destinatário (MDe).
        Tipos: ciencia, confirmacao, desconhecimento, operacao_nao_realizada
        """
        payload = {"tipo": tipo}
        if justificativa:
            payload["justificativa"] = justificativa
        return self._request("POST", f"/v2/nfe/{chave_nfe}/manifestar", json=payload)

    # ----------------------
    # CTe (Transporte)
    # ----------------------
    def emitir_cte(self, referencia: str, dados_cte: Dict[str, Any]) -> FocusNFSeResponse:
        """Envia o CTe para processamento."""
        return self.create_document("cte", referencia, dados_cte)

    def consultar_cte(self, referencia: str) -> FocusNFSeResponse:
        """Consulta completa do CTe."""
        return self.get_document("cte", referencia, completa=1)

    def cancelar_cte(self, referencia: str, justificativa: str) -> FocusNFSeResponse:
        """Cancela um CTe autorizado."""
        if len(justificativa or "") < 15:
            raise ValueError("Justificativa deve ter no mínimo 15 caracteres.")
        payload = {"justificativa": justificativa}
        return self._request("DELETE", f"/v2/cte/{referencia}", json=payload)

    # ----------------------
    # MDFe (Manifesto)
    # ----------------------
    def emitir_mdfe(self, referencia: str, dados_mdfe: Dict[str, Any]) -> FocusNFSeResponse:
        """Envia o MDFe para processamento."""
        return self.create_document("mdfe", referencia, dados_mdfe)

    def consultar_mdfe(self, referencia: str) -> FocusNFSeResponse:
        """Consulta completa do MDFe."""
        return self.get_document("mdfe", referencia, completa=1)

    def encerrar_mdfe(self, referencia: str, codigo_municipio: str) -> FocusNFSeResponse:
        """Encerra um MDFe autorizado informando o município de encerramento."""
        payload = {"fechamento_municipio": codigo_municipio}
        return self._request("POST", f"/v2/mdfe/{referencia}/encerrar", json=payload)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "FocusNFSeClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


FocusNFeResponse = FocusNFSeResponse
FocusNFeClient = FocusNFSeClient
