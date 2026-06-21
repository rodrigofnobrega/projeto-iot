"""Simula falha de conexão e verifica a recuperação após reconexão."""
import time

from helpers import (
    BROKER_HOST, BROKER_PORT, TOPIC, QOS,
    make_client, broker_available, make_payload, write_result,
)


def _publica_recebe(sub, msg):
    """Publica `msg` por um cliente novo e espera o subscriber recebê-la."""
    antes = len(sub["recv"])
    pub = make_client("test-reconnect-pub")
    pub.connect(BROKER_HOST, BROKER_PORT, 60)
    pub.loop_start()
    pub.publish(TOPIC, msg, qos=QOS)
    deadline = time.time() + 5
    while len(sub["recv"]) == antes and time.time() < deadline:
        time.sleep(0.05)
    pub.loop_stop()
    pub.disconnect()
    return len(sub["recv"]) > antes


def run():
    if not broker_available():
        write_result(
            "test_reconnect.md", "Reconexão após Falha", "skip", {},
            ["Broker indisponível — teste pulado."],
            "Suba o broker e rode novamente.",
        )
        return ("test_reconnect", None, "broker indisponível")

    estado = {"recv": [], "reconnects": 0}

    def on_connect(c, u, flags, rc, props=None):
        c.subscribe(TOPIC, qos=QOS)

    def on_message(c, u, msg):
        estado["recv"].append(msg.payload.decode())

    c = make_client("test-reconnect-sub")
    c.on_connect = on_connect
    c.on_message = on_message
    c.connect(BROKER_HOST, BROKER_PORT, 60)
    c.loop_start()
    time.sleep(0.6)

    antes_ok = _publica_recebe(estado, make_payload(24.0, 55.0))

    c.disconnect()
    time.sleep(1.0)
    caiu = not c.is_connected()
    c.loop_stop()


    c.reconnect()
    estado["reconnects"] += 1
    c.loop_start()
    deadline = time.time() + 8

    while not c.is_connected() and time.time() < deadline:
        time.sleep(0.1)
    reconectou = c.is_connected()

    depois_ok = _publica_recebe(estado, make_payload(24.5, 56.0))

    c.loop_stop()
    c.disconnect()

    passed = antes_ok and caiu and reconectou and depois_ok
    write_result(
        "test_reconnect.md", "Reconexão após Falha",
        "pass" if passed else "fail",
        {"QoS": QOS},
        [
            f"Recebeu antes da queda: {antes_ok}",
            f"Conexão derrubada: {caiu}",
            f"Reconectou: {reconectou}",
            f"Recebeu após reconexão: {depois_ok}",
        ],
        "Recuperação após falha bem-sucedida (reassinou e voltou a receber)."
        if passed else "Falha na recuperação após queda de conexão.",
    )
    return ("test_reconnect", passed, f"antes={antes_ok}, depois={depois_ok}")


if __name__ == "__main__":
    name, passed, summary = run()
    print(f"{name}: {passed} — {summary}")
