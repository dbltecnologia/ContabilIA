import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api"

def test_emit_mock_nfce():
    ref = f"NFCE-{uuid.uuid4().hex[:8]}"
    print(f"=== Testando emissão de NFCe (Varejo) mock (REF: {ref}) ===")
    
    payload = {
        "natureza_operacao": "Venda ao Consumidor",
        "presenca_comprador": 1,
        "items": [
            {
                "numero_item": "1",
                "codigo_produto": "CONSUMO01",
                "descricao": "Item de Varejo Teste",
                "cfop": "5102",
                "unidade_comercial": "UN",
                "quantidade_comercial": 1.0,
                "valor_unitario_comercial": 10.0,
                "valor_bruto": 10.0,
                "valor_total": 10.0,
                "ncm": "62034200",
                "icms_origem": "0",
                "icms_situacao_tributaria": "102",
                "pis_situacao_tributaria": "07",
                "cofins_situacao_tributaria": "07"
            }
        ],
        "prestador": {
            "cnpj": "12345678000199",
            "codigo_municipio": "3550308"
        },
        "formas_pagamento": [
            {
                "forma_pagamento": "01",
                "valor_pagamento": 10.0
            }
        ]
    }

    try:
        response = requests.post(f"{BASE_URL}/nfce/?ref={ref}", json=payload, timeout=10)
        if response.status_code == 200:
            print("Sucesso na emissão da NFCe!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erro na emissão da NFCe: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"ERRO: Servidor em {BASE_URL} não encontrado.")

if __name__ == "__main__":
    test_emit_mock_nfce()
