# Documentação Módulo SEFAZ (PyNFe)

Este módulo fornece uma interface direta com os WebServices da SEFAZ (Secretaria da Fazenda) utilizando a biblioteca `PyNFe`. Ele é focado em operações de NFe e NFCe diretamente com o governo.

## Funcionalidades

### 1. Consulta de Distribuição (Download de Notas)
- **Método**: `baixar_notas_emitidas_contra_cnpj()`
- **Objetivo**: Recuperar todos os documentos fiscais (XMLs) emitidos contra o CNPJ configurado.
- **Lógica**: Utiliza o NSU (Número Seqüencial Único) para controle de sincronismo, garantindo que apenas notas novas sejam baixadas. O estado é persistido em um arquivo definido no `config.ini`.

### 2. Emissão e Autorização
- **Método**: `enviar_nota_sefaz(caminho_xml)`
- **Objetivo**: Assinar digitalmente um XML e enviá-lo para autorização em tempo real (síncrono).

### 3. Gestão e Status
- **Status do Serviço**: `verificar_status_sefaz()` para validar se a SEFAZ do estado está online.
- **Consulta por Chave**: `consultar_uma_nota(chave_acesso)` para verificar a validade de uma nota específica.

## Configuração (`config.ini`)

O módulo requer um arquivo `config.ini` na raiz do módulo com as seguintes seções:

```ini
[SEFAZ]
UF = SP
CNPJ = 00000000000000
CERT_PATH = certificado.pfx
CERT_PASSWORD = minha_senha

[CONTROLE]
OUTPUT_DIR = output/xmls
STATE_FILE = ultimo_nsu.json
```

## Dependências
- `PyNFe`: Biblioteca principal para comunicação.
- `cryptography`: Para manipulação dos certificados digitais.

> [!IMPORTANT]
> Diferente do Hub FocusNFe, este módulo requer a gestão manual de certificados digitais (.pfx) e senhas, sendo utilizado para integrações mais "baixo nível" diretamente com a SEFAZ.
