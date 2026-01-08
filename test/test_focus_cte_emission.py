import requests
import json
import uuid

BASE_URL = "http://localhost:8001/api"

def test_emit_mock_cte():
    ref = f"CTE-{uuid.uuid4().hex[:8]}"
    print(f"=== Testando emissão de CTe (Transporte) mock (REF: {ref}) ===")
    
    payload = {
        "modal": "01",
        "tipo_servico": "0",
        "tipo_cte": "0",
        "natureza_operacao": "Transporte de Carga",
        "forma_pagamento": "1",
        "tomador": "0",
        "data_emissao": "2024-01-01T12:00:00-03:00",
        "valor_total_servico": 150.0,
        "valor_receber": 150.0,
        "remetente": {
            "cnpj": "12345678000199",
            "razao_social": "Remetente de Teste",
            "logradouro": "Rua Origem",
            "numero": "1",
            "bairro": "Centro",
            "codigo_municipio": "3550308",
            "uf": "SP",
            "cep": "01001000"
        },
        "destinatario": {
            "cnpj": "98765432000188",
            "razao_social": "Destinatário de Teste",
            "logradouro": "Rua Destino",
            "numero": "99",
            "bairro": "Distrito",
            "codigo_municipio": "2111300",
            "uf": "MA",
            "cep": "65000000"
        },
        "produtos_predominante": "Diversos",
        "valor_carga": 1000.0,
        "informacoes_cte_normal": {
            "documentos_anteriores": [],
            "documentos_transporte_anterior": []
        }
    }

    try:
        response = requests.post(f"{BASE_URL}/cte/?ref={ref}", json=payload, timeout=10)
        if response.status_code == 200:
            print("Sucesso na emissão do CTe!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erro na emissão do CTe: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"ERRO: Servidor em {BASE_URL} não encontrado.")

if __name__ == "__main__":
    test_emit_mock_cte()
