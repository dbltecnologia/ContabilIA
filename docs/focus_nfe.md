# Documentação FocusNFE Hub

Este módulo funciona como um Hub central para emissão e gestão de documentos fiscais eletrônicos via API FocusNFE v2.

## Funcionalidades Implementadas

### Documentos Suportados
- **NFSe**: Serviço (incluindo padrão nacional).
- **NFe**: Produto (emissão, cancelamento, CCe).
- **NFCe**: Consumidor final (varejo).
- **CTe**: Transporte.
- **MDFe**: Manifesto de documentos.

### Diferenciais do Hub
1. **Multi-Cliente**: Use o header `X-Focus-Token` para emitir notas de diferentes clientes em uma única instância do servidor.
2. **Automação de Backup**: O sistema baixa automaticamente o PDF e o XML assim que a nota é autorizada pela SEFAZ via Webhook.
3. **Persistência Local**: Todas as notas e retornos são salvos em um banco de dados local para consulta rápida sem depender da API externa.

## Como Usar

### Emissão (Exemplo NFe)
```http
POST /nfse/nfe/?ref=CLIENTE_ID_123
X-Focus-Token: SEU_TOKEN_AQUI
Content-Type: application/json

{ ... dados da nota ... }
```

### Consulta de Dados Locais
Para sua aplicação cliente recuperar os dados salvos (status, caminhos de arquivo, payload original):
```http
GET /nfse/local/CLIENTE_ID_123
```

## Estrutura de Arquivos
Os documentos baixados são organizados em:
`storage/invoices/{referencia}/{referencia}.pdf`
`storage/invoices/{referencia}/{referencia}.xml`
