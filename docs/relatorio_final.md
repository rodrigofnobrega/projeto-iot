# Relatório Técnico Final

**Disciplina:** IMD0907 — Tecnologias de Comunicação para IoT
**Instituição:** UFRN · Instituto Metrópole Digital
**Professora:** Fernanda Tasso Salmoria
**Projeto:** Sistema de Monitoramento Inteligente com MQTT

---

## 1. Introdução

Este projeto implementa um sistema IoT completo de **monitoramento de
temperatura e umidade**, da coleta física do dado até a visualização em tempo
real, usando o protocolo **MQTT** em ambiente simulado pela plataforma Wokwi. O sistema 
é dividido em três camadas independentes — sensor, broker e dashboard — que se
comunicam exclusivamente por mensagens MQTT.

Além do fluxo de telemetria sensor → dashboard, o sistema oferece **controle
remoto**: o dashboard publica comandos em um tópico próprio para solicitar uma
leitura imediata do microcontrolador.

## 2. Objetivos

- Coletar temperatura e umidade com um sensor DHT22 acoplado a um ESP32.
- Transmitir as leituras via MQTT, com validação rigorosa do payload.
- Intermediar a comunicação por um broker MQTT público (`test.mosquitto.org`).
- Visualizar os dados em tempo real em um dashboard web, com detecção de
  anomalias.
- Permitir o **controle remoto** do dispositivo a partir do dashboard.
- Validar o sistema com uma suíte de testes automatizados.

---

## 3. Arquitetura

O sistema é organizado em três camadas que se comunicam exclusivamente por MQTT:

```
┌────────────────────────┐   publish    ┌──────────────────────┐   subscribe   ┌──────────────────────────┐
│   Camada Física         │ ───────────▶ │  Camada de Aplicação  │ ────────────▶ │  Camada de Visualização   │
│  ESP32 + DHT22          │  dados        │  Broker MQTT          │  WebSocket    │  Dashboard React          │
│  (MicroPython)          │ ◀─────────── │  test.mosquitto.org   │  (wss :8081)  │  (MQTT.js + Recharts)     │
└────────────────────────┘  comando      └──────────────────────┘               └──────────────────────────┘
        TCP :1883            (controle remoto: dashboard → ESP32)
```

- **Publisher / Subscriber (ESP32):** lê o sensor, valida e publica o payload
  JSON no tópico de dados; e **assina o tópico de comando** para receber
  solicitações do dashboard.
- **Broker (`test.mosquitto.org`):** intermedia todas as mensagens.
- **Subscriber / Publisher (dashboard):** assina o tópico de dados via WebSocket,
  exibe os dados em gráfico, valida cada mensagem, detecta anomalias e **publica
  comandos** no tópico de comando.

### 3.1 Camada Física (firmware)

- **Hardware:** ESP32 (DevKit) + sensor DHT22 no **pino GPIO 19**.
- **Linguagem / runtime:** **MicroPython** (arquivo único `firmware/main.py`).
- **Simulação:** Wokwi (`firmware/diagram.json`), com WiFi `Wokwi-GUEST`.
- **Bibliotecas:** `dht` (DHT22), `network` (WiFi), `ntptime` (relógio),
  `umqtt.simple` (cliente MQTT) e `json`.

Fluxo principal do `firmware/main.py`:

1. **Conectividade** — conecta ao WiFi (`Wokwi-GUEST`) e ao broker MQTT;
   sincroniza o relógio via **NTP** (`ntptime.settime()`).
2. **Assinatura de comando** — assina `imd/tec/com/iot/rodflaw/comando`.
3. **Leitura** — lê temperatura e umidade do DHT22.
4. **Timestamp** — gera `dataHora` em ISO 8601 a partir do relógio sincronizado.
5. **Publicação** — monta o JSON com `json.dumps` e publica no tópico de dados,
   automaticamente **a cada 2 segundos** (`INTERVALO_MS = 2000`).
6. **Reconexão** — em falha de rede (`OSError`), reconecta ao broker e segue.
7. **Comando** — a cada ciclo chama `check_msg()`; ao receber `"1"` no tópico de
   comando, dispara uma leitura/publicação imediata além do ciclo automático.

