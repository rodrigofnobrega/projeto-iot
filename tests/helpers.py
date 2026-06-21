"""Utilitários compartilhados pelos testes do projeto IoT.

Centraliza: configuração do broker, validação de payload, detecção de
anomalia (espelha o algoritmo do dashboard) e gravação de resultados em
docs/resultados/ no formato .md exigido pelo CLAUDE.md.
"""
import json
import math
import os
import re
import socket
from datetime import datetime

import paho.mqtt.client as mqtt

# ===================== Configuração do broker =====================
BROKER_HOST = "localhost"
BROKER_PORT = 1883
WS_PORT = 9001
TOPIC = "imd/tec/com/iot/rodflaw"
QOS = 1

# ===================== Faixas válidas (DHT22) =====================
TEMP_MIN, TEMP_MAX = -40.0, 85.0
HUM_MIN, HUM_MAX = 0.0, 100.0
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

# ==================== Diretório com resultados =====================
RESULTS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "docs", "resultados")
)


# ---------------------------------------------------------------- payload
def make_payload(temperatura, umidade, device="esp32-01", when="2026-06-14T10:30:00"):
    return json.dumps(
        {
            "id_dispositivo": device,
            "temperatura": temperatura,
            "umidade": umidade,
            "dataHora": when,
        }
    )


# ---------------------------------------------------------------- broker
def make_client(client_id):
    """Cria um cliente paho-mqtt compatível com a API v2."""
    return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)


def broker_available(host=BROKER_HOST, port=BROKER_PORT, timeout=2.0):
    """Verifica rapidamente se o broker está aceitando conexões TCP."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


# ---------------------------------------------------------------- resultados
def write_result(filename, title, status, params, body_lines, conclusion):
    """Grava o resultado de um teste em docs/resultados/<filename>.md."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    icon = {"pass": "✅ PASSOU", "fail": "❌ FALHOU", "skip": "⚠️ PULADO"}.get(
        status, status
    )
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# Resultado — {title}",
        "",
        f"- **Data:** {now}",
        f"- **Status:** {icon}",
        f"- **Broker:** {BROKER_HOST}:{BROKER_PORT}",
        f"- **Tópico:** `{TOPIC}`",
        "",
        "## Parâmetros",
    ]
    for k, v in params.items():
        lines.append(f"- {k}: {v}")
    lines += ["", "## Resultado"]
    lines += [f"- {ln}" for ln in body_lines]
    lines += ["", "## Conclusão", conclusion, ""]
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path
