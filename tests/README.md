# Suíte de Testes

Testes automatizados do sistema IoT, em **Python + paho-mqtt**, cobrindo os
cenários da Etapa 4 do projeto e extras. Cada execução grava um relatório em
`docs/resultados/`.

## Pré-requisitos

```bash
pip install paho-mqtt
```

```bash
cd ../mosquitto && docker compose up -d
```

## Como rodar

```bash
# toda a suíte (gera docs/resultados/_resumo.md)
python3 run_tests.py

# um teste individual
python3 test_anomaly.py
```

## Testes disponíveis

| Arquivo | Descrição | Precisa do broker? |
| --- | --- | --- |
| `test_mqtt_payload.py` | valida estrutura, tipos e faixas do payload | não |
| `test_latency.py` | latência média/mín/máx/P95 das mensagens | sim |
| `test_multi_client.py` | múltiplos subscribers recebem a mesma mensagem | sim |
| `test_reconnect.py` | recuperação após queda e reconexão | sim |

¹ A lógica FIFO roda sem broker; o reenvio ordenado é validado contra o broker.

## Estrutura

- `helpers.py` — configuração do broker, validação de payload, detecção de
  anomalia e gravação de resultados (`docs/resultados/<nome>.md`).
- `run_tests.py` — runner que executa todos os testes e grava
  `docs/resultados/_resumo.md`.

## Resultados

Cada teste gera um `.md` em `docs/resultados/` com **data, parâmetros e
conclusão**. O `run_tests.py` adiciona um `_resumo.md` com a tabela geral
(passaram / falharam / pulados).