### 3.2 Camada de Aplicação (broker)

- **Broker:** **`test.mosquitto.org`**.
- **Portas utilizadas:**

  | Porta | Transporte | Quem usa |
  | --- | --- | --- |
  | 1883 | MQTT sobre TCP | firmware (ESP32) |
  | 8081 | MQTT sobre WebSocket seguro (**wss**) | dashboard (navegador) |

- **Sem autenticação:** o broker de testes na porta escolhida é aberto e naõ necessita de autenticação.

> A suíte de testes automatizados (seção 7) aponta para o broker configurado em
> `tests/helpers.py` (`BROKER_HOST`), por padrão um **Mosquitto local** (via
> Docker, em `mosquitto/`), o que permite medir latência sem o ruído da
> internet. Basta alterar `BROKER_HOST` para apontá-la a `test.mosquitto.org`.

### 3.3 Camada de Visualização (dashboard)

- **Stack:** React + Vite + MQTT.js + Recharts.
- **Conexão:** WebSocket (`wss://test.mosquitto.org:8081`) e configuração centralizada em `dashboard/src/config.js` (sem `.env`).
- **Componentes (`src/components/`):**
  - `StatusBar` — status da conexão MQTT e contagem de leituras.
  - `CurrentValues` — última leitura em destaque (datas em pt-BR).
  - `SensorChart` — gráfico em tempo real de temperatura e umidade.
  - `AnomalyAlert` — alertas de anomalia (valor, tipo e timestamp).
  - `DeviceControl` — **controle remoto**: botão que publica comando para o ESP32.
- **Lógica (`src/utils/` e `src/hooks/`):**
  - `payload.js` — valida toda mensagem recebida antes de exibir.
  - `anomaly.js` — detecção de anomalias por média móvel (seção 6).
  - `format.js` — formatação de datas no padrão pt-BR.
  - `useMQTT.js` — hook que gerencia conexão, assinatura, recepção, detecção de
    anomalia e a publicação de comandos (`publishCommand`).

---

## 4. Protocolo MQTT

### 4.1 O que é MQTT

**MQTT** (Message Queuing Telemetry Transport) é um protocolo de mensageria leve
no padrão **publish/subscribe**, projetado para dispositivos com recursos
limitados e redes instáveis. Em vez de o sensor
falar diretamente com o dashboard, ambos se comunicam por um intermediário, o
**broker**: o *publisher* publica em um **tópico**, o broker distribui, e os
*subscribers* que assinam aquele tópico recebem as mensagens. Esse desacoplamento
permite vários consumidores simultâneos sem que o sensor saiba quem são.

### 4.2 Tópicos

| Tópico | Direção | Uso |
| --- | --- | --- |
| `imd/tec/com/iot/rodflaw` | ESP32 → dashboard | leituras do sensor (temperatura/umidade) |
| `imd/tec/com/iot/rodflaw/comando` | dashboard → ESP32 | **controle remoto** (`"1"` = leitura imediata) |

Tópicos MQTT são hierárquicos (separados por `/`). O curinga `#` (multinível)
permite assinar tudo abaixo de um nível: `mosquitto_sub -t 'imd/tec/com/iot/rodflaw/#'`.

### 4.3 Payload JSON padrão

Toda leitura é publicada como JSON neste formato **obrigatório**:

```json
{
  "id_dispositivo": "esp32-01",
  "temperatura": 25.4,
  "umidade": 68.2,
  "dataHora": "2026-06-14T10:30:00"
}
```

Regras de validação:

| Campo | Tipo | Regra |
| --- | --- | --- |
| `id_dispositivo` | string | não pode ser vazia |
| `temperatura` | float | entre **-40.0 e 85.0 °C** (faixa do DHT22) |
| `umidade` | float | entre **0.0 e 100.0 %** |
| `dataHora` | string | ISO 8601 — `YYYY-MM-DDTHH:MM:SS` |

O tópico de **comando** usa um payload simples (texto): o valor `"1"` solicita
uma leitura imediata ao ESP32.

### 4.4 Qualidade de Serviço (QoS)

