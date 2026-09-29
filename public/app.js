(() => {
  'use strict';

  const sample = document.getElementById('sample');
  const manifest = document.getElementById('manifest');
  const fileInput = document.getElementById('file');
  const advancedPanel = document.getElementById('advanced-panel');
  const checkId = document.getElementById('check-id');
  const analyzeButton = document.getElementById('analyze');
  const clearButton = document.getElementById('clear');
  const loading = document.getElementById('loading');
  const errorBox = document.getElementById('error');
  const emptyReport = document.getElementById('empty-report');
  const resultSection = document.getElementById('result');
  const copyState = document.getElementById('copy-state');
  let latest = null;

  const isLoopback = ['127.0.0.1', 'localhost'].includes(location.hostname);
  document.getElementById('runtime-label').textContent = isLoopback
    ? 'Local evidence analysis'
    : 'Hosted evidence analysis';
  document.getElementById('runtime-intro').textContent = isLoopback
    ? 'Review supplied evidence, see what remains uncertain, and decide what to check next.'
    : 'Review supplied evidence and its limits. Use synthetic or public-safe data only.';
  document.getElementById('runtime-boundary').textContent = isLoopback
    ? 'The loopback app analyzes manifests in memory. It never runs checks or saves submissions.'
    : 'The hosted API does not run checks or store submissions. Vercel request retention is unverified; use synthetic or public-safe data only.';
  document.getElementById('runtime-footer').textContent = isLoopback
    ? 'Proofline · local evidence report · supplied manifests are processed in memory.'
    : 'Proofline · hosted demo · application storage off; platform retention unverified.';

  function setActiveStep(name) {
    for (const stepName of ['change', 'evidence', 'report']) {
      const element = document.getElementById(`step-${stepName}`);
      const active = stepName === name;
      element.classList.toggle('is-current', active);
      if (active) element.setAttribute('aria-current', 'step');
      else element.removeAttribute('aria-current');
    }
  }

  function makeError(message, kind = 'api') {
    const error = new Error(message);
    error.kind = kind;
    return error;
  }

  function showError(message, kind = 'api') {
    errorBox.textContent = message;
    errorBox.dataset.kind = kind;
    errorBox.hidden = false;
  }

  function clearError() {
    errorBox.textContent = '';
    errorBox.hidden = true;
    delete errorBox.dataset.kind;
  }

  function setLoading(isLoading, message = 'Analyzing the supplied evidence…') {
    loading.textContent = message;
    loading.hidden = !isLoading;
    analyzeButton.disabled = isLoading;
    clearButton.disabled = isLoading;
    sample.disabled = isLoading;
    checkId.disabled = isLoading;
    fileInput.disabled = isLoading;
    analyzeButton.textContent = isLoading ? 'Working…' : 'Analyze evidence';
  }

  function setCheckSelection(id) {
    checkId.value = [...checkId.options].some(option => option.value === id) ? id : '';
    const details = document.getElementById('declared-check');
    details.hidden = !checkId.value;
    if (!checkId.value) return;

    const selected = checkId.selectedOptions[0];
    document.getElementById('check-class').value = selected.dataset.evidenceClass || 'local';
    const isFixture = checkId.value === 'fixture-simulated-telemetry';
    document.getElementById('check-result').value = isFixture ? 'fixture' : 'pass';
    document.getElementById('check-source').value = isFixture
      ? 'Synthetic fixture declaration; not live telemetry'
      : 'User-declared result; not run by the browser';
  }

  function populateGuided(raw) {
    document.getElementById('scenario-name').value = raw.scenario || 'my-change';
    const claim = raw.claims && raw.claims[0] || {};
    document.getElementById('claim-id').value = claim.id || 'claim-1';
    document.getElementById('claim-title').value = claim.title || '';
    document.getElementById('evidence-class').value = claim.evidence_class || 'local';
    document.getElementById('limitation').value = claim.limitation || '';
    const check = raw.checks && raw.checks.find(item => (claim.evidence_refs || []).includes(item.id));
    setCheckSelection(check ? check.id : '');
    if (check) {
      document.getElementById('check-result').value = check.result || 'pass';
      document.getElementById('check-class').value = check.evidence_class || 'local';
      document.getElementById('check-source').value = check.source || '';
    }
    document.getElementById('change-request').value = raw.change_request || '';
  }

  function buildGuidedManifest() {
    const selectedCheck = checkId.value;
    const claim = {
      id: document.getElementById('claim-id').value.trim(),
      title: document.getElementById('claim-title').value.trim(),
      evidence_class: document.getElementById('evidence-class').value,
      evidence_refs: selectedCheck ? [selectedCheck] : [],
    };
    const limitation = document.getElementById('limitation').value.trim();
    if (limitation) claim.limitation = limitation;

    const raw = {
      scenario: document.getElementById('scenario-name').value.trim(),
      claims: [claim],
      checks: selectedCheck ? [{
        id: selectedCheck,
        result: document.getElementById('check-result').value,
        evidence_class: document.getElementById('check-class').value,
        source: document.getElementById('check-source').value.trim(),
      }] : [],
    };
    const changeRequest = document.getElementById('change-request').value.trim();
    if (changeRequest) raw.change_request = changeRequest;
    return raw;
  }

  function node(tag, text, className) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = String(text);
    if (className) element.className = className;
    return element;
  }

  async function loadSample() {
    clearError();
    setLoading(true, 'Loading the synthetic example…');
    try {
      const response = await fetch(`/api/fixtures?name=${encodeURIComponent(sample.value)}`, {cache: 'no-store'});
      let data;
      try {
        data = await response.json();
      } catch {
        throw makeError('The example service returned an invalid response.');
      }
      if (!response.ok) throw makeError(data.error || 'The synthetic example could not be loaded.');
      manifest.value = JSON.stringify(data, null, 2);
      populateGuided(data);
      advancedPanel.open = false;
      fileInput.value = '';
      latest = null;
      resultSection.hidden = true;
      emptyReport.hidden = false;
      copyState.textContent = '';
      setActiveStep('change');
    } catch (error) {
      showError(`API error: ${error.message || 'The synthetic example could not be loaded.'}`, 'api');
    } finally {
      setLoading(false);
    }
  }

  function addClaimDetails(claim, checksById) {
    const card = node('article', undefined, 'claim-card');
    const heading = node('h3');
    heading.append(document.createTextNode(claim.title));
    heading.append(node('span', claim.status.toUpperCase(), `badge ${claim.status}`));
    card.append(heading);

    const details = document.createElement('dl');
    for (const [label, value] of [
      ['Evidence class', claim.evidence_class],
      ['Limitation', claim.limitation],
      ['Next action', claim.next_action],
    ]) {
      details.append(node('dt', label), node('dd', value || 'Not recorded'));
    }
    card.append(details, node('h4', 'Evidence details', 'evidence-heading'));

    if (!claim.evidence_refs.length) {
      card.append(node('p', 'No supporting evidence was supplied.', 'field-help'));
    }
    for (const reference of claim.evidence_refs) {
      const check = checksById.get(reference);
      const evidence = document.createElement('details');
      evidence.className = 'evidence';
      evidence.append(node('summary', check ? `${reference} · ${check.result}` : `${reference} · missing`));
      if (check) {
        const evidenceDetails = document.createElement('dl');
        for (const [label, value] of [
          ['Result', check.result],
          ['Evidence class', check.evidence_class],
          ['Source', check.source],
          ['Provenance', check.provenance],
          ['Observed at', check.observed_at || 'Not recorded'],
        ]) {
          evidenceDetails.append(node('dt', label), node('dd', value || 'Not recorded'));
        }
        evidence.append(evidenceDetails);
      }
      card.append(evidence);
    }
    return card;
  }

  function render(data) {
    latest = data;
    const report = data.report;
    const counts = report.summary;
    const proven = counts.proven || 0;
    const total = report.claims.length;

    document.getElementById('markdown-preview').value = data.markdown;
    document.getElementById('outcome').textContent = proven
      ? `Proofline observed evidence for ${proven} of ${total} claims within their declared evidence classes.`
      : 'No claim has runner-observed evidence in its declared evidence class yet.';
    document.getElementById('next-action').textContent = report.claims[0]?.next_action
      || 'Add a claim and supporting evidence to continue.';
    document.getElementById('meta').textContent = [
      `Scenario: ${report.scenario}`,
      `Repository: ${report.repository_id || 'Not supplied'}`,
      `Report: ${report.report_id}`,
      `Generated: ${report.generated_at || 'not recorded'}`,
    ].join(' · ');
    document.getElementById('request-summary').textContent = report.change_request
      ? `Change request: ${report.change_request}`
      : 'No change request supplied.';

    const countBox = document.getElementById('counts');
    countBox.replaceChildren();
    for (const [status, count] of Object.entries(counts)) {
      countBox.append(node('span', `${status}: ${count}`, `count ${status}`));
    }

    const checksById = new Map(report.checks.map(check => [check.id, check]));
    const claimList = document.getElementById('claims');
    claimList.replaceChildren(...report.claims.map(claim => addClaimDetails(claim, checksById)));

    const notes = document.getElementById('notes');
    notes.replaceChildren(...report.security_notes.map(note => node('li', note)));
    resultSection.hidden = false;
    emptyReport.hidden = true;
    setActiveStep('report');
    document.getElementById('result-title').focus({preventScroll: true});
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    resultSection.scrollIntoView({behavior: reduceMotion ? 'auto' : 'smooth', block: 'start'});
  }

  function download(name, content, type) {
    const url = URL.createObjectURL(new Blob([content], {type}));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = name;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  sample.addEventListener('change', loadSample);
  checkId.addEventListener('change', () => setCheckSelection(checkId.value));
  clearButton.addEventListener('click', () => {
    latest = null;
    resultSection.hidden = true;
    emptyReport.hidden = false;
    clearError();
    copyState.textContent = '';
    setActiveStep('change');
  });

  fileInput.addEventListener('change', async () => {
    const file = fileInput.files && fileInput.files[0];
    if (!file) return;
    clearError();
    if (file.size > 262144) {
      showError('Validation error: the file exceeds the 256 KB limit.', 'validation');
      fileInput.value = '';
      return;
    }
    try {
      manifest.value = await file.text();
      sample.selectedIndex = -1;
      advancedPanel.open = true;
    } catch {
      showError('API error: the selected manifest file could not be read.', 'api');
    }
  });

  analyzeButton.addEventListener('click', async () => {
    clearError();
    latest = null;
    resultSection.hidden = true;
    emptyReport.hidden = false;
    setActiveStep('evidence');
    setLoading(true);

    try {
      let parsed;
      if (advancedPanel.open) {
        try {
          parsed = JSON.parse(manifest.value);
        } catch {
          throw makeError('The JSON manifest is invalid.', 'validation');
        }
        if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
          const changeRequest = document.getElementById('change-request').value.trim();
          if (changeRequest) parsed.change_request = changeRequest;
          else delete parsed.change_request;
        }
      } else {
        parsed = buildGuidedManifest();
      }

      const body = JSON.stringify(parsed);
      if (new TextEncoder().encode(body).byteLength > 262144) {
        throw makeError('The manifest exceeds the 256 KB limit.', 'validation');
      }

      let response;
      try {
        response = await fetch('/api/report', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body,
          cache: 'no-store',
        });
      } catch {
        throw makeError('The report service could not be reached. Check the local or hosted connection and retry.');
      }

      let data;
      try {
        data = await response.json();
      } catch {
        throw makeError(`The report service returned an invalid response (HTTP ${response.status}).`);
      }
      if (!response.ok) {
        const kind = response.status >= 500 ? 'api' : 'validation';
        throw makeError(data.error || `Request failed with HTTP ${response.status}.`, kind);
      }
      if (!data.report || !Array.isArray(data.report.claims) || !data.report.summary
        || !Array.isArray(data.report.checks) || !Array.isArray(data.report.security_notes)
        || typeof data.markdown !== 'string') {
        throw makeError('The report service returned an incomplete report.');
      }
      render(data);
    } catch (error) {
      const kind = error.kind || 'api';
      const label = kind === 'validation' ? 'Validation error' : 'API error';
      showError(`${label}: ${error.message || 'The manifest could not be analyzed.'}`, kind);
      setActiveStep('evidence');
    } finally {
      setLoading(false);
    }
  });

  document.getElementById('download-json').addEventListener('click', () => {
    if (!latest) return;
    download('proofline-report.json', JSON.stringify(latest.report, null, 2), 'application/json');
    copyState.textContent = 'JSON report download started.';
  });

  document.getElementById('download-md').addEventListener('click', () => {
    if (!latest) return;
    download('proofline-report.md', latest.markdown, 'text/markdown');
    copyState.textContent = 'Markdown report download started.';
  });

  document.getElementById('copy-md').addEventListener('click', async () => {
    if (!latest) return;
    const preview = document.getElementById('markdown-preview');
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('unavailable');
      await navigator.clipboard.writeText(latest.markdown);
      copyState.textContent = 'Markdown copied.';
    } catch {
      document.querySelector('.markdown-details').open = true;
      preview.focus();
      preview.select();
      copyState.textContent = 'Markdown selected. Copy it, or download the report.';
    }
  });

  async function initialize() {
    setLoading(true, 'Loading the check registry…');
    try {
      const response = await fetch('/api/checks', {cache: 'no-store'});
      if (!response.ok) throw new Error('The check registry could not be loaded.');
      for (const check of await response.json()) {
        const option = node('option', check.id);
        option.value = check.id;
        option.dataset.evidenceClass = check.evidence_class;
        checkId.append(option);
      }
      await loadSample();
    } catch {
      showError('API error: the code-owned check registry could not be loaded.', 'api');
    } finally {
      setLoading(false);
    }
  }

  initialize();
})();
