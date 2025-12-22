import sys
import os
import logging

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.sefaz.sefaz_client import baixar_notas_emitidas_contra_cnpj, verificar_status_sefaz

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sincronizador SEFAZ via PyNFe")
    parser.add_argument("--status", action="store_true", help="Verifica apenas o status da SEFAZ")
    parser.add_argument("--sync", action="store_true", help="Baixa novos documentos fiscais")
    
    args = parser.parse_args()
    
    if args.status:
        verificar_status_sefaz()
    elif args.sync:
        baixar_notas_emitidas_contra_cnpj()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
