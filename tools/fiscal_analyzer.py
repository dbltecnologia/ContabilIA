# modules/fiscal_analyzer.py

import os
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
from datetime import datetime
import json
import re

# --- CONFIGURAÇÕES GERAIS ---
ALIQUOTA_PIS = Decimal('1.65')
ALIQUOTA_COFINS = Decimal('7.6')
CSTS_TRIBUTADOS_INCORRETOS = {'01', '02'}

def carregar_categorias_fiscais(arquivo_config: str):
    """Carrega e pré-compila as categorias, NCMs e regex de um arquivo JSON."""
    if not os.path.exists(arquivo_config):
        print(f"ERRO CRÍTICO: O arquivo de configuração '{arquivo_config}' não foi encontrado!")
        sys.exit(1)

    with open(arquivo_config, 'r', encoding='utf-8') as f:
        categorias = json.load(f)

    todos_ncms_validos = set()
    for cat in categorias:
        cat['regex_compilado'] = [re.compile(p, re.IGNORECASE) for p in cat['regex_produtos']]
        for ncm in cat['ncms_esperados']:
            todos_ncms_validos.add(ncm)
            
    print(f"Sucesso: {len(categorias)} categorias fiscais carregadas do arquivo '{arquivo_config}'.")
    return categorias, todos_ncms_validos

def analisar_xmls_fiscais(diretorio_xmls: str, categorias: list, todos_ncms_validos: set) -> dict:
    """Analisa os arquivos XML de NF-e, aplicando uma lógica de duas camadas."""
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    inconsistencias = []
    total_faturado = Decimal('0.0')
    arquivos_processados = 0

    print(f"\nIniciando análise no diretório: {diretorio_xmls}")
    arquivos_xml = [f for f in os.listdir(diretorio_xmls) if f.lower().endswith('.xml')]
    total_arquivos = len(arquivos_xml)

    if total_arquivos == 0:
        print("Nenhum arquivo XML encontrado no diretório.")
        return {'inconsistencias': [], 'total_faturado': Decimal('0.0'), 'arquivos_processados': 0}

    for i, nome_arquivo in enumerate(arquivos_xml):
        print(f"Processando arquivo {i+1}/{total_arquivos}: {nome_arquivo}", end='\r')
        caminho_completo = os.path.join(diretorio_xmls, nome_arquivo)
        try:
            tree = ET.parse(caminho_completo)
            root = tree.getroot()
            # Suporta tanto NF-e (nfeProc) quanto o XML da NFe em si (NFe)
            itens_nota = root.findall('.//nfe:det', ns)
            if not itens_nota: # Fallback para o caso de o XML não ter o nfeProc
                root_nfe = root.find('nfe:NFe', ns)
                if root_nfe is not None:
                    itens_nota = root_nfe.findall('.//nfe:det', ns)

            for item in itens_nota:
                prod = item.find('nfe:prod', ns)
                imposto = item.find('nfe:imposto', ns)
                if prod is None or imposto is None: continue

                ncm = (prod.find('nfe:NCM', ns).text or '').strip()
                valor_produto = Decimal(prod.find('nfe:vProd', ns).text)
                nome_produto = prod.find('nfe:xProd', ns).text
                total_faturado += valor_produto
                
                item_inconsistente = None

                # Camada 1: Erro de Tributação (NCM correto, CST errado)
                is_ncm_valido = any(ncm.startswith(codigo) for codigo in todos_ncms_validos)
                if is_ncm_valido:
                    pis_node = imposto.find('nfe:PIS/nfe:PISAliq', ns)
                    cofins_node = imposto.find('nfe:COFINS/nfe:COFINSAliq', ns)
                    if pis_node is not None and cofins_node is not None:
                        cst_pis = pis_node.find('nfe:CST', ns).text
                        cst_cofins = cofins_node.find('nfe:CST', ns).text
                        if cst_pis in CSTS_TRIBUTADOS_INCORRETOS or cst_cofins in CSTS_TRIBUTADOS_INCORRETOS:
                            item_inconsistente = {
                                'tipo_inconsistencia': 'Erro de Tributação',
                                'categoria_detectada': 'N/A',
                                'pis_pago_a_maior': (valor_produto * ALIQUOTA_PIS) / 100,
                                'cofins_pago_a_maior': (valor_produto * ALIQUOTA_COFINS) / 100
                            }
                
                # Camada 2: Risco de Cadastro (Descrição correta, NCM errado)
                if not item_inconsistente:
                    for cat in categorias:
                        if any(regex.search(nome_produto) for regex in cat['regex_compilado']):
                            if not any(ncm.startswith(ncm_esperado) for ncm_esperado in cat['ncms_esperados']):
                                item_inconsistente = {
                                    'tipo_inconsistencia': 'Risco de Cadastro',
                                    'categoria_detectada': cat['categoria'],
                                    'pis_pago_a_maior': Decimal('0.0'),
                                    'cofins_pago_a_maior': Decimal('0.0')
                                }
                                break
                
                if item_inconsistente:
                    base_info = {'arquivo_xml': nome_arquivo, 'produto': nome_produto, 'ncm': ncm, 'valor_item': valor_produto}
                    base_info.update(item_inconsistente)
                    inconsistencias.append(base_info)
            arquivos_processados += 1
        except ET.ParseError:
            print(f"\nAviso: Arquivo '{nome_arquivo}' não é um XML válido e foi ignorado.")
        except Exception as e:
            print(f"\nAviso: Erro inesperado ao processar '{nome_arquivo}': {e}. O arquivo foi ignorado.")
    
    print("\nAnálise concluída.                                     ")
    return {'inconsistencias': inconsistencias, 'total_faturado': total_faturado, 'arquivos_processados': arquivos_processados}


