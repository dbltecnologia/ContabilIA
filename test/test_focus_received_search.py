import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_list_received_invoices(cnpj="12345678000199"):
    print(f"=== Testando busca de notas recebidas (ENTRADA) para CNPJ: {cnpj} ===")
    
    try:
        response = requests.get(f"{BASE_URL}/nfse/recebidos/nfe?cnpj={cnpj}", timeout=15)
        if response.status_code == 200:
            print("Sucesso! Notas encontradas:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erro na busca: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"ERRO: Servidor em {BASE_URL} não encontrado.")

if __name__ == "__main__":
    # Nota: No ambiente de homologação, pode ser necessário um CNPJ válido com notas emitidas contra ele.
    test_list_received_invoices()
