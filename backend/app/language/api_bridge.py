
import json
import sys

from .errors import ErrorLenguaje
from .parser import analizar


def main():
    try:
        solicitud = json.loads(sys.stdin.read().lstrip('\ufeff'))
        comando = solicitud.get("command") if isinstance(solicitud, dict) else None
        if not isinstance(comando, str) or not comando.strip() or len(comando) > 300:
            salida = {"ok": False, "error": {"tipo": "Solicitud inválida", "mensaje": "Envía una instrucción de 1 a 300 caracteres."}}
        else:
            try:
                arbol = analizar(comando)
                salida = {"ok": True, "ast": arbol.a_dict()}
            except ErrorLenguaje as error:
                salida = {"ok": False, "error": error.a_dict()}
        print(json.dumps(salida, ensure_ascii=False))
    except (ValueError, TypeError, json.JSONDecodeError):
        print(json.dumps({"ok": False, "error": {"tipo": "Solicitud inválida", "mensaje": "JSON de entrada inválido."}}, ensure_ascii=False))
    except Exception:
        print(json.dumps({"ok": False, "error": {"tipo": "Error interno", "mensaje": "Error interno del analizador."}}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
