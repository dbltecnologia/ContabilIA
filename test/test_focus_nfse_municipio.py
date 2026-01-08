import requests
import json
import os

BASE_URL = "http://localhost:8000/api"

def test_municipio_requirements(ibge_code="3550308"): # São Paulo
    print(f"=== Testando requisitos para município {ibge_code} ===")
    try:
        response = requests.get(f"{BASE_URL}/nfse/municipio/{ibge_code}", timeout=5)
        if response.status_code == 200:
            print("Sucesso!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erro: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"\nERRO: Não foi possível conectar ao servidor em {BASE_URL}.")
        print("Certifique-se de que o servidor está rodando (uvicorn main:app --reload) antes de executar este script.")

if __name__ == "__main__":
    test_municipio_requirements()
