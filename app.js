// Reads status.json (written by CI next to this page) and fills in the card.
// Values are inserted with textContent, never innerHTML, and links are only set for https URLs.

const $ = (id) => document.getElementById(id)

const CHIP_TEXT = {
	passed: 'All checks passing',
	failed: 'Checks failing',
	unknown: 'Status unavailable',
}

const LAYER_NAMES = { lint: 'Lint', smoke: 'Smoke tests' }

function safeHref(element, url) {
	if (typeof url === 'string' && url.startsWith('https://')) {
		element.href = url
		return true
	}
	return false
}

function render(status) {
	const overall = status.overall === 'passed' || status.overall === 'failed' ? status.overall : 'unknown'
	const chip = $('status-chip')
	chip.className = `chip chip-${overall}`
	chip.textContent = CHIP_TEXT[overall]

	$('status-detail').textContent =
		overall === 'passed'
			? 'The latest run on main completed without failures.'
			: 'The latest run has at least one failing layer. Open the report for details.'

	const layers = $('layers')
	layers.replaceChildren()
	for (const [key, label] of Object.entries(LAYER_NAMES)) {
		const result = status.layers?.[key] ?? 'unknown'
		const item = document.createElement('li')
		item.className = result === 'success' ? 'ok' : result === 'unknown' || result === 'skipped' ? '' : 'bad'
		item.textContent = `${label}: ${result}`
		layers.append(item)
	}
	layers.hidden = false

	const t = status.tests
	if (t) {
		const extras = [
			t.failed ? `${t.failed} failed` : '',
			t.broken ? `${t.broken} broken` : '',
			t.skipped ? `${t.skipped} skipped` : '',
			t.flaky ? `${t.flaky} flaky` : '',
		].filter(Boolean)
		$('fact-tests').textContent =
			`${t.passed} passed of ${t.total}${extras.length ? ` (${extras.join(', ')})` : ''}`
	}
	$('fact-date').textContent = status.generatedAt ? new Date(status.generatedAt).toLocaleString() : 'unknown'
	$('fact-trigger').textContent = status.trigger === 'schedule' ? 'nightly schedule' : (status.trigger ?? 'unknown')

	const commit = $('fact-commit')
	commit.textContent = status.commit?.short || 'unknown'
	safeHref(commit, status.commit?.url)

	const run = $('link-run')
	run.hidden = !safeHref(run, status.run?.url)

	// Relative links only, so a value in status.json can never send a visitor to another site.
	if (typeof status.links?.report === 'string' && !status.links.report.includes(':')) {
		$('link-report').href = status.links.report
	}
	const trends = $('link-trends')
	if (typeof status.links?.trends === 'string' && !status.links.trends.includes(':')) {
		trends.href = status.links.trends
		trends.hidden = false
	}
	$('facts').hidden = false
}

function renderUnavailable() {
	const chip = $('status-chip')
	chip.className = 'chip chip-unknown'
	chip.textContent = CHIP_TEXT.unknown
	$('status-detail').textContent = 'The latest results could not be loaded. The full report is still available below.'
}

fetch('status.json', { cache: 'no-store' })
	.then((response) => {
		if (!response.ok) {
			throw new Error(`status.json returned ${response.status}`)
		}
		return response.json()
	})
	.then(render)
	.catch(renderUnavailable)
