import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { formatTimeBR } from '../utils/format.js'

export default function SensorChart({ readings }) {
  const data = readings.map((r) => ({
    hora: formatTimeBR(r.dataHora),
    temperatura: r.temperatura,
    umidade: r.umidade,
  }))

  return (
    <section className="card">
      <h2 className="card__title">Temperatura e Umidade — tempo real</h2>
      {data.length === 0 ? (
        <p className="card__empty">Aguardando leituras do sensor…</p>
      ) : (
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: -8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eaf0f7" />
            <XAxis dataKey="hora" tick={{ fontSize: 11, fill: '#93a3b8' }} minTickGap={32} stroke="#dce5f0" />
            <YAxis
              yAxisId="temp"
              domain={['auto', 'auto']}
              tick={{ fontSize: 11, fill: '#d18b62' }}
              stroke="#dce5f0"
              label={{ value: '°C', angle: 0, position: 'insideTopLeft', fill: '#d18b62' }}
            />
            <YAxis
              yAxisId="hum"
              orientation="right"
              domain={[0, 100]}
              tick={{ fontSize: 11, fill: '#5aa7b8' }}
              stroke="#dce5f0"
              label={{ value: '%', angle: 0, position: 'insideTopRight', fill: '#5aa7b8' }}
            />
            <Tooltip
              contentStyle={{ background: '#ffffff', border: '1px solid #e2eaf4', borderRadius: 10, boxShadow: '0 2px 8px rgba(80,110,150,0.12)' }}
              labelStyle={{ color: '#3a4a5e' }}
            />
            <Legend />
            <Line
              yAxisId="temp"
              type="monotone"
              dataKey="temperatura"
              name="Temperatura (°C)"
              stroke="#e6a17c"
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              yAxisId="hum"
              type="monotone"
              dataKey="umidade"
              name="Umidade (%)"
              stroke="#79c4d4"
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </section>
  )
}
