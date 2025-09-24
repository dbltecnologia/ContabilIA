# -*- coding: utf-8 -*-

"""
SCRIPT BASEADO NOS EXEMPLOS DA WIKI OFICIAL DA PyNFe
------------------------------------------------------
Este script demonstra as principais funcionalidades da biblioteca,
lendo as configurações de um arquivo `config.ini`.

Para usar, escolha qual função executar no final do arquivo,
na seção `if __name__ == "__main__":`.
"""

import os
import logging
import base64
import zlib
import json
import configparser
from xml.etree import ElementTree

# A importação para ComunicacaoSefaz está correta na versão mais recente
from pynfe.processamento.comunicacao import ComunicacaoSefaz

# --- CARREGAMENTO DA CONFIGURAÇÃO ---
config = configparser.ConfigParser()
if not os.path.exists('config.ini'):
    print("ERRO: Arquivo 'config.ini' não encontrado.")
    exit()
config.read('config.ini')

SEFAZ_CONFIG = config['SEFAZ']
CONTROLE_CONFIG = config['CONTROLE']

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# --- EXEMPLO 1: VERIFICAR STATUS DO SERVIÇO (da Wiki) ---
def verificar_status_sefaz():
    """Conecta-se à SEFAZ do estado definido no config e verifica o status do serviço de NFe."""
    logging.info("--- 1. Verificando Status do Serviço da SEFAZ ---")
    try:
        con = ComunicacaoSefaz(
            uf=SEFAZ_CONFIG['UF'],
            certificado=SEFAZ_CONFIG['CERT_PATH'],
            certificado_senha=SEFAZ_CONFIG['CERT_PASSWORD'],
            homologacao=False
        )
        retorno = con.status_servico('nfe')
        
        # Analisa o XML de retorno
        xml_retorno = ElementTree.fromstring(retorno.text)
        status = xml_retorno.findtext('.//{http://www.portalfiscal.inf.br/nfe}cStat')
        motivo = xml_retorno.findtext('.//{http://www.portalfiscal.inf.br/nfe}xMotivo')
        logging.info(f"Status: [{status}] - {motivo}")

    except Exception as e:
        logging.error(f"Ocorreu um erro: {e}", exc_info=True)


# --- EXEMPLO 2: BAIXAR NOTAS (nosso objetivo principal, da Wiki) ---
def baixar_notas_emitidas_contra_cnpj():
    """Busca e salva todos os documentos fiscais emitidos contra o CNPJ configurado."""
    logging.info("--- 2. Baixando Documentos Fiscais (DF-e) ---")
    output_dir = CONTROLE_CONFIG['OUTPUT_DIR']
    state_file = CONTROLE_CONFIG['STATE_FILE']
    os.makedirs(output_dir, exist_ok=True)

    # Carrega o último NSU
    ultimo_nsu = '0'
    try:
        with open(state_file, 'r') as f:
            ultimo_nsu = json.load(f).get('ultimo_nsu', '0')
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    logging.info(f"Buscando a partir do NSU: {ultimo_nsu}")
    
    try:
        con = ComunicacaoSefaz(
            uf='AN',  # Para este serviço, a UF é sempre 'AN' (Ambiente Nacional)
            certificado=SEFAZ_CONFIG['CERT_PATH'],
            certificado_senha=SEFAZ_CONFIG['CERT_PASSWORD'],
            homologacao=False
        )
        
        retorno = con.consulta_distribuicao(
            cnpj=SEFAZ_CONFIG['CNPJ'],
            nsu=ultimo_nsu,
            consulta_nsu_especifico=False
        )
        
        if retorno.status_code == 200:
            xml_retorno = ElementTree.fromstring(retorno.text.encode('utf-8'))
            
            lote_docs = xml_retorno.find(".//{http://www.portalfiscal.inf.br/nfe}loteDistDFeInt")
            if lote_docs:
                for doc in lote_docs.findall('{http://www.portalfiscal.inf.br/nfe}docZip'):
                    ns_u = doc.get("NSU")
                    schema = doc.get("schema")
                    conteudo_zip = doc.text.encode('utf-8')
                    conteudo_descompactado = zlib.decompress(base64.b64decode(conteudo_zip), 16+zlib.MAX_WBITS)
                    
                    nome_arquivo = os.path.join(output_dir, f"{ns_u}-{schema}.xml")
                    with open(nome_arquivo, 'wb') as f:
                        f.write(conteudo_descompactado)
                    
                    logging.info(f"Nota fiscal salva: {nome_arquivo}")

                ult_nsu_retorno = xml_retorno.findtext(".//{http://www.portalfiscal.inf.br/nfe}ultNSU")
                with open(state_file, 'w') as f:
                    json.dump({'ultimo_nsu': ult_nsu_retorno}, f)
                logging.info(f"Último NSU atualizado para: {ult_nsu_retorno}")
            else:
                logging.info("Nenhum novo documento encontrado.")

    except Exception as e:
        logging.error(f"Ocorreu um erro: {e}", exc_info=True)


