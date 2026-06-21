import { useCallback, useEffect, useRef, useState } from 'react'
import mqtt from 'mqtt'
import { MQTT_URL, DATA_TOPIC, COMMAND_TOPIC, MQTT_QOS, MAX_HISTORY } from '../config.js'
import { validatePayload } from '../utils/payload.js'
import { detectAnomalies } from '../utils/anomaly.js'

export function useMQTT() {
  const [status, setStatus] = useState('connecting')
  const [readings, setReadings] = useState([])   
  const [anomalies, setAnomalies] = useState([])
  const [lastError, setLastError] = useState(null)
  const clientRef = useRef(null)
  const historyRef = useRef([])

  useEffect(() => {
    const client = mqtt.connect(MQTT_URL, {
      reconnectPeriod: 3000,
      connectTimeout: 8000,
      clean: true,
    })
    clientRef.current = client

    client.on('connect', () => {
      setStatus('connected')
      client.subscribe(DATA_TOPIC, { qos: MQTT_QOS })
    })
    client.on('reconnect', () => setStatus('reconnecting'))
    client.on('offline', () => setStatus('offline'))
    client.on('close', () => setStatus((s) => (s === 'connected' ? 'offline' : s)))
    client.on('error', (err) => {
      setStatus('error')
      setLastError(err?.message || String(err))
    })

    client.on('message', (topic, message) => {
      if (topic !== DATA_TOPIC) return

      const result = validatePayload(message.toString())
      if (!result.valid) {
        console.warn('[MQTT] Payload inválido descartado:', result.error)
        return
      }

      const reading = { ...result.data, recvAt: Date.now() }

      const found = detectAnomalies(historyRef.current, reading)
      if (found.length > 0) {
        setAnomalies((prev) => [...found, ...prev].slice(0, 50))
      }

      reading.anomaly = {
        temperatura: found.some((a) => a.tipo === 'temperatura'),
        umidade: found.some((a) => a.tipo === 'umidade'),
      }

      const next = [...historyRef.current, reading].slice(-MAX_HISTORY)
      historyRef.current = next
      setReadings(next)
    })

    return () => {
      client.end(true)
      clientRef.current = null
    }
  }, [])

  const clearAnomalies = useCallback(() => setAnomalies([]), [])

  const publishCommand = useCallback((payload = '1') => {
    const client = clientRef.current
    if (!client || !client.connected) return false
    client.publish(COMMAND_TOPIC, String(payload), { qos: MQTT_QOS })
    return true
  }, [])

  return { status, readings, anomalies, lastError, clearAnomalies, publishCommand }
}
