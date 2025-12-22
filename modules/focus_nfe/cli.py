# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

from modules.focus_nfe.focus_client import FocusNFeClient


def _load_json_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise RuntimeError(f"Payload JSON deve ser um objeto (dict), recebido: {type(payload).__name__}")
    return payload


def _write_bytes(path: str, content: bytes) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="focus-nfe", description="CLI mínima para API Focus NFe")
    parser.add_argument("--base-url", default=os.getenv("FOCUS_NFE_BASE_URL"), help="Ex: https://api.focusnfe.com.br")
    parser.add_argument("--token", default=os.getenv("FOCUS_NFE_TOKEN"), help="Token da Focus NFe")
    parser.add_argument("--env", default=os.getenv("FOCUS_NFE_ENV"), help="producao|homologacao (usado se base-url não for informado)")
    parser.add_argument("--timeout-s", default=os.getenv("FOCUS_NFE_TIMEOUT_S") or "60", help="Timeout (segundos)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create", help="Cria/solicita emissão de um documento (ex: nfe)")
    p_create.add_argument("--doc", default="nfe", help="Tipo do documento: nfe, nfce, nfse, ...")
    p_create.add_argument("--ref", required=True, help="Referência (ref) única do documento")
    p_create.add_argument("--json", required=True, dest="json_path", help="Arquivo JSON com payload")

    p_status = sub.add_parser("status", help="Consulta status de um documento por ref")
    p_status.add_argument("--doc", default="nfe", help="Tipo do documento: nfe, nfce, nfse, ...")
    p_status.add_argument("--ref", required=True, help="Referência (ref) do documento")

    p_download = sub.add_parser("download", help="Baixa XML/PDF por ref")
    p_download.add_argument("--doc", default="nfe", help="Tipo do documento: nfe, nfce, nfse, ...")
    p_download.add_argument("--ref", required=True, help="Referência (ref) do documento")
    p_download.add_argument("--format", choices=["xml", "pdf"], default="xml", help="Formato do arquivo")
    p_download.add_argument("--out", required=True, help="Caminho de saída (ex: ./out/minha_nfe.xml)")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    token = (args.token or "").strip()
    if not token:
        print("ERRO: defina FOCUS_NFE_TOKEN (ou passe --token).", file=sys.stderr)
        return 2

    try:
        client = FocusNFeClient(
            token=token,
            base_url=(args.base_url or None),
            environment=(args.env or None),
            timeout=float(args.timeout_s),
        )

        if args.cmd == "create":
            payload = _load_json_file(args.json_path)
            response = client.create_document(args.doc, args.ref, payload)
            print(json.dumps(response.body, indent=2, ensure_ascii=False))
            return 0

        if args.cmd == "status":
            response = client.get_document(args.doc, args.ref)
            print(json.dumps(response.body, indent=2, ensure_ascii=False))
            return 0

        if args.cmd == "download":
            response = client.download_document(args.doc, args.ref, args.format)
            if not response.is_success:
                print(f"ERRO: HTTP {response.status_code} - {response.text}", file=sys.stderr)
                return 1
            _write_bytes(args.out, response.content)
            print(f"OK: salvo em {args.out}")
            return 0

        print("ERRO: comando não implementado.", file=sys.stderr)
        return 2

    except Exception as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
