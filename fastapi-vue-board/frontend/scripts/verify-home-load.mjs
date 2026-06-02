import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const scriptDir = dirname(fileURLToPath(import.meta.url))
const homeViewPath = resolve(scriptDir, '../src/views/HomeView.vue')
const source = readFileSync(homeViewPath, 'utf8')

const checks = [
  {
    name: 'home job request avoids external APIs',
    pass: /api\.get\('\/jobs\/',\s*\{\s*params:\s*\{[^}]*include_external:\s*false/s.test(source),
  },
  {
    name: 'home contest request avoids external APIs',
    pass: /api\.get\('\/contests\/',\s*\{\s*params:\s*\{[^}]*include_external:\s*false/s.test(source),
  },
  {
    name: 'home reveal observer initializes before data fetch completes',
    pass: /onMounted\(\(\)\s*=>\s*\{\s*initRevealObserver\(\)\s*fetchHomeData\(\)/s.test(source),
  },
  {
    name: 'home data requests are not serialized',
    pass: /Promise\.allSettled\(/.test(source),
  },
]

const failures = checks.filter((check) => !check.pass)

if (failures.length) {
  console.error('Home load verification failed:')
  for (const failure of failures) console.error(`- ${failure.name}`)
  process.exit(1)
}

console.log('Home load verification passed.')
