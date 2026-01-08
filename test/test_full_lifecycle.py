import requests
import json
import uuid
import time
import os

BASE_URL = "http://localhost:8001/api"

def test_full_lifecycle():
    ref = f"LIFE-{uuid.uuid4().hex[:8]}"
    print(f"=== Iniciando Ciclo de Vida Completo (REF: {ref}) ===")
    
    # 1. Emitir NFSe
    print("\n1. Emitindo Nota...")
    emission_payload = {
        "prestador": {"cnpj": "12345678000199", "codigo_municipio": "3550308"},
        "tomador": {
            "razao_social": "Ciclo de Vida Teste",
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
            "discriminacao": "Teste de ciclo de vida completo",
            "item_lista_servico": "0107",
            "valor_servicos": 1.0
        }
    }
    
    res_emit = requests.post(f"{BASE_URL}/nfse/?ref={ref}", json=emission_payload)
    if res_emit.status_code != 200:
        print(f"ERRO na emissão: {res_emit.text}")
        return
    print("Nota enviada com sucesso!")

    # 2. Simular Webhook da FocusNFE
    print("\n2. Simulando Webhook de Autorização...")
    time.sleep(1) # Pequena pausa para garantir processamento inicial
    webhook_payload = {
        "ref": ref,
        "status": "autorizado",
        "id": f"ID-{uuid.uuid4().hex[:6]}",
        "mensagem": "Nota autorizada pelo ciclo de vida"
    }
    res_hook = requests.post(f"{BASE_URL}/nfse/webhooks/focusnfe", json=webhook_payload)
    if res_hook.status_code != 200:
        print(f"ERRO no webhook: {res_hook.text}")
        return
    print("Webhook processado!")

    # 3. Verificar Persistência e Download
    print("\n3. Verificando dados locais...")
    time.sleep(2) # Pausa para processamento em background (background_tasks)
    res_local = requests.get(f"{BASE_URL}/nfse/local/{ref}")
    if res_local.status_code != 200:
        print(f"ERRO ao buscar dados locais: {res_local.text}")
        return
    
    data = res_local.json()
    print(f"Status Local: {data.get('status')}")
    print(f"Caminho PDF: {data.get('pdf_path')}")
    print(f"Caminho XML: {data.get('xml_path')}")

    if data.get('status') == 'autorizado':
        print("\n✅ CICLO DE VIDA CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ FALHA: O status local não foi atualizado corretamente.")

if __name__ == "__main__":
    test_full_lifecycle()
