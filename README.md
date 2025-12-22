# Contabil_IA: Automação Fiscal e Integração

## 🚀 Visão Geral do Projeto

O **Contabil_IA** é um projeto de automação desenvolvido em Python, com o objetivo de simplificar e agilizar o fluxo de trabalho de escritórios de contabilidade. Ele integra duas funcionalidades essenciais em um único painel de controle de linha de comando:

1.  **Download Automático de Notas Fiscais:** Utiliza a biblioteca `PyNFe` para se conectar ao webservice da SEFAZ (Secretaria da Fazenda), baixar os arquivos XML de notas fiscais (NF-e, NFC-e) emitidas contra um CNPJ e salvar os documentos em uma pasta local.
2.  **Envio para API Externa:** Processa os arquivos XML baixados e os envia em lote para a API da Thomson Reuters (Dominio Sistemas), automatizando a entrada de dados e garantindo a conformidade fiscal.

O projeto foi estruturado para ser modular, seguro e fácil de usar, ideal para ser apresentado como parte de um portfólio de desenvolvimento.

## 📦 Estrutura do Projeto

A organização do código é dividida por responsabilidade, facilitando a manutenção e a compreensão:

```

Contabil\_IA/
├── .env.example              \# Exemplo de arquivo para credenciais e configurações
├── .gitignore                \# Arquivos e pastas a serem ignorados pelo Git
├── main.py                   \# Ponto de entrada e orquestrador principal do projeto
├── requirements.txt          \# Dependências do Python
├── config/
│   ├── config.ini.example    \# Exemplo de arquivo de configuração da SEFAZ
│   └── categorias\_fiscais.json \# Arquivo de configuração para análises fiscais
├── modules/
│   ├── dominio/
│   │   └── dominio\_client.py   \# Lógica de autenticação e envio para a API da Thomson Reuters
│   └── sefaz/
│       └── sefaz\_client.py     \# Lógica de download e consulta de notas da SEFAZ
├── tools/
│   └── fiscal\_analyzer.py      \# Ferramenta para análise fiscal (opcional)
└── README.md                 \# Este arquivo

````

## ⚙️ Instalação e Configuração

Siga os passos abaixo para configurar e executar o projeto.

### Pré-requisitos
* Python 3.8+
* Um certificado digital A1 (.pfx) com a senha
* Credenciais de API da Thomson Reuters (clientId e clientSecret)

### Passo 1: Clone o Repositório
```bash
git clone [https://github.com/seu-usuario/Contabil_IA.git](https://github.com/seu-usuario/Contabil_IA.git)
cd Contabil_IA
````

### Passo 2: Crie e Ative o Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instale as Dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configure as Credenciais

Crie um arquivo chamado `.env` na raiz do projeto (na mesma pasta deste `README.md`) e preencha com suas credenciais. Utilize o arquivo `.env.example` como guia.

```ini
# Conteúdo do seu arquivo .env
DOMINIO_CLIENT_ID="SUA_CLIENT_ID_DA_THOMSON_REUTERS"
DOMINIO_CLIENT_SECRET="SUA_CLIENT_SECRET_DA_THOMSON_REUTERS"

SEFAZ_CNPJ="SEU_CNPJ_AQUI_SOMENTE_NUMEROS"
SEFAZ_CERT_PASSWORD="SUA_SENHA_DO_CERTIFICADO"
SEFAZ_UF="DF" # Ou a sigla do seu estado, ex: SP, MG, PR
SEFAZ_CERT_PATH="caminho/para/o/certificado_js.pfx"
```

> **Importante:** O arquivo `.env` está listado no `.gitignore` por segurança e não será enviado ao repositório público.

## 🚀 Como Usar o Painel de Controle

O arquivo `main.py` funciona como o ponto de entrada para todas as operações. Utilize-o com o `argparse` para executar os comandos.

### 1\. Baixar notas da SEFAZ e enviar para a API (Fluxo Completo)

Este comando executa o fluxo completo de ponta a ponta. Ele baixa os XMLs da SEFAZ e os envia para a API externa.

```bash
python main.py fluxo-completo
```

  - **Parâmetros Opcionais:**
      - `--saida-sefaz`: Permite especificar uma pasta diferente para salvar os XMLs baixados.

### 2\. Enviar um lote de XMLs para a API

Utilize este comando se você já possui os arquivos XML e quer apenas enviá-los para a API.

```bash
python main.py enviar-api caminho/para/a/sua/pasta/de/xmls
```

### 3\. Analisar Notas Fiscais

Utilize este comando para executar a análise fiscal do seu projeto.

```bash
python main.py analisar caminho/para/a/sua/pasta/de/xmls
```

## 🛠️ Tecnologias Utilizadas

  - **Python 3.8+**
  - **PyNFe:** Biblioteca para comunicação com os webservices da SEFAZ.
  - **Requests:** Para requisições HTTP à API da Thomson Reuters.
  - **python-dotenv:** Para gerenciar variáveis de ambiente de forma segura.
  - **argparse:** Para criar uma interface de linha de comando robusta.

## 🧩 Integração adicional: Focus NFe (API)

Esta integração é **independente** da integração atual com SEFAZ via PyNFe (ou seja, mantém o que já existe hoje) e fica em `modules/focus_nfe/`.

### Configuração

Defina no `.env` (veja `.env.example`):

- `FOCUS_NFE_TOKEN`
- `FOCUS_NFE_BASE_URL` (opcional, default `https://api.focusnfe.com.br`)
- `FOCUS_NFE_ENV` (opcional: `producao`|`homologacao`, usado se `FOCUS_NFE_BASE_URL` não estiver definido)

### Uso (CLI mínima)

Criar/solicitar emissão (exemplo):

```bash
python -m modules.focus_nfe.cli create --doc nfe --ref MINHA_REF --json payload.json
```

Consultar status:

```bash
python -m modules.focus_nfe.cli status --doc nfe --ref MINHA_REF
```

Baixar XML/PDF:

```bash
python -m modules.focus_nfe.cli download --doc nfe --ref MINHA_REF --format xml --out ./out/minha_nfe.xml
```