O MQTT define três níveis de garantia de entrega: **QoS 0** (*at most once*, sem
confirmação), **QoS 1** (*at least once*, com confirmação, pode duplicar) e
**QoS 2** (*exactly once*, handshake completo). Neste projeto:

- As **assinaturas** do dashboard e dos testes usam **QoS 1**.
- A **publicação do firmware** usa `umqtt.simple`, que publica em **QoS 0**.
  Para o intervalo de 2 s e o ambiente do projeto, isso é adequado; entrega
  garantida na publicação exigiria `umqtt.robust` ou QoS explícito.

### 4.5 Reconexão

Tanto o firmware quanto o dashboard tratam quedas de conexão:

- **Firmware:** em falha de rede ao publicar ou checar mensagens,
  reconecta ao broker e reassina o tópico de comando, retomando o ciclo.
- **Dashboard:** o MQTT.js reconecta automaticamente e
  reassina o tópico de dados ao reconectar; a `StatusBar` reflete o estado em
  tempo real (`connecting` / `connected` / `reconnecting` / `offline` / `error`).

### 4.6 Comandos úteis (linha de comando)

```bash
# escutar o tópico de dados do projeto
mosquitto_sub -h test.mosquitto.org -t "imd/tec/com/iot/rodflaw" -v

# publicar uma leitura de teste
mosquitto_pub -h test.mosquitto.org -t "imd/tec/com/iot/rodflaw" \
  -m '{"id_dispositivo":"esp32-01","temperatura":25.4,"umidade":68.2,"dataHora":"2026-06-14T10:30:00"}'

# enviar comando de leitura imediata para o ESP32
mosquitto_pub -h test.mosquitto.org -t "imd/tec/com/iot/rodflaw/comando" -m "1"
```

---

## 5. Validação de dados

A validação acontece em **dois pontos**, garantindo robustez:

1. **No firmware**, ao construir o payload — os valores vêm do DHT22 e são
   formatados no padrão JSON obrigatório antes de publicar.
2. **No dashboard**, ao receber (`validatePayload`) — protege a visualização de
   mensagens inválidas vindas de **qualquer** publisher no tópico, o que é
   especialmente importante num broker público e compartilhado.

Regras: `id_dispositivo` não vazio; `temperatura` em [-40, 85]; `umidade` em
[0, 100]; `dataHora` em ISO 8601. Mensagens inválidas são **logadas e
descartadas**. Por isso, por exemplo, uma
umidade fora da faixa publicada por outro cliente do broker público não aparece
no dashboard.

---

## 6. Detecção de anomalias

O dashboard mantém uma janela das **últimas leituras** (configurável em
`config.js`, atualmente `ANOMALY_WINDOW = 20`) e, para cada campo
(temperatura e umidade), calcula a média e o desvio-padrão. Uma nova leitura é
marcada como anomalia somente quando satisfaz **dois critérios simultâneos**:

1. **Critério estatístico (z-score):** desviar **mais de 2 desvios-padrão**
   (`ANOMALY_STD_FACTOR`) da média da janela.
2. **Zona morta (desvio absoluto mínimo):** afastar-se da média pelo menos
   `ANOMALY_MIN_DEVIATION` (3,0 °C para temperatura, 3,0 % para umidade).

A zona morta corrige um problema clássico do z-score puro: quando a série é
muito estável, o desvio-padrão tende a zero e o limiar estatístico fica
microscópico, fazendo qualquer flutuação mínima ser sinalizada como anomalia. O
desvio absoluto mínimo descarta esse ruído.

Além disso, o **baseline exclui as leituras já marcadas como anomalia**. Sem
isso, valores anômalos sustentados entrariam na janela, deslocariam a média e
deixariam de ser detectados (só o primeiro seria sinalizado). Com a exclusão,
uma anomalia que persiste continua sendo apontada. Para iniciar a análise, é
exigida a janela cheia de leituras normais (`minSamples = ANOMALY_WINDOW`).

O alerta (`AnomalyAlert`) exibe valor, tipo (temperatura/umidade) e timestamp,
sem bloquear o fluxo normal do gráfico.

---

## 7. Controle remoto do dispositivo

O dashboard permite acionar o ESP32 remotamente via MQTT:

