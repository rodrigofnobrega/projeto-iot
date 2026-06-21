from machine import Pin
from time import sleep, ticks_ms, ticks_diff, localtime
from dht import DHT22
import network
import ntptime
import json
from umqtt.simple import MQTTClient

WIFI_SSID = 'Wokwi-GUEST'
WIFI_PASS = ''

MQTT_BROKER = 'test.mosquitto.org'
MQTT_PORT = 1883

MQTT_TOPIC_DADOS = 'imd/tec/com/iot/rodflaw'
MQTT_TOPIC_COMANDO = 'imd/tec/com/iot/rodflaw/comando'

CLIENT_ID = 'esp32-rodflaw'
DEVICE_ID = 'esp32-01'

DHT_PIN = 19
INTERVALO_MS = 2000  

sensor = DHT22(Pin(DHT_PIN))

ler_sensor = False


def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando ao WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            sleep(0.5)
    print('WiFi conectado:', wlan.ifconfig()[0])


def sincronizar_relogio():
    try:
        ntptime.settime()
        print('Relogio sincronizado via NTP')
    except Exception as e:
        print('Falha ao sincronizar NTP:', e)


def timestamp_iso():
    t = localtime()
    return '%04d-%02d-%02dT%02d:%02d:%02d' % (t[0], t[1], t[2], t[3], t[4], t[5])


def callback(topic, msg):
    global ler_sensor
    print('Mensagem recebida em %s: %s' % (topic.decode(), msg.decode()))
    if msg == b'1':
        ler_sensor = True


def conectar_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(callback)
    client.connect()
    client.subscribe(MQTT_TOPIC_COMANDO)
    print('Conectado ao broker MQTT:', MQTT_BROKER)
    print('Inscrito no tópico de comando:', MQTT_TOPIC_COMANDO)
    return client


def publicar_leitura(client, origem=''):
    sensor.measure()
    temp = sensor.temperature()
    humidity = sensor.humidity()

    print('Temperature: %2.2f C' % temp)
    print('Humidity: %2.2f %%' % humidity)

    mensagem = json.dumps({
        'id_dispositivo': DEVICE_ID,
        'temperatura': round(temp, 2),
        'umidade': round(humidity, 2),
        'dataHora': timestamp_iso(),
    })

    try:
        client.publish(MQTT_TOPIC_DADOS, mensagem)
        print('Publicado (%s): %s' % (origem, mensagem))
    except OSError:
        print('Falha ao publicar, reconectando...')
        return conectar_mqtt()
    return client


conectar_wifi()
sincronizar_relogio()
client = conectar_mqtt()

ultima_publicacao = ticks_ms()

while True:
    try:
        client.check_msg()
    except OSError:
        print('Falha na conexão, reconectando...')
        client = conectar_mqtt()

    if ticks_diff(ticks_ms(), ultima_publicacao) >= INTERVALO_MS:
        client = publicar_leitura(client, origem='automatico')
        ultima_publicacao = ticks_ms()

    if ler_sensor:
        ler_sensor = False
        client = publicar_leitura(client, origem='comando')

    sleep(0.1)
