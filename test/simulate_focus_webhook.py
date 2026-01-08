import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def simulate_webhook_authorized(ref="TEST-REF-123"):
    print(f"=== Simulando Webhook de Autorização para {ref} ===")
    
    payload = {
        "ref": ref,
        "status": "autorizado",
        "id": "123456",
        "mensagem": "Nota autorizada com sucesso"
    }

    try:
        response = requests.post(f"{BASE_URL}/nfse/webhooks/focusnfe", json=payload)
        if response.status_code == 200:
            print("Webhook enviado com sucesso!")
            print("Verifique a pasta 'storage/invoices/' para ver se o download (simulado) ocorreu.")
        else:
            print(f"Erro ao enviar webhook: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"ERRO: Servidor em {BASE_URL} não encontrado.")

if __name__ == "__main__":
    simulate_webhook_authorized()