def gerar_relatorio_final(resultados: dict, pasta_saida: str):
    """Gera o relatório no console e o arquivo Excel detalhado."""
    f_moeda = lambda v: f"R$ {v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    if resultados['arquivos_processados'] == 0:
        return

    df = pd.DataFrame(resultados['inconsistencias'])
    
    df_erros_tributacao = df[df['tipo_inconsistencia'] == 'Erro de Tributação'] if not df.empty else pd.DataFrame(columns=df.columns)
    total_pis_recuperar = df_erros_tributacao['pis_pago_a_maior'].sum() if not df_erros_tributacao.empty else Decimal('0.0')
    total_cofins_recuperar = df_erros_tributacao['cofins_pago_a_maior'].sum() if not df_erros_tributacao.empty else Decimal('0.0')
    total_recuperar = total_pis_recuperar + total_cofins_recuperar

    print("\n" + "="*80)
    print(" RELATÓRIO DE ANÁLISE FISCAL PIS/COFINS")
    print("="*80)
    print("\n--- SUMÁRIO GERAL ---")
    print(f"Arquivos XML de NF-e analisados: {resultados['arquivos_processados']}")
    print(f"Faturamento Total no Período Analisado: {f_moeda(resultados['total_faturado'])}")
    print("\n--- DIAGNÓSTICO ---")
    print(f"Itens com ERRO DE TRIBUTAÇÃO (imposto a recuperar): {len(df_erros_tributacao)}")
    print(f"Itens com RISCO DE CADASTRO (NCM x Descrição inconsistente): {len(df) - len(df_erros_tributacao)}")
    print("\n--- VALORES A RECUPERAR (de Erros de Tributação) ---")
    print(f"Total de PIS a recuperar: {f_moeda(total_pis_recuperar)}")
    print(f"Total de COFINS a recuperar: {f_moeda(total_cofins_recuperar)}")
    print("--------------------------------------------------")
    print(f"   VALOR TOTAL A SER RECUPERADO: {f_moeda(total_recuperar)}")
    print("--------------------------------------------------")

    if df.empty:
        print("\nNenhuma inconsistência encontrada. Nenhum relatório em Excel foi gerado.")
        return

    print("\nGerando relatório detalhado em Excel...")
    try:
        df_final = df.rename(columns={
            'arquivo_xml': 'Arquivo de Origem', 'produto': 'Nome do Produto', 'ncm': 'NCM do Produto',
            'valor_item': 'Valor (R$)', 'tipo_inconsistencia': 'Tipo de Inconsistência',
            'categoria_detectada': 'Categoria Sugerida (via Descrição)',
            'pis_pago_a_maior': 'PIS a Recuperar (R$)', 'cofins_pago_a_maior': 'COFINS a Recuperar (R$)'
        })
        ordem_colunas = ['Tipo de Inconsistência', 'Nome do Produto', 'NCM do Produto', 'Categoria Sugerida (via Descrição)',
                         'Valor (R$)', 'PIS a Recuperar (R$)', 'COFINS a Recuperar (R$)', 'Arquivo de Origem']
        df_final = df_final[ordem_colunas]
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        nome_arquivo = f"Diagnostico_Fiscal_PIS_COFINS_{timestamp}.xlsx"
        caminho_completo_saida = os.path.join(pasta_saida, nome_arquivo)
        
        df_final.to_excel(caminho_completo_saida, index=False, engine='openpyxl')
        
        print(f"\nSUCESSO: O diagnóstico completo foi salvo em:\n{caminho_completo_saida}")
    except Exception as e:
        print(f"\nERRO: Não foi possível gerar o arquivo Excel. Causa: {e}")


def run_fiscal_analysis(diretorio_xmls: str, pasta_saida: str, arquivo_categorias_path: str):
    """
    Função principal para ser chamada pelo main.py.
    Orquestra o carregamento de categorias, a análise e a geração de relatório.
    """
    categorias_fiscais, todos_ncms_validos = carregar_categorias_fiscais(arquivo_categorias_path)
    resultados = analisar_xmls_fiscais(diretorio_xmls, categorias_fiscais, todos_ncms_validos)
    gerar_relatorio_final(resultados, pasta_saida)