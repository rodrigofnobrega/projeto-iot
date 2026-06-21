"""Runner geral: executa todos os testes e grava um resumo em docs/resultados/."""
import os
import sys
from datetime import datetime

# garante import dos módulos irmãos quando rodado de qualquer diretório
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import test_latency
import test_multi_client
import test_reconnect
from helpers import RESULTS_DIR, broker_available, BROKER_HOST, BROKER_PORT

TESTES = [
    test_latency,
    test_multi_client,
    test_reconnect,
]


def main():
    print(f"Broker {BROKER_HOST}:{BROKER_PORT} ->",
          "disponível" if broker_available() else "INDISPONÍVEL")
    print("=" * 60)

    resultados = []
    for mod in TESTES:
        try:
            nome, passou, resumo = mod.run()
        except Exception as e: 
            nome, passou, resumo = mod.__name__, False, f"exceção: {e}"
        resultados.append((nome, passou, resumo))
        status = {True: "PASSOU", False: "FALHOU", None: "PULADO"}[passou]
        print(f"[{status:^7}] {nome:<22} {resumo}")

    passaram = sum(1 for _, p, _ in resultados if p is True)
    falharam = sum(1 for _, p, _ in resultados if p is False)
    pulados = sum(1 for _, p, _ in resultados if p is None)
    print("=" * 60)
    print(f"Total: {len(resultados)} | Passaram: {passaram} | "
          f"Falharam: {falharam} | Pulados: {pulados}")

    # resumo em markdown
    os.makedirs(RESULTS_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linhas = [
        "# Resumo da Execução dos Testes",
        "",
        f"- **Data:** {now}",
        f"- **Broker:** {BROKER_HOST}:{BROKER_PORT}",
        f"- **Passaram:** {passaram} | **Falharam:** {falharam} | **Pulados:** {pulados}",
        "",
        "| Teste | Status | Resumo |",
        "| --- | --- | --- |",
    ]
    for nome, passou, resumo in resultados:
        status = {True: "✅ PASSOU", False: "❌ FALHOU", None: "⚠️ PULADO"}[passou]
        linhas.append(f"| {nome} | {status} | {resumo} |")
    linhas.append("")
    with open(os.path.join(RESULTS_DIR, "_resumo.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    return 0 if falharam == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
