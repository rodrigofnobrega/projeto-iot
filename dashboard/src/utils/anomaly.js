import { ANOMALY_WINDOW, ANOMALY_STD_FACTOR, ANOMALY_MIN_DEVIATION } from '../config.js'

function meanStd(values) {
  const n = values.length
  
  if (n === 0) return { mean: 0, std: 0 }
  
  const mean = values.reduce((a, b) => a + b, 0) / n
  const variance = values.reduce((a, b) => a + (b - mean) ** 2, 0) / n

  return { mean, std: Math.sqrt(variance) }
}

export function detectAnomalies(history, reading) {
  const anomalies = []
  const minSamples = ANOMALY_WINDOW

  for (const field of ['temperatura', 'umidade']) {
    const baseline = history
      .filter((r) => !(r.anomaly && r.anomaly[field]))
      .slice(-ANOMALY_WINDOW)

    if (baseline.length < minSamples) continue

    const values = baseline.map((r) => r[field])
    const { mean, std } = meanStd(values)

    const deviation = Math.abs(reading[field] - mean)
    const minDeviation = ANOMALY_MIN_DEVIATION[field] ?? 0

    if (deviation >= minDeviation && deviation > ANOMALY_STD_FACTOR * std) {
      anomalies.push({
        tipo: field,
        valor: reading[field],
        media: Number(mean.toFixed(2)),
        dataHora: reading.dataHora,
        id_dispositivo: reading.id_dispositivo,
      })
    }
  }

  return anomalies
}
