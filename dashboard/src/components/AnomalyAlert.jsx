import { formatDateTimeBR } from '../utils/format.js'

export default function AnomalyAlert({ anomalies, onClear }) {
  return (
    <section className="card">
      <div className="card__header">
        <h2 className="card__title">Alertas de Anomalia</h2>
        {anomalies.length > 0 && (
          <button className="btn btn--ghost" onClick={onClear}>
            Limpar
          </button>
        )}
      </div>

      {anomalies.length === 0 ? (
        <p className="card__empty">Nenhuma anomalia detectada.</p>
      ) : (
        <ul className="anomaly-list">
          {anomalies.map((a, i) => (
            <li key={`${a.dataHora}-${a.tipo}-${i}`} className={`anomaly anomaly--${a.tipo}`}>
              <span className="anomaly__badge">{a.tipo}</span>
              <div className="anomaly__body">
                <strong>
                  {a.valor}
                  {a.tipo === 'temperatura' ? ' °C' : ' %'}
                </strong>
                <span className="anomaly__meta">média {a.media}</span>
                <span className="anomaly__time">{formatDateTimeBR(a.dataHora)}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
