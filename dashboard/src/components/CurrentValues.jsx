import { formatDateTimeBR } from '../utils/format.js'

export default function CurrentValues({ reading }) {
  const temp = reading ? `${reading.temperatura.toFixed(1)} °C` : '—'
  const hum = reading ? `${reading.umidade.toFixed(1)} %` : '—'
  const when = reading ? formatDateTimeBR(reading.dataHora) : 'sem dados'
  const device = reading ? reading.id_dispositivo : '—'

  return (
    <section className="metrics">
      <div className="metric metric--temp">
        <span className="metric__label">Temperatura</span>
        <span className="metric__value">{temp}</span>
      </div>
      <div className="metric metric--hum">
        <span className="metric__label">Umidade</span>
        <span className="metric__value">{hum}</span>
      </div>
      <div className="metric metric--meta">
        <span className="metric__label">Dispositivo</span>
        <span className="metric__value metric__value--sm">{device}</span>
        <span className="metric__time">{when}</span>
      </div>
    </section>
  )
}
