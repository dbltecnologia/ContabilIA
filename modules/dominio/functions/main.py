# functions/main.py

import firebase_admin
from firebase_admin import firestore, storage
from firebase_functions import firestore_fn

# Adiciona o diretório pai ao path para poder importar o módulo api_client
# Isso é uma forma comum de compartilhar código entre Cloud Functions
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))

from api_client import generate_access_token, get_integration_key, send_xml_to_external_api

firebase_admin.initialize_app()

@firestore_fn.on_document_created("documents/{document_id}")
def process_fiscal_document(event: firestore_fn.Event[firestore_fn.Change]) -> None:
    """ Gatilho automático do Firestore para processar documentos. """
    document_id = event.params["document_id"]
    doc_data = event.data.to_dict()

    if doc_data.get("status") != "PROCESSING":
        print(f"Documento {document_id} ignorado (status: {doc_data.get('status')}).")
        return

    print(f"--- [AUTOMÁTICO] Iniciando processamento para o documento: {document_id} ---")
    
    db = firestore.client()
    doc_ref = db.collection("documents").document(document_id)

    try:
        file_name = doc_data.get("fileName")
        user_id = doc_data.get("userId")
        if not file_name or not user_id:
            raise ValueError("fileName ou userId ausentes no documento.")

        print(f"Recuperando credenciais para o usuário: {user_id}")
        users_ref = db.collection("users").where("uid", "==", user_id).limit(1)
        user_docs = list(users_ref.stream())
        if not user_docs: raise ValueError(f"Usuário com uid '{user_id}' não encontrado.")
        
        user_data = user_docs[0].to_dict()
        client_id = user_data.get("clientId")
        client_secret = user_data.get("clientSecret")
        if not client_id or not client_secret: raise ValueError("Credenciais do cliente não configuradas no Firestore.")

        print("Baixando arquivo do Firebase Storage...")
        bucket = storage.bucket()
        file_path = f"uploads/{user_id}/{file_name}"
        blob = bucket.blob(file_path)
        if not blob.exists(): raise FileNotFoundError(f"Arquivo não encontrado no Storage: {file_path}")
        xml_content = blob.download_as_string()
        
        print("Iniciando comunicação com a API externa...")
        access_token = generate_access_token(client_id, client_secret)
        integration_key = get_integration_key(access_token, client_id)
        api_response = send_xml_to_external_api(integration_key, access_token, xml_content, file_name)

        print(f"Processo concluído com sucesso para {document_id}.")
        doc_ref.update({
            "status": "SUCCESS",
            "updatedAt": firestore.SERVER_TIMESTAMP,
            "apiResponse": api_response,
            "failureReason": firestore.DELETE_FIELD
        })

    except Exception as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_message += f" | Detalhe da API: {e.response.text}"
        print(f"ERRO no processamento do documento {document_id}: {error_message}")
        doc_ref.update({
            "status": "FAILURE",
            "updatedAt": firestore.SERVER_TIMESTAMP,
            "failureReason": error_message
        })