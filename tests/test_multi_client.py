"""Testa múltiplos subscribers recebendo a mesma mensagem simultaneamente."""
import time

from helpers import (
    BROKER_HOST, BROKER_PORT, TOPIC, QOS,
    make_client, broker_available, make_payload, write_result,
)

N_SUBS = 3


def run():
    if not broker_available():
        write_result(
            "test_multi_client.md", "Múltiplos Clientes", "skip",
            {"subscribers": N_SUBS}, ["Broker indisponível — teste pulado."],
            "Suba o broker e rode novamente.",
        )
        return ("test_multi_client", None, "broker indisponível")

    recebidas = [[] for _ in range(N_SUBS)]
    subs = []
    for i in range(N_SUBS):
        c = make_client(f"test-sub-{i}")
        c.user_data_set(i)
        c.on_message = lambda cl, idx, msg: recebidas[idx].append(msg.payload.decode())
        c.connect(BROKER_HOST, BROKER_PORT, 60)
        c.loop_start()
        c.subscribe(TOPIC, qos=QOS)
        subs.append(c)
    time.sleep(0.8)  

    pub = make_client("test-pub")
    pub.connect(BROKER_HOST, BROKER_PORT, 60)
    pub.loop_start()
    enviado = make_payload(26.1, 70.0)
    pub.publish(TOPIC, enviado, qos=QOS)

    deadline = time.time() + 5
    while any(len(r) == 0 for r in recebidas) and time.time() < deadline:
        time.sleep(0.05)

    for c in subs + [pub]:
        c.loop_stop()
        c.disconnect()

    receberam = sum(1 for r in recebidas if r and r[0] == enviado)
    passed = receberam == N_SUBS
    write_result(
        "test_multi_client.md", "Múltiplos Clientes",
        "pass" if passed else "fail",
        {"subscribers": N_SUBS, "QoS": QOS},
        [f"Subscriber {i} recebeu: {bool(recebidas[i])}" for i in range(N_SUBS)]
        + [f"Total que recebeu corretamente: {receberam}/{N_SUBS}"],
        "Todos os subscribers receberam a mensagem." if passed
        else "Nem todos os subscribers receberam a mensagem.",
    )
    return ("test_multi_client", passed, f"{receberam}/{N_SUBS} receberam")


if __name__ == "__main__":
    name, passed, summary = run()
    print(f"{name}: {passed} — {summary}")
