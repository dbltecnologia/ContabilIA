# Documentação Módulo Domínio (Thomson Reuters)

Este módulo é responsável pela integração com a API da Thomson Reuters (Domínio/Onvio), permitindo o envio de arquivos XML de notas fiscais para processamento contábil.

## Componentes Principais

### 1. Cliente de API (`dominio_client.py`)
O cliente encapsula toda a lógica de comunicação com a API Onvio v3:
- **Autenticação**: Gera tokens de acesso OAuth2 usando `clientId` e `clientSecret`.
- **Ativação**: Gerencia a `integrationKey` necessária para o envio.
- **Envio de Lote (`Invoice Batch`)**: Envia arquivos XML de forma individual ou em lote.

### 2. Automação via Cloud Functions (`functions/main.py`)
O sistema possui um gatilho automático no Firebase Firestore (`on_document_created` na coleção `documents/`):
1. Detecta um novo documento com status `PROCESSING`.
2. Recupera as credenciais do cliente (`clientId`/`clientSecret`) do perfil do usuário no Firestore.
3. Baixa o XML do Firebase Storage.
4. Realiza o envio automático para a API do Domínio.
5. Atualiza o status do documento para `SUCCESS` ou `FAILURE` com a resposta detalhada da API.

## Fluxos de Trabalho

### Fluxo Manual (CLI)
Você pode rodar o envio de uma pasta inteira de XMLs localmente:
```python
from modules.dominio.dominio_client import run_manual_api_submission

# Processa todos os XMLs de uma pasta e gera um log JSON de resultados
run_manual_api_submission("caminho/para/meus/xmls")
```

### Fluxo Automático (Web App)
1. O usuário faz upload do XML no frontend.
2. O arquivo vai para o Firebase Storage.
3. Um registro é criado no Firestore.
4. A Cloud Function entra em ação e faz o "handoff" para o Domínio.

## Configuração Necessária (`.env` ou Firestore)
- `MANUAL_CLIENT_ID`: Para envios via CLI.
- `MANUAL_CLIENT_SECRET`: Para envios via CLI.
- No Firestore (coleção `users`): Cada usuário deve ter `clientId` e `clientSecret` configurados para a automação funcionar.
