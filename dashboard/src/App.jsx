import { useMQTT } from './hooks/useMQTT.js'
import StatusBar from './components/StatusBar.jsx'
import CurrentValues from './components/CurrentValues.jsx'
import SensorChart from './components/SensorChart.jsx'
import AnomalyAlert from './components/AnomalyAlert.jsx'
import DeviceControl from './components/DeviceControl.jsx'

export default function App() {
  const { status, readings, anomalies, lastError, clearAnomalies, publishCommand } = useMQTT()

  const last = readings.length ? readings[readings.length - 1] : null

  return (
    <div className="app">
      <StatusBar status={status} lastError={lastError} count={readings.length} />

      <main className="app__main">
        <CurrentValues reading={last} />

        <div className="grid">
          <div className="grid__col grid__col--main">
            <SensorChart readings={readings} />
          </div>
          <div className="grid__col grid__col--side">
            <DeviceControl status={status} onCommand={publishCommand} />
            <AnomalyAlert anomalies={anomalies} onClear={clearAnomalies} />
          </div>
        </div>
      </main>
    </div>
  )
}
