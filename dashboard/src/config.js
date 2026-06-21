export const MQTT_URL = 'wss://test.mosquitto.org:8081'
export const DATA_TOPIC = 'imd/tec/com/iot/rodflaw'
export const COMMAND_TOPIC = 'imd/tec/com/iot/rodflaw/comando'
export const MQTT_QOS = 1
export const MAX_HISTORY = 100
export const ANOMALY_WINDOW = 20     
export const ANOMALY_STD_FACTOR = 2   

export const ANOMALY_MIN_DEVIATION = {
  temperatura: 3.0,   
  umidade: 3.0,       
}

// Faixas válidas de payload (DHT22).
export const RANGES = {
  temperatura: { min: -40.0, max: 85.0 },
  umidade: { min: 0.0, max: 100.0 },
}
