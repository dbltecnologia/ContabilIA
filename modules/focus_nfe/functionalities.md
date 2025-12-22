# FocusNFE Functionalities & SDK Analysis

A FocusNFE é uma plataforma robusta para gestão de documentos fiscais eletrônicos (DF-e) no Brasil. Abaixo estão as principais funcionalidades e a análise sobre o uso de bibliotecas.

## Principais Funcionalidades

### 1. Tipos de Documentos Suportados
- **NFSe (Serviço)**: Emissão para centenas de prefeituras com um único padrão.
- **NFe (Produto)**: Vendas entre empresas (B2B), devoluções, etc.
- **NFCe (Consumidor)**: Vendas diretas ao consumidor final (Varejo).
- **CTe (Transporte)**: Conhecimento de Transporte eletrônico.
- **MDFe (Manifesto)**: Manifesto de Documentos Fiscais.
- **NFCom (Comunicação)**: Nota fiscal para serviços de comunicação.

### 2. Operações Auxiliares
- **Cancelamento**: Solicitação de cancelamento de notas conforme regras do SEFAZ/Prefeitura.
- **Consulta de Status**: Verificação em tempo real do processamento da nota.
- **Envio de Checklist/E-mail**: Disparo automático de PDF e XML para o cliente.
- **Cartas de Correção (CCe)**: Correção de campos específicos da NFe/CTe.
- **Inutilização**: Inutilização de numeração não utilizada.

### 3. Gestão e Recebimento
- **NFSe/NFe Recebidas**: Consulta de documentos emitidos contra o CNPJ da empresa (Tomada de serviço/entrada de produtos).
- **Manifestação do Destinatário (MDe)**: Registro de ciência, confirmação ou desconhecimento de operações.

### 4. Integração e Automação
- **Webhooks (Gatilhos)**: Notificações automáticas para o seu servidor quando uma nota é aprovada ou rejeitada.
- **API de CEP**: Consulta de endereços via CEP.
- **Backup de XML/PDF**: Armazenamento em nuvem dos documentos emitidos.

---

## Sobre a Biblioteca (SDK)

### Existe uma Lib Oficial?
**Não existe uma biblioteca oficial da FocusNFE no PyPI (pip) que seja mantida ativamente pela empresa.** 

### Análise: Usar Lib de Terceiros ou Nossa Implementação?
- **Lib de Terceiros**: Existem wrappers criados pela comunidade (como os voltados para Odoo), mas muitas vezes estão desatualizados em relação à API v2.
- **Nossa Implementação (Recomendado)**: O `focus_client.py` que já temos utiliza o `httpx` e segue exatamente os padrões da documentação oficial da FocusNFE. 
    - **Vantagem**: Menos dependências externas, controle total sobre o código e facilidade de manutenção para novas versões da API.
    - **Vantagem**: A própria FocusNFE recomenda o uso direto da API via REST, fornecendo exemplos em Python (Requests/Httpx).

### Sugestão
Podemos manter e expandir nosso cliente atual (`focus_client.py`) para suportar os outros tipos de notas conforme necessário. Ele já está operando com NFSe e pode ser facilmente adaptado para NFe/NFCe seguindo a mesma estrutura de `_request`.
