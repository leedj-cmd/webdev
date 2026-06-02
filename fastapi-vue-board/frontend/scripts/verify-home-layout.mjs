import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const scriptDir = dirname(fileURLToPath(import.meta.url))
const homeViewPath = resolve(scriptDir, '../src/views/HomeView.vue')
const navbarPath = resolve(scriptDir, '../src/components/Navbar.vue')
const loginViewPath = resolve(scriptDir, '../src/views/LoginView.vue')
const registerViewPath = resolve(scriptDir, '../src/views/RegisterView.vue')
const adminRegisterViewPath = resolve(scriptDir, '../src/views/AdminRegisterView.vue')
const source = readFileSync(homeViewPath, 'utf8')
const navbarSource = readFileSync(navbarPath, 'utf8')
const loginSource = readFileSync(loginViewPath, 'utf8')
const registerSource = readFileSync(registerViewPath, 'utf8')
const adminRegisterSource = readFileSync(adminRegisterViewPath, 'utf8')

const communityRule = source.match(/\.panel-community\s*\{(?<body>[^}]*)\}/)
const desktopCommunitySpansAllColumns = /grid-column\s*:\s*span\s+2/.test(communityRule?.groups?.body || '')

const checks = [
  {
    name: 'dashboard uses independent columns instead of shared grid rows',
    pass: /class="dashboard-column dashboard-column-main"/.test(source)
      && /class="dashboard-column dashboard-column-side"/.test(source),
  },
  {
    name: 'dashboard columns stack cards without row-height gaps',
    pass: /\.dashboard-column\s*\{[^}]*display\s*:\s*grid[^}]*gap\s*:\s*1rem/s.test(source),
  },
  {
    name: 'posts panel no longer spans synthetic grid rows',
    pass: !/\.panel-posts\s*\{[^}]*grid-row\s*:\s*span\s+2/s.test(source),
  },
  {
    name: 'community panel does not force the brief card onto a new row',
    pass: !desktopCommunitySpansAllColumns,
  },
  {
    name: 'community card list collapses to one column in its dashboard column',
    pass: /\.community-grid\s*\{[^}]*grid-template-columns\s*:\s*1fr/s.test(source),
  },
  {
    name: 'responsive layout restores single-column card ordering',
    pass: /@media \(max-width:\s*1024px\)[\s\S]*\.dashboard-column\s*\{[^}]*display\s*:\s*contents/s.test(source)
      && /@media \(max-width:\s*1024px\)[\s\S]*\.panel-jobs\s*\{[^}]*order\s*:\s*2/s.test(source)
      && /@media \(max-width:\s*1024px\)[\s\S]*\.panel-community\s*\{[^}]*order\s*:\s*4/s.test(source),
  },
  {
    name: 'brief panel fills the full dashboard width on desktop',
    pass: /\.panel-brief\s*\{[^}]*grid-column\s*:\s*1\s*\/\s*-1/s.test(source)
      && /\.brief-core\s*\{[^}]*grid-template-columns\s*:\s*minmax\(0,\s*1fr\)\s*minmax\(280px,\s*0\.42fr\)/s.test(source),
  },
  {
    name: 'contest panel stretches to remove the gap below the side column',
    pass: /\.dashboard-grid\s*\{[^}]*align-items\s*:\s*stretch/s.test(source)
      && /\.dashboard-column-side\s*\{[^}]*grid-template-rows\s*:\s*auto\s+minmax\(0,\s*1fr\)/s.test(source)
      && /\.panel-contests\s*\{[^}]*height\s*:\s*100%/s.test(source),
  },
  {
    name: 'dashboard heading uses stronger copy without the old description',
    pass: /놓치면 안 되는/.test(source)
      && /커리어 신호/.test(source)
      && /class="section-title-accent"/.test(source)
      && /v-for="summary in feedSummaries"/.test(source)
      && /\.section-summary\s*\{[^}]*grid-template-columns\s*:\s*repeat\(3,\s*minmax\(0,\s*1fr\)\)/s.test(source)
      && !/정보량은 줄이고 판단은 빠르게/.test(source)
      && !/지금 바로 확인해야 할/.test(source),
  },
  {
    name: 'dashboard summary aligns horizontally with heading',
    pass: /\.section-head\s*\{[^}]*align-items\s*:\s*start/s.test(source)
      && /\.section-brief\s*\{[^}]*padding-top\s*:\s*0/s.test(source)
      && /\.section-summary\s*\{[^}]*align-items\s*:\s*start/s.test(source),
  },
  {
    name: 'hero removes the main headline and lower metric cards',
    pass: !/hero-title/.test(source)
      && !/metric-grid/.test(source)
      && !/heroMetrics/.test(source),
  },
  {
    name: 'focus card is compact without the three lower signal cards',
    pass: !/signal-list/.test(source)
      && !/signal-item/.test(source)
      && /\.terminal-code\s*\{[^}]*padding\s*:\s*1\.5rem\s+1\.45rem\s+1\.65rem/s.test(source),
  },
  {
    name: 'hero search area is removed in favor of brand messaging',
    pass: /\.hero-copy\s*\{[^}]*display\s*:\s*grid/s.test(source)
      && !/class="search-shell/.test(source)
      && !/class="search-box"/.test(source)
      && !/searchSuggestionsOpen/.test(source),
  },
  {
    name: 'focus area renders as a code terminal card',
    pass: /class="terminal-card reveal"/.test(source)
      && /class="terminal-bar"/.test(source)
      && /class="terminal-code"/.test(source)
      && /\.terminal-card\s*\{[^}]*background\s*:\s*#1f1e1c/s.test(source),
  },
  {
    name: 'terminal panel uses scan command copy instead of function code',
    pass: /<span class="terminal-title">techbridge\.scan<\/span>/.test(source)
      && /code-muted">\$<\/span>/.test(source)
      && /code-green">techbridge<\/span>/.test(source)
      && /code-blue">scan<\/span>/.test(source)
      && /code-orange">--today<\/span>/.test(source)
      && /jobs/.test(source)
      && /contests/.test(source)
      && /community/.test(source)
      && /next step is ready/.test(source)
      && !/FocusBoard/.test(source)
      && !/=&gt;/.test(source),
  },
  {
    name: 'hero left column gains a visual message block',
    pass: /class="[^"]*hero-signal-card[^"]*"/.test(source)
      && /class="signal-orbit"/.test(source)
      && /TechBridge는 흩어진 커리어 정보를/.test(source),
  },
  {
    name: 'hero background adds subtle bridge signal lines',
    pass: /class="hero-signal-map"/.test(source)
      && /class="signal-line signal-line-primary"/.test(source)
      && /class="signal-line signal-line-secondary"/.test(source)
      && /class="signal-line signal-line-dotted"/.test(source)
      && /\.hero-section\s*\{[^}]*position\s*:\s*relative[^}]*overflow\s*:\s*hidden/s.test(source)
      && /\.hero-signal-map\s*\{[^}]*pointer-events\s*:\s*none/s.test(source)
      && /\.signal-line-primary\s*\{[^}]*stroke\s*:\s*rgba\(47,\s*111,\s*115,\s*0\.34\)/s.test(source)
      && /\.signal-line-dotted\s*\{[^}]*stroke-dasharray\s*:\s*1\s+18/s.test(source),
  },
  {
    name: 'signal orbit labels rotate clockwise around the center',
    pass: /class="orbit-track"/.test(source)
      && /class="orbit-label"/.test(source)
      && /@keyframes\s+orbit-clockwise/.test(source)
      && /@keyframes\s+orbit-label-counter/.test(source)
      && /\.orbit-track\s*\{[^}]*animation\s*:\s*orbit-clockwise/s.test(source)
      && /\.orbit-label\s*\{[^}]*animation\s*:\s*orbit-label-counter/s.test(source)
      && /rotate\(360deg\)/.test(source)
      && /rotate\(-360deg\)/.test(source),
  },
  {
    name: 'home page reads global search query and renders results',
    pass: /useRoute/.test(source)
      && /const route = useRoute\(\)/.test(source)
      && /searchTerm/.test(source)
      && /fetchHomeSearchResults/.test(source)
      && /v-if="hasSearchQuery"/.test(source)
      && /class="search-results-section page-shell"/.test(source)
      && /검색 결과/.test(source),
  },
  {
    name: 'home search queries searchable APIs and filters community locally',
    pass: /api\.get\('\/posts\/',\s*\{\s*params:\s*\{\s*limit:\s*6,\s*search:\s*query/s.test(source)
      && /api\.get\('\/jobs\/',\s*\{\s*params:\s*\{\s*limit:\s*6,\s*search:\s*query,\s*include_external:\s*false\s*\}\s*\}\)/s.test(source)
      && /api\.get\('\/contests\/',\s*\{\s*params:\s*\{\s*limit:\s*6,\s*search:\s*query,\s*include_external:\s*false\s*\}\s*\}\)/s.test(source)
      && /api\.get\('\/community\/'\)/.test(source)
      && /matchesSearch/.test(source),
  },
  {
    name: 'global navbar search keeps users on the searchable home route',
    pass: /router\.push\(\{\s*path:\s*'\/',\s*query:\s*\{\s*search:\s*query\s*\}\s*\}\)/.test(navbarSource),
  },
  {
    name: 'navbar brand is renamed to TechBridge',
    pass: /<strong>TechBridge<\/strong>/.test(navbarSource)
      && !/<strong>Career Board<\/strong>/.test(navbarSource),
  },
  {
    name: 'navbar logo mark uses TB initials',
    pass: /<span class="logo-mark">TB<\/span>/.test(navbarSource)
      && !/<span class="logo-mark">MiQ<\/span>/.test(navbarSource),
  },
  {
    name: 'auth page brand names are renamed to TechBridge',
    pass: /<span class="brand-name">TechBridge<\/span>/.test(loginSource)
      && /<span class="brand-name">TechBridge<\/span>/.test(registerSource)
      && /<span class="brand-name">TechBridge<\/span>/.test(adminRegisterSource)
      && !/Career Board/.test(loginSource)
      && !/Career Board/.test(registerSource)
      && !/Career Board/.test(adminRegisterSource),
  },
  {
    name: 'navbar search opens as a full-width drop panel',
    pass: /class="[^"]*search-toggle[^"]*"/.test(navbarSource)
      && /class="search-overlay"/.test(navbarSource)
      && /class="search-backdrop"/.test(navbarSource)
      && /\.search-overlay\s*\{[^}]*position\s*:\s*fixed[^}]*top\s*:\s*0/s.test(navbarSource)
      && /\.search-panel\s*\{[^}]*min-height\s*:\s*24rem/s.test(navbarSource),
  },
  {
    name: 'navbar no longer uses the compact expanding search bar',
    pass: !/class="search-bar"/.test(navbarSource)
      && !/\.search-bar/.test(navbarSource),
  },
  {
    name: 'navbar search overlay shows only recent searches',
    pass: /최근 검색어/.test(navbarSource)
      && /최근 검색어가 없어요/.test(navbarSource)
      && /saveRecentSearch/.test(navbarSource)
      && !/quickSearchTags/.test(navbarSource)
      && !/추천 검색어/.test(navbarSource)
      && !/quick-searches/.test(navbarSource)
      && !/quick-chip/.test(navbarSource),
  },
  {
    name: 'recommended jobs remove deadline badge',
    pass: !/D-\{\{\s*job\.dday\s*\}\}/.test(source)
      && !/job\.dday !== '마감'/.test(source)
      && /D-\{\{\s*contest\.dday\s*\}\}/.test(source),
  },
  {
    name: 'quick brief card focuses on exploration routine only',
    pass: /class="routine-note"/.test(source)
      && /탐색 루틴을 따라가면/.test(source)
      && !/class="brief-cta"/.test(source)
      && !/개인 보드 만들기/.test(source)
      && !/class="primary-cta full-width"/.test(source),
  },
  {
    name: 'quick brief routine fills the full card width without empty column',
    pass: /\.brief-list\s*\{[^}]*grid-column\s*:\s*1\s*\/\s*-1[^}]*grid-template-columns\s*:\s*minmax\(220px,\s*0\.9fr\)\s+repeat\(3,\s*minmax\(0,\s*1fr\)\)/s.test(source)
      && /\.brief-core\s*\{[^}]*gap\s*:\s*0\.75rem/s.test(source)
      && /\.brief-item,\s*\.routine-note\s*\{[^}]*min-height\s*:\s*100%/s.test(source),
  },
  {
    name: 'quick brief intro sentence is centered',
    pass: /\.routine-note\s*\{[^}]*display\s*:\s*flex[^}]*align-items\s*:\s*center[^}]*justify-content\s*:\s*center[^}]*text-align\s*:\s*center/s.test(source),
  },
]

const failures = checks.filter((check) => !check.pass)

if (failures.length) {
  console.error('Home layout verification failed:')
  for (const failure of failures) console.error(`- ${failure.name}`)
  process.exit(1)
}

console.log('Home layout verification passed.')
