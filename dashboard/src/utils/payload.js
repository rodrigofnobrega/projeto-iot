import { RANGES } from '../config.js'

const FORMATO_HORA = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/

export function validatePayload(raw) {
  let obj
  try {
    obj = typeof raw === 'string' ? JSON.parse(raw) : raw
  } catch {
    return { valid: false, error: 'JSON inválido' }
  }

  if (obj === null || typeof obj !== 'object') {
    return { valid: false, error: 'Payload não é um objeto' }
  }

  const { id_dispositivo, temperatura, umidade, dataHora } = obj

  if (typeof id_dispositivo !== 'string' || id_dispositivo.trim() === '') {
    return { valid: false, error: 'id_dispositivo ausente ou vazio' }
  }
  if (typeof temperatura !== 'number' || Number.isNaN(temperatura)) {
    return { valid: false, error: 'temperatura ausente ou não numérica' }
  }
  if (typeof umidade !== 'number' || Number.isNaN(umidade)) {
    return { valid: false, error: 'umidade ausente ou não numérica' }
  }
  if (typeof dataHora !== 'string' || !FORMATO_HORA.test(dataHora)) {
    return { valid: false, error: 'dataHora ausente ou fora do formato padrão' }
  }

  if (temperatura < RANGES.temperatura.min || temperatura > RANGES.temperatura.max) {
    return { valid: false, error: `temperatura fora da faixa (${temperatura})` }
  }
  if (umidade < RANGES.umidade.min || umidade > RANGES.umidade.max) {
    return { valid: false, error: `umidade fora da faixa (${umidade})` }
  }

  return { valid: true, data: { id_dispositivo, temperatura, umidade, dataHora } }
}
