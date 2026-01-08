import argparse
import subprocess
import os
import sys

def run_test(script_path):
    print(f"\n🚀 Executando: {os.path.basename(script_path)}")
    try:
        # Usar o mesmo interpretador python atual
        result = subprocess.run([sys.executable, script_path], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Script falhou com código {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Script não encontrado: {script_path}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Ferramenta de Homologação FocusNFE")
    parser.add_argument(
        "--type", 
        choices=["nfse", "nfe", "nfce", "cte", "mdfe", "lifecycle", "all"],
        default="all",
        help="Tipo de documento ou teste para homologar"
    )
    
    args = parser.parse_args()
    
    test_dir = "test"
    mapping = {
        "nfse": "test_focus_nfse_emission.py",
        "nfe": "test_focus_nfe_emission.py",
        "nfce": "test_focus_nfce_emission.py",
        "cte": "test_focus_cte_emission.py",
        "mdfe": "test_focus_mdfe_emission.py",
        "lifecycle": "test_full_lifecycle.py"
    }

    print("========================================")
    print("   HOMOLOGAÇÃO FOCUSNFE - CONTABIL IA   ")
    print("========================================\n")

    if args.type == "all":
        success_count = 0
        total = len(mapping)
        for t in mapping.values():
            if run_test(os.path.join(test_dir, t)):
                success_count += 1
        print(f"\n📊 Resultado Final: {success_count}/{total} testes passaram.")
    else:
        script = mapping.get(args.type)
        if script:
            run_test(os.path.join(test_dir, script))
        else:
            print(f"❌ Tipo '{args.type}' não mapeado.")

if __name__ == "__main__":
    main()