- O componente `DeviceControl` exibe um botão que chama `publishCommand('1')`
  (no hook `useMQTT`), publicando `"1"` em `imd/tec/com/iot/rodflaw/comando`.
- O firmware, inscrito nesse tópico, recebe a mensagem em seu `callback`,
  reconhece o valor `"1"` e dispara uma **leitura/publicação imediata**, sem
  esperar o ciclo automático de 2 s.
- O botão fica **desabilitado enquanto não há conexão** com o broker, e exibe
  feedback de sucesso/falha ao enviar o comando.

Esse caminho fecha o ciclo bidirecional do sistema: além de receber telemetria,
o usuário pode comandar o dispositivo.

---

## 8. Testes

A suíte em `tests/` (Python + paho-mqtt) valida o comportamento do sistema sobre
o broker. Cada execução grava um relatório em `docs/resultados/*.md`, e
`run_tests.py` gera um resumo consolidado em `docs/resultados/_resumo.md`.

| Teste | O que valida |
| --- | --- |
| `test_latency.py` | latência de entrega (média/mín/máx/P95) com 500 mensagens |
| `test_multi_client.py` | múltiplos subscribers recebendo a mesma mensagem |
| `test_reconnect.py` | recuperação após queda e reconexão (reassina e volta a receber) |

### 8.1 Descrição dos testes

- **Latência (`test_latency.py`):** publica 500 mensagens sequenciais em um
  subtópico de latência e mede o tempo de ida e volta de cada uma, reportando
  média, mínima, máxima e P95. Passa se a média ficar dentro do limite
  (150 ms).
- **Múltiplos clientes (`test_multi_client.py`):** conecta 3 subscribers ao
  mesmo tópico, publica uma mensagem e verifica que **todos** a recebem —
  demonstrando o desacoplamento publish/subscribe.
- **Reconexão (`test_reconnect.py`):** confirma que o subscriber recebe antes da
  queda, derruba a conexão de propósito, reconecta reiniciando o loop de rede
  (reassinando via `on_connect`) e confirma que volta a receber.

### 8.2 Resultados obtidos

Execução em 2026-06-21, contra um Mosquitto local (`localhost:1883`), QoS 1 —
**3/3 testes aprovados**:

| Teste | Status | Resumo |
| --- | --- | --- |
| `test_latency` | ✅ PASSOU | média = 0,71 ms · P95 = 1,02 ms · 500/500 recebidas |
| `test_multi_client` | ✅ PASSOU | 3/3 subscribers receberam |
| `test_reconnect` | ✅ PASSOU | recebeu antes e depois da queda |

> A latência sub-milissegundo reflete o broker local usado pela suíte. Contra o
> `test.mosquitto.org` (broker público na internet) os tempos são naturalmente
> maiores, sujeitos à latência de rede.

---

## 9. Como executar

```bash
# 1. Firmware — simular no Wokwi (importar firmware/diagram.json + main.py)
#    ou gravar o main.py no ESP32 real com MicroPython.
#    Já aponta para test.mosquitto.org; nenhum broker precisa ser iniciado.

# 2. Dashboard
cd dashboard && npm install && npm run dev
#    Já configurado para wss://test.mosquitto.org:8081 em src/config.js

# 3. Testes (broker padrão em tests/helpers.py = localhost)
cd mosquitto && docker compose up -d     # sobe o Mosquitto local p/ os testes
cd ../tests && python3 run_tests.py      # gera docs/resultados/_resumo.md
```

---

## 11. Conclusão

O projeto entrega um pipeline IoT funcional e desacoplado: coleta física em
**MicroPython** no ESP32, transmissão via **MQTT** por um broker público
(`test.mosquitto.org`), visualização em tempo real no dashboard React, detecção
de anomalias por média móvel e **controle remoto** do dispositivo via tópico de
comando. A validação de dados em ambas as pontas e a suíte de testes
automatizados (latência, múltiplos clientes e reconexão, todos aprovados)
demonstram, na prática, os conceitos de mensageria publish/subscribe, qualidade
de serviço, comunicação bidirecional e resiliência de conexão estudados na
disciplina.
