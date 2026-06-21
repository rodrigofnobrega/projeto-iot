import { MQTT_URL } from '../config.js'

const LABELS = {
  connecting: { text: 'Conectando…', cls: 'status--wait' },
  connected: { text: 'Conectado', cls: 'status--ok' },
  reconnecting: { text: 'Reconectando…', cls: 'status--wait' },
  offline: { text: 'Offline', cls: 'status--off' },
  error: { text: 'Erro', cls: 'status--off' },
}

export default function StatusBar({ status, lastError, count }) {
  const info = LABELS[status] || LABELS.error
  return (
    <header className="statusbar">
      <div className="statusbar__title">
        <span className="statusbar__dot" />
        Monitoramento IoT — MQTT
      </div>
      <div className="statusbar__right">
        <span className="statusbar__broker">{MQTT_URL}</span>
        <span className="statusbar__count">{count} leituras</span>
        <span className={`status ${info.cls}`} title={lastError || ''}>
          ● {info.text}
        </span>
      </div>
    </header>
  )
}
