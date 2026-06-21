import { useState } from 'react'
import { COMMAND_TOPIC } from '../config.js'

export default function DeviceControl({ status, onCommand }) {
  const [feedback, setFeedback] = useState(null)
  const connected = status === 'connected'

  function solicitarLeitura() {
    const enviado = onCommand('1')
    setFeedback(enviado ? 'ok' : 'err')
    setTimeout(() => setFeedback(null), 2500)
  }

  return (
    <section className="card">
      <div className="card__header">
        <h2 className="card__title">Controle do Dispositivo</h2>
      </div>

      <button className="btn" onClick={solicitarLeitura} disabled={!connected}>
        Obter leitura
      </button>

      {!connected && (
        <p className="control__msg control__msg--muted">
          Conecte ao broker para enviar comandos.
        </p>
      )}
      {feedback === 'ok' && (
        <p className="control__msg control__msg--ok">Comando enviado ✓</p>
      )}
      {feedback === 'err' && (
        <p className="control__msg control__msg--err">
          Falha — sem conexão com o broker.
        </p>
      )}
    </section>
  )
}
