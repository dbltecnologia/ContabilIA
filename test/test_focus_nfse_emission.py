import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api"

def test_emit_mock_nfse():
    ref = f"TEST-{uuid.uuid4().hex[:8]}"
    print(f"=== Testando emissão de nota mock (REF: {ref}) ===")
    
    payload = {
        "prestador": {
            "cnpj": "12345678000199",
            "codigo_municipio": "3550308"
        },
        "tomador": {
            "razao_social": "Cliente de Teste no Script",
            "endereco": {
                "logradouro": "Rua de Teste",
                "numero": "100",
                "bairro": "Centro",
                "codigo_municipio": "3550308",
                "uf": "SP",
                "cep": "01001000"
            }
        },
        "servico": {
            "aliquota": 2.0,
            "discriminacao": "Serviço de teste via script automatizado",
            "item_lista_servico": "0107",
            "valor_servicos": 50.0
        }
    }

    response = requests.post(f"{BASE_URL}/nfse/?ref={ref}", json=payload)
    
    if response.status_code == 200:
        print("Sucesso na emissão!")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"Erro na emissão: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_emit_mock_nfse()
