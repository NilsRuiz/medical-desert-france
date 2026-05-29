const apiBase = window.API_BASE_URL || "/api";
let selectedCommune = null;

const statusEl = document.querySelector("#api-status");
const form = document.querySelector("#search-form");
const queryInput = document.querySelector("#query");
const listEl = document.querySelector("#commune-list");
const selectedName = document.querySelector("#selected-name");
const detailsEl = document.querySelector("#commune-details");
const predictButton = document.querySelector("#predict-button");
const predictionEl = document.querySelector("#prediction");
const summaryEl = document.querySelector("#summary");
const regionsEl = document.querySelector("#regions");

async function api(path, options = {}) {
  const response = await fetch(`${apiBase}${path}`, {
    headers: { "content-type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

function metricCard(metric) {
  const value = Number(metric.metric_value).toLocaleString("en-US", { maximumFractionDigits: 2 });
  return `<div class="metric"><span>${metric.label} - ${metric.metric_name}</span><strong>${value}</strong></div>`;
}

function renderCommune(commune) {
  selectedCommune = commune;
  selectedName.textContent = `${commune.name} (${commune.code})`;
  detailsEl.innerHTML = `
    <dt>Department</dt><dd>${commune.department_name || commune.department_code || "n/a"}</dd>
    <dt>Region</dt><dd>${commune.region_name || commune.region_code || "n/a"}</dd>
    <dt>Population</dt><dd>${commune.population?.toLocaleString("en-US") || "n/a"}</dd>
    <dt>APL score</dt><dd>${commune.apl_score ?? "n/a"}</dd>
  `;
  predictionEl.textContent = "";
  predictButton.disabled = false;
}

async function loadHealth() {
  try {
    await api("/health");
    statusEl.textContent = "API online";
    statusEl.classList.add("ok");
  } catch {
    statusEl.textContent = "API offline";
    statusEl.classList.add("fail");
  }
}

async function loadMetrics() {
  try {
    const [summary, regions] = await Promise.all([
      api("/dashboard/summary"),
      api("/dashboard/regions"),
    ]);
    summaryEl.innerHTML = summary.map(metricCard).join("") || "<p>No summary metrics loaded.</p>";
    regionsEl.innerHTML = regions.map(metricCard).join("") || "<p>No regional metrics loaded.</p>";
  } catch {
    summaryEl.innerHTML = "<p>Dashboard metrics unavailable.</p>";
  }
}

async function searchCommune(event) {
  event.preventDefault();
  const q = encodeURIComponent(queryInput.value.trim());
  const communes = await api(`/communes${q ? `?q=${q}` : ""}`);
  listEl.innerHTML = communes
    .map((commune) => `<li><button type="button" data-code="${commune.code}">${commune.name} (${commune.code})</button></li>`)
    .join("");
}

listEl.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-code]");
  if (!button) return;
  renderCommune(await api(`/communes/${button.dataset.code}`));
});

predictButton.addEventListener("click", async () => {
  if (!selectedCommune) return;
  const prediction = await api("/predict", {
    method: "POST",
    body: JSON.stringify({ commune_code: selectedCommune.code }),
  });
  predictionEl.textContent = `${prediction.risk_class.toUpperCase()} risk - score ${prediction.risk_score.toFixed(2)}`;
});

form.addEventListener("submit", searchCommune);
loadHealth();
loadMetrics();
searchCommune(new Event("submit"));