# --- NOVA FUNÇÃO PARA ENVIAR NOTA À SEFAZ ---
def enviar_nota_sefaz(caminho_xml_para_enviar):
    """
    Assina e envia um XML de NF-e/NFC-e para a SEFAZ para autorização.
    Certifique-se de que o XML de teste esteja na pasta do projeto.
    """
    logging.info(f"--- Enviando a nota {caminho_xml_para_enviar} para a SEFAZ ---")
    try:
        # Carrega o XML da nota fiscal
        with open(caminho_xml_para_enviar, 'rb') as f:
            xml_content = f.read()
        
        # Constrói o objeto de comunicação
        con = ComunicacaoSefaz(
            uf=SEFAZ_CONFIG['UF'],
            certificado=SEFAZ_CONFIG['CERT_PATH'],
            certificado_senha=SEFAZ_CONFIG['CERT_PASSWORD'],
            homologacao=True
        )
        
        # Assina e envia o XML
        retorno = con.autorizacao(
            modelo='nfce',
            nota_fiscal=xml_content,
            ind_sinc=1
        )
        
        # Processa a resposta
        if retorno[0] == 0:
            logging.info("Nota enviada com sucesso e autorizada!")
        else:
            logging.error(f"Erro ao enviar a nota: {retorno[1].text}")
            
    except FileNotFoundError:
        logging.error(f"Arquivo XML não encontrado em: {caminho_xml_para_enviar}")
    except Exception as e:
        logging.error(f"Ocorreu um erro: {e}", exc_info=True)


# --- EXEMPLO 3: CONSULTAR UMA NOTA (da Wiki) ---
def consultar_uma_nota(chave_acesso):
    """Consulta uma única NFe pela sua chave de acesso de 44 dígitos."""
    logging.info(f"--- 3. Consultando a NFe de chave: {chave_acesso} ---")
    if len(chave_acesso) != 44 or not chave_acesso.isdigit():
        logging.error("Chave de acesso inválida. Deve conter 44 dígitos numéricos.")
        return

    try:
        # Correção: O modelo da nota agora é NFCe
        con = ComunicacaoSefaz(
            uf=SEFAZ_CONFIG['UF'],
            certificado=SEFAZ_CONFIG['CERT_PATH'],
            certificado_senha=SEFAZ_CONFIG['CERT_PASSWORD'],
            homologacao=False
        )
        retorno = con.consulta_nota('nfce', chave_acesso) # <-- CORREÇÃO AQUI
        
        if retorno.status_code == 200:
            xml_retorno = ElementTree.fromstring(retorno.text.encode('utf-8'))
            status = xml_retorno.findtext('.//{http://www.portalfiscal.inf.br/nfe}cStat')
            motivo = xml_retorno.findtext('.//{http://www.portalfiscal.inf.br/nfe}xMotivo')
            
            logging.info(f"Status da Nota: [{status}] - {motivo}")
        else:
            logging.error("Ocorreu um erro na requisição: " + str(retorno.status_code))
    
    except Exception as e:
        logging.error(f"Ocorreu um erro: {e}", exc_info=True)


# --- EXEMPLO 4: GERAR DANFE (da Wiki) ---
def gerar_danfe_de_xml(caminho_xml):
    """Gera um PDF (DANFE) a partir de um arquivo XML de NFe autorizado."""
    logging.info(f"--- 4. Gerando DANFE para o arquivo: {caminho_xml} ---")
    if not os.path.exists(caminho_xml):
        logging.error(f"Arquivo XML não encontrado em: {caminho_xml}")
        return

    logging.error("A funcionalidade de geração de DANFE requer uma biblioteca auxiliar. " +
                  "Esta função está desabilitada para evitar erros de importação. " +
                  "Consulte a documentação oficial para a maneira correta de gerar o DANFE.")


# --- EXECUÇÃO ---
if __name__ == "__main__":
    # --------------------------------------------------------------------------
    # Escolha qual função você quer executar descomentando a linha correspondente
    # --------------------------------------------------------------------------

    # 1. Para verificar o status da Sefaz do seu estado
    # verificar_status_sefaz()

    # 2. Para baixar as notas emitidas contra seu CNPJ
    # baixar_notas_emitidas_contra_cnpj()
    
    # 3. Para enviar uma nota de teste para a SEFAZ (use um XML válido!)
    # xml_para_enviar = "53250919019208000180651150000119591999880404.xml"
    # enviar_nota_sefaz(xml_para_enviar)

    # 4. Para consultar uma NFe específica (substitua pela chave que quer consultar)
    chave = "53250819019208000180651110000176579999823420"
    consultar_uma_nota(chave)

    # 5. Para gerar um DANFE de um XML que você já baixou
    # xml_para_danfe = "output/NFe-352101...CHAVE_DA_NOTA...-nfe.xml"
    # gerar_danfe_de_xml(xml_para_danfe)