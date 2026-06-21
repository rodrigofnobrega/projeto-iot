export function formatDateTimeBR(iso) {
  if (typeof iso !== 'string' || iso.length < 19) return iso || '—'
  const [date, time] = iso.split('T')
  const [y, m, d] = date.split('-')
  return `${d}/${m}/${y} ${time.slice(0, 8)}`
}

export function formatTimeBR(iso) {
  if (typeof iso !== 'string' || iso.length < 19) return iso
  return iso.slice(11, 19)
}
