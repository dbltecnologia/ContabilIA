import argparse
import requests
import json
import os
import sys

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def emit(doc_type, ref, payload_file, token):
    url = f"{BASE_URL}/nfse/{doc_type}/"
    if doc_type == "nfse":
        url = f"{BASE_URL}/nfse/"
    
    headers = {}
    if token:
        headers["X-Focus-Token"] = token
    
    with open(payload_file, 'r') as f:
        payload = json.load(f)
    
    params = {"ref": ref}
    print(f"Enviando {doc_type} (Ref: {ref}) para {url}...")
    
    try:
        response = requests.post(url, json=payload, params=params, headers=headers)
        if response.status_code == 200:
            print("Sucesso!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erro {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Falha na conexão: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utilitário para emissão de notas via Hub FocusNFE")
    parser.add_argument("type", choices=["nfse", "nfe", "nfce", "cte", "mdfe"], help="Tipo de documento")
    parser.add_argument("ref", help="Referência única da nota")
    parser.add_argument("file", help="Caminho para o arquivo JSON com os dados da nota")
    parser.add_argument("--token", help="Token FocusNFe (opcional, sobrescreve .env)")
    
    args = parser.parse_args()
    emit(args.type, args.ref, args.file, args.token)
