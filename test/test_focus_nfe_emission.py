import requests
import json
import uuid

BASE_URL = "http://localhost:8001/api"

def test_emit_mock_nfe():
    ref = f"NFE-{uuid.uuid4().hex[:8]}"
    print(f"=== Testando emissão de NFe (PRODUTO) mock (REF: {ref}) ===")
    
    payload = {
        "natureza_operacao": "Venda de mercadoria",
        "tipo_documento": 1,
        "items": [
            {
                "numero_item": "1",
                "codigo_produto": "PROD001",
                "descricao": "Produto de Teste NFe",
                "cfop": "5102",
                "unidade_comercial": "UN",
                "quantidade_comercial": 1.0,
                "valor_unitario_comercial": 100.0,
                "valor_bruto": 100.0,
                "valor_total": 100.0,
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
        "tomador": {
            "razao_social": "Comprador de Teste",
            "endereco": {
                "logradouro": "Rua de Entrega",
                "numero": "500",
                "bairro": "Industrial",
                "codigo_municipio": "3550308",
                "uf": "SP",
                "cep": "01001000"
            }
        }
    }

    try:
        response = requests.post(f"{BASE_URL}/nfe/?ref={ref}", json=payload, timeout=10)
        if response.status_code == 200:
            print("Sucesso na emissão da NFe!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erro na emissão da NFe: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"ERRO: Servidor em {BASE_URL} não encontrado.")

if __name__ == "__main__":
    test_emit_mock_nfe()
