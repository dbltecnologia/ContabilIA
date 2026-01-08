import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api"

def test_emit_mock_mdfe():
    ref = f"MDFE-{uuid.uuid4().hex[:8]}"
    print(f"=== Testando emissão de MDFe (Manifesto) mock (REF: {ref}) ===")
    
    payload = {
        "tipo_emitente": "1",
        "tipo_transportador": "1",
        "modal": "1",
        "data_emissao": "2024-01-01T12:00:00-03:00",
        "uf_inicio": "SP",
        "uf_fim": "RJ",
        "placa": "ABC1234",
        "renavam": "123456789",
        "capacidade_kg": 10000,
        "capacidade_m3": 50,
        "condutores": [
            {
                "nome": "Motorista de Teste",
                "cpf": "12345678901"
            }
        ],
        "inf_documentos": {
            "inf_municipio_descarga": [
                {
                    "codigo_municipio": "3304557",
                    "nome_municipio": "Rio de Janeiro",
                    "inf_cte": [
                        {
                            "chave": "35231212345678000199570010000000011234567890"
                        }
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(f"{BASE_URL}/mdfe/?ref={ref}", json=payload, timeout=10)
        if response.status_code == 200:
            print("Sucesso na emissão do MDFe!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erro na emissão do MDFe: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"ERRO: Servidor em {BASE_URL} não encontrado.")

if __name__ == "__main__":
    test_emit_mock_mdfe()
