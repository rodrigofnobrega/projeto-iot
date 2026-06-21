"""Mede a latência de entrega de mensagens pelo broker (ida e volta)."""
import time

from helpers import (
    BROKER_HOST, BROKER_PORT, TOPIC, QOS,
    make_client, broker_available, write_result,
)

N_MSGS = 500
LATENCY_LIMIT_MS = 150.0  


def run():
    if not broker_available():
        write_result(
            "test_latency.md", "Latência de Mensagens", "skip",
            {"mensagens": N_MSGS}, ["Broker indisponível — teste pulado."],
            "Suba o broker e rode novamente.",
        )
        return ("test_latency", None, "broker indisponível")

    topic = TOPIC + "/latency"
    enviados = {}       
    latencias = []      

    def on_message(c, u, msg):
        t_recv = time.perf_counter()
        seq = int(msg.payload.decode())
        if seq in enviados:
            latencias.append((t_recv - enviados[seq]) * 1000.0)

    c = make_client("test-latency")
    c.on_message = on_message
    c.connect(BROKER_HOST, BROKER_PORT, 60)
    c.loop_start()
    c.subscribe(topic, qos=QOS)
    time.sleep(0.5)

    for seq in range(N_MSGS):
        enviados[seq] = time.perf_counter()
        c.publish(topic, str(seq), qos=QOS)
        time.sleep(0.05)

    deadline = time.time() + 5
    while len(latencias) < N_MSGS and time.time() < deadline:
        time.sleep(0.05)

    c.loop_stop()
    c.disconnect()

    if not latencias:
        write_result(
            "test_latency.md", "Latência de Mensagens", "fail",
            {"mensagens": N_MSGS}, ["Nenhuma mensagem retornou."],
            "Não foi possível medir latência.",
        )
        return ("test_latency", False, "sem medições")

    media = sum(latencias) / len(latencias)
    mn, mx = min(latencias), max(latencias)
    ordenada = sorted(latencias)
    p95 = ordenada[min(len(ordenada) - 1, int(len(ordenada) * 0.95))]
    passed = media <= LATENCY_LIMIT_MS

    write_result(
        "test_latency.md", "Latência de Mensagens",
        "pass" if passed else "fail",
        {"mensagens": N_MSGS, "QoS": QOS, "limite média (ms)": LATENCY_LIMIT_MS},
        [
            f"Recebidas: {len(latencias)}/{N_MSGS}",
            f"Latência média: {media:.2f} ms",
            f"Mínima: {mn:.2f} ms | Máxima: {mx:.2f} ms",
            f"P95: {p95:.2f} ms",
        ],
        f"Latência média de {media:.2f} ms "
        + ("dentro" if passed else "ACIMA") + f" do limite de {LATENCY_LIMIT_MS} ms.",
    )
    return ("test_latency", passed, f"média={media:.2f}ms, p95={p95:.2f}ms")


if __name__ == "__main__":
    name, passed, summary = run()
    print(f"{name}: {passed} — {summary}")
