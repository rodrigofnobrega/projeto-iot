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
