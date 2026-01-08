# Documentação Técnica: Integração FocusNFE

Esta documentação detalha a integração do sistema com a plataforma **FocusNFE** para emissão de diversos tipos de documentos fiscais eletrônicos.

## 1. Visão Geral
O módulo `focus_nfe` centraliza todas as comunicações com a API v2 da FocusNFE. Ele utiliza um cliente customizado (`FocusNFeClient`) baseado em `httpx` para garantir performance e total controle sobre as requisições.

## 2. Configurações (Ambiente)
As credenciais e URLs base são configuradas via variáveis de ambiente (`.env`):

| Variável | Descrição | Valor Padrão |
| :--- | :--- | :--- |
| `FOCUS_NFE_TOKEN` | Token de autenticação da Focus | (Obrigatório) |
| `FOCUS_NFE_ENV` | Ambiente (`homologacao` ou `producao`) | `homologacao` |
| `FOCUS_NFE_BASE_URL` | URL base personalizada (opcional) | (Padrão Focus) |
| `STORAGE_PATH` | Diretório para salvar XML/PDF | `storage/invoices` |

## 3. Endpoints Disponíveis (API Local)
O sistema expõe routers específicos para cada tipo de documento, facilitando a integração do frontend ou de scripts externos.

### 3.1 NFSe (Serviços) - `/nfse`
- `POST /nfse/?ref={REF}`: Emite uma nova NFSe.
- `GET /nfse/`: Lista NFSe emitidas (suporta filtros `status` e `cnpj_prestador`).
- `GET /nfse/municipio/{ibge}`: Consulta requisitos específicos da prefeitura.

### 3.2 NFe (Produtos) - `/nfe`
- `POST /nfe/?ref={REF}`: Emite uma nova NFe.
- `GET /nfe/{ref}`: Consulta detalhes e status da NFe.
- `DELETE /nfe/{ref}?justificativa={TEXTO}`: Cancela uma NFe autorizada.
- `POST /nfe/{ref}/carta_correcao?texto={TEXTO}`: Envia CC-e (mínimo 15 caracteres).

### 3.3 Outros Documentos
- **NFCe**: `POST /nfce/?ref={REF}`
- **CTe**: `POST /cte/?ref={REF}`
- **MDFe**: `POST /mdfe/?ref={REF}`

### 3.4 Documentos Recebidos (Entrada) - `/recebidos`
- `GET /recebidos/nfe?cnpj={CNPJ}`: Lista notas emitidas contra a empresa.
- `POST /recebidos/nfe/{chave}/manifestar`: Realiza MDe (ciência, confirmação, etc).

### 3.5 Dashboard & Dados Locais - `/dashboard`, `/local`
- `GET /dashboard/stats`: Contagem de notas por status.
- `GET /dashboard/list`: Últimas 50 notas com timestamps.
- `GET /dashboard/{ref}/timeline`: Histórico de eventos da nota (envio, autorização, erro).
- `GET /local/{ref}`: Recupera dados da nota salvos no banco local (incluindo paths dos arquivos).

## 4. Fluxo de Webhooks e Persistência
O sistema utiliza Webhooks para processamento assíncrono, garantindo que o status da nota esteja sempre atualizado localmente.

### Processo:
1. **Recebimento**: FocusNFE envia um POST para `/webhooks/focusnfe`.
2. **Log**: O payload bruto é salvo na tabela `webhook_logs`.
3. **Background Task**:
   - O status é atualizado na tabela `invoices`.
   - Um novo registro é inserido no `invoice_events` (Timeline).
   - **Download Automático**: Se o status for `autorizado`, o sistema baixa o **PDF** e o **XML** da Focus e os salva em `{STORAGE_PATH}/{ref}/`.

## 5. Modelagem de Dados
- `invoices`: Armazena o ID externo, referência, status, e caminhos locais dos arquivos.
- `invoice_events`: Histórico completo de cada estado da nota.

## 7. Suíte de Homologação
Para facilitar os testes e a homologação de novas funcionalidades ou alterações no sistema, uma suíte de scripts foi desenvolvida:

### 7.1 Ferramenta Principal (`scripts/homologate.py`)
Centraliza a execução de todos os testes.
- **Uso**: `python scripts/homologate.py --type [TIPO]`
- **Tipos**: `nfse`, `nfe`, `nfce`, `cte`, `mdfe`, `lifecycle`, `all`

### 7.2 Scripts Individuais (`test/`)
- `test_focus_nfse_emission.py`: Emissão de NFSe.
- `test_focus_nfe_emission.py`: Emissão de NFe.
- `test_focus_nfce_emission.py`: Emissão de NFCe.
- `test_focus_cte_emission.py`: Emissão de CTe.
- `test_focus_mdfe_emission.py`: Emissão de MDFe.
- `test_full_lifecycle.py`: Teste end-to-end (Emissão -> Webhook -> Verificação de Status).

### 7.3 Simulação de Webhooks (`test/simulate_focus_webhook.py`)
Permite testar a reação do sistema a notificações da FocusNFE sem precisar esperar pelo processamento real.

---
**Status atual:** Documentado e homologado com suíte de testes dedicada.
