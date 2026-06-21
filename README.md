# Definição de Projeto

**Disciplina:** IMD0907 - Tecnologias de Comunicação para Internet das Coisas - T01  
**Professora:** Fernanda de Araujo Miranda Tasso Salmoria  
**Alunos:** Rodrigo Ferreira e Flawbert Lorran  

---

## 1. Introdução
Este documento tem por finalidade definir como será realizado o desenvolvimento do projeto de monitoramento de temperatura com o sensor DHT22 e o microcontrolador ESP32 desenvolvido com MicroPython e utilizando o protocolo MQTT para visualizar os dados em uma plataforma Web.

## 2. Escopo e Objetivos do Projeto
O projeto consiste no desenvolvimento de uma solução de IoT que realiza a coleta de dados de temperatura e umidade do ar. Os objetivos específicos incluem:

* **Resiliência de Rede:** Garantir a persistência local e a integridade dos dados coletados mesmo em cenários de instabilidade de rede.
* **Análise Estatística:** Realizar a verificação se ocorreu alguma anomalia de acordo com a média dos últimos 50 dados.
* **Visualização:** Processar, armazenar de forma eficiente e visualizar os dados em tempo real por meio de um dashboard web.

## 3. Arquitetura do Sistema
A arquitetura é dividida em três camadas principais, garantindo o desacoplamento e a manutenibilidade do ecossistema:

### 3.1. Camada Física
Composta pelo ESP32 executando MicroPython. Esta camada é responsável pela leitura física do sensor DHT22, validação inicial dos dados e transmissão segura via protocolo MQTT.

### 3.2. Camada de Aplicação
Uma interface web que consome dados via MQTT para exibição e controle do microcontrolador de forma remota.

## 4. Recursos Extras

### 4.1. Garantir Integridade dos Dados
> **Mecanismo de Contingência (Buffer Local):** > Em caso de perda de conexão Wi-Fi ou falha no broker, o firmware em MicroPython grava as leituras estruturadas em formato JSON ou CSV diretamente no sistema de arquivos local do ESP32. Assim que a conectividade é restabelecida, é realizado o envio de todos os dados que foram coletados durante esse período de indisponibilidade.

### 4.2. Detectar Anomalias
O backend executa uma análise estatística simples com base na média móvel dos últimos 50 dados enviados para verificar e alertar se ocorreu alguma anomalia na leitura dos dados.

---

## 5. Estrutura do repositório

```
projeto-iot/
├── firmware/        ESP32 (Wokwi, MicroPython) — src/main.cpp + Wokwi
├── mosquitto/       broker Mosquitto (docker-compose + mosquitto.conf)
├── dashboard/       app React (Vite + MQTT.js + Recharts)
├── tests/           suíte de testes Python (paho-mqtt)
└── docs/            documentação e resultados dos testes
```

## 6. Como executar

### 6.1. Broker (Mosquitto)

```bash
cd mosquitto
docker compose up -d          # MQTT (1883) e WebSocket (9001)
docker compose logs -f
```
OBS: Necessário apenas se for executar o código local, mas como está sendo utilizado o Wokwi não é possível se conectar ao broker no localhost, sendo utilizado o `test.mosquitto.org`

### 6.2. Firmware (ESP32)

Copiar código main.py e diagram.json e exextuar na plataforma Wokwi.

### 6.3. Dashboard (React)

```bash
cd dashboard
npm install
npm run dev                   # http://localhost:5173
```

O broker fica em `dashboard/src/config.js` — use o **mesmo** que o firmware
(`wss://broker.hivemq.com:8884/mqtt` para Wokwi, ou `ws://localhost:9001` local).

### 6.4. Testes

```bash
cd tests
python3 run_tests.py          # roda a suíte e grava docs/resultados/
```

## 7. Verificar mensagens manualmente

```bash
mosquitto_sub -h test.mosquitto.org -t "imd/tec/com/iot/rodflaw" -v
mosquitto_pub -h test.mosquitto.org -t "imd/tec/com/iot/rodflaw" \
  -m '{"id_dispositivo":"esp32-01","temperatura":25.4,"umidade":68.2,"dataHora":"2026-06-14T10:30:00"}'
```

## 8. Documentação completa

Toda a documentação do projeto está consolidada em um único arquivo `realtorio_final.md` no diretório `docs`:

- [docs/relatorio_final.md](docs/relatorio_final.md) — relatório técnico final
- [docs/resultados/](docs/resultados/) — resultados das execuções dos testes
