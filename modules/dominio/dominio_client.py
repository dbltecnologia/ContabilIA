# modules/api_client.py

import os
import sys
import json
import requests

# --- DADOS DA API EXTERNA ---
AUDIENCE = "409f91f6-dc17-44c8-a5d8-e0a1bafd8b67"
AUTH_URL = "https://auth.thomsonreuters.com/oauth/token"
API_ACTIVATION_ENABLE_URL = "https://api.onvio.com.br/dominio/integration/v1/activation/enable"
API_INVOICE_BATCH_URL = "https://api.onvio.com.br/dominio/invoice/v3/batches"

def generate_access_token(client_id, client_secret):
    """Gera um token de acesso usando as credenciais fornecidas."""
    print(f"Gerando token para o clientId: {client_id[:5]}...")
    auth_payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": AUDIENCE,
    }
    response = requests.post(AUTH_URL, data=auth_payload)
    response.raise_for_status()
    access_token = response.json().get("access_token")
    if not access_token:
        raise ValueError("Token de acesso não retornado pela API de autenticação.")
    print("-> Token de acesso gerado com sucesso.")
    return access_token

def get_integration_key(access_token, client_key):
    """Gera a chave de integração para o envio."""
    print("Gerando chave de integração...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-integration-key": client_key,
    }
    response = requests.post(API_ACTIVATION_ENABLE_URL, headers=headers)
    response.raise_for_status()
    integration_key = response.json().get("integrationKey")
    if not integration_key:
        raise ValueError("Chave de integração não retornada pela API.")
    print("-> Chave de integração gerada com sucesso.")
    return integration_key

def send_xml_to_external_api(integration_key, access_token, xml_content, file_name):
    """Envia o conteúdo XML para a API de processamento."""
    print(f"Enviando arquivo '{file_name}' para a API externa...")
    files = {
        'file[]': (file_name, xml_content, 'application/xml'),
        'query': (None, '{"boxeFile":false}', 'application/json')
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-integration-key": integration_key
    }
    response = requests.post(API_INVOICE_BATCH_URL, headers=headers, files=files)
    response.raise_for_status()
    print(f"-> Arquivo '{file_name}' enviado com sucesso.")
    return response.json()

def run_manual_api_submission(diretorio_xmls: str):
    """
    Função principal para orquestrar o envio manual de um lote de XMLs.
    Lê as credenciais das variáveis de ambiente.
    """
    MANUAL_CLIENT_ID = os.getenv("MANUAL_CLIENT_ID")
    MANUAL_CLIENT_SECRET = os.getenv("MANUAL_CLIENT_SECRET")

    if not MANUAL_CLIENT_ID or not MANUAL_CLIENT_SECRET:
        print("\nERRO CRÍTICO: As variáveis MANUAL_CLIENT_ID e MANUAL_CLIENT_SECRET devem ser definidas no arquivo .env")
        sys.exit(1)

    results = {}
    try:
        # Autentica uma vez para todo o lote
        access_token = generate_access_token(MANUAL_CLIENT_ID, MANUAL_CLIENT_SECRET)
        integration_key = get_integration_key(access_token, MANUAL_CLIENT_ID)

        # Itera sobre os arquivos da pasta
        arquivos_xml = [f for f in os.listdir(diretorio_xmls) if f.lower().endswith('.xml')]
        total_arquivos = len(arquivos_xml)
        print(f"\nEncontrados {total_arquivos} arquivos XML para processar.")

        for i, filename in enumerate(arquivos_xml):
            print(f"\n--- Processando {i+1}/{total_arquivos}: {filename} ---")
            file_path = os.path.join(diretorio_xmls, filename)
            try:
                with open(file_path, 'rb') as f:
                    xml_content = f.read()
                
                api_response = send_xml_to_external_api(integration_key, access_token, xml_content, filename)
                results[filename] = {"status": "SUCCESS", "response": api_response}
                
            except Exception as e:
                error_msg = str(e)
                if hasattr(e, 'response') and e.response is not None:
                    error_msg += f" | Detalhe da API: {e.response.text}"
                print(f"!!! ERRO ao processar {filename}: {error_msg}")
                results[filename] = {"status": "FAILURE", "error": error_msg}
    
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" | Detalhe da API: {e.response.text}"
        print(f"\n!!! ERRO FATAL durante a execução: {error_msg}")
        sys.exit(1)

    # Salva um resumo do lote em um arquivo JSON
    output_path = "envio_api_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n--- Processamento concluído. Resultados salvos em '{output_path}' ---")