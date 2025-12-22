# Changelog

## [2.0.0] - 2025-12-22

### Adicionado
- **Hub Universal FocusNFE**: Implementação completa de API para documentos fiscais brasileiros.
  - Suporte total para **NFSe** (incluindo Padrão Nacional), **NFe**, **NFCe**, **CTe** e **MDFe**.
  - Novo endpoint `GET /nfse/local/{ref}` para permitir que sistemas externos recuperem dados persistidos localmente.
- **Suporte Multi-Cliente**: Capacidade de processar requisições para diferentes clientes dinamicamente através do header HTTP `X-Focus-Token`.
- **Automação de Webhooks**: Implementação de receiver para FocusNFE que:
  - Atualiza automaticamente o status no banco de dados local.
  - Baixa e organiza o PDF e XML em background assim que a nota é autorizada pela SEFAZ.
- **Persistência Local**: Integração com SQLAlchemy e SQLite para armazenamento histórico de emissões e logs de webhook.
- **Pasta `docs/`**: Documentação técnica detalhada para os módulos Domínio, FocusNFE e SEFAZ.
- **Scripts Utilitários**: Ferramentas CLI para facilitar a emissão (`focus_emit.py`) e sincronização (`sefaz_sync.py`).

### Alterado
- **Arquitetura de Testes**: Todos os scripts de teste e simulação foram movidos para a pasta dedicada `test/`.
- **Simplificação do .env**: Refatoração do `.env.example` para melhor clareza e separação de responsabilidades.
- **Módulo Domínio**: Melhoria nos gatilhos de automação via Cloud Functions.

### Removido
- Removidas chaves e tokens hardcoded, movendo tudo para variáveis de ambiente seguras.
