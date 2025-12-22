# Contabil_IA: Universal Fiscal Hub 🚀

O **Contabil_IA** evoluiu para um servidor de API robusto e centralizado para gestão de documentos fiscais eletrônicos no Brasil. Este hub integra os principais players do mercado (FocusNFE, Domínio/Onvio) e comunicação direta com a SEFAZ, permitindo que qualquer sistema externo emita e gerencie notas de forma simplificada e multi-cliente.

## 🌟 Principais Funcionalidades

### 1. Hub FocusNFE (API v2)
*   **Aparato Total**: Suporte completo para **NFSe, NFe, NFCe, CTe e MDFe**.
*   **Multi-Tenant**: Suporte nativo para múltiplos clientes via header `X-Focus-Token`.
*   **Automação de Backup**: Receiver de Webhooks que baixa automaticamente o **PDF e XML** autorizado para armazenamento local.
*   **Persistência**: Banco de dados SQLite local para rastrear status e payloads.

### 2. Integração Domínio (Onvio/Thomson Reuters)
*   Envio automático de XMLs para processamento contábil.
*   Gatilhos via Firebase Cloud Functions para handoff automatizado.

### 3. Automação SEFAZ Direta
*   Sincronismo via NSU para download de notas emitidas contra o CNPJ.
*   Consulta de status e manifesto do destinatário (MDe).

---

## 📂 Estrutura do Repositório

```text
Contabil_IA/
├── docs/               # Documentação detalhada de cada módulo
├── modules/
│   ├── focus_nfe/      # Core Hub: Router, Models, Schemas, Webhooks
│   ├── dominio/        # Integração Thomson Reuters
│   └── sefaz/          # Comunicação direta via PyNFe
├── scripts/            # Utilitários de linha de comando (CLI)
├── test/               # Scripts de teste e simulação
├── storage/            # Armazenamento local de XMLs e PDFs
├── main.py             # Entrypoint FastAPI
└── ...
```

---

## 🛠️ Instalação e Uso Rápido

1. **Dependências**: `pip install -r requirements.txt`
2. **Configuração**: Renomeie `.env.example` para `.env` e preencha suas chaves.
3. **Servidor**: `uvicorn main:app --reload`
4. **Documentação Interativa (Swagger)**: Acesse `http://localhost:8000/docs`.

### Ferramentas CLI Úteis
*   **Emitir Nota**: `python scripts/focus_emit.py nfe REF_001 payload.json`
*   **Sincronizar SEFAZ**: `python scripts/sefaz_sync.py --sync`

---

## 📖 Documentação Detalhada
Confira os guias na pasta `docs/`:
- [Guia FocusNFE Hub](docs/focus_nfe.md)
- [Guia Integração Domínio](docs/dominio.md)
- [Guia Módulo SEFAZ](docs/sefaz.md)
