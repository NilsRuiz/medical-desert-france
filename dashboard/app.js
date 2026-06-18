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
const departmentMapEl = document.querySelector("#department-map");
const mapDetailsEl = document.querySelector("#map-details");
const mapLegendEl = document.querySelector("#map-legend");

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

const riskColors = {
  high: "#b42318",
  medium: "#d98d00",
  low: "#2f855a",
  unknown: "#94a3b8",
};

function metricCard(metric) {
  const value = Number(metric.metric_value).toLocaleString("en-US", { maximumFractionDigits: 2 });
  return `<div class="metric"><span>${metric.label} - ${metric.metric_name}</span><strong>${value}</strong></div>`;
}

function renderLegend() {
  mapLegendEl.innerHTML = ["high", "medium", "low", "unknown"]
    .map((risk) => `<span class="legend-item"><span class="legend-swatch" style="background:${riskColors[risk]}"></span>${risk}</span>`)
    .join("");
}

function projectPoint([longitude, latitude], bounds, width, height, padding) {
  const [minLon, minLat, maxLon, maxLat] = bounds;
  const x = padding + ((longitude - minLon) / (maxLon - minLon)) * (width - padding * 2);
  const y = padding + ((maxLat - latitude) / (maxLat - minLat)) * (height - padding * 2);
  return [x, y];
}

function polygonPath(coordinates, bounds, width, height, padding) {
  return coordinates
    .map((ring) =>
      ring
        .map((point, index) => {
          const [x, y] = projectPoint(point, bounds, width, height, padding);
          return `${index === 0 ? "M" : "L"}${x.toFixed(3)} ${y.toFixed(3)}`;
        })
        .join(" ") + " Z",
    )
    .join(" ");
}

function featureBounds(features) {
  const points = features.flatMap((feature) => feature.geometry.coordinates.flat());
  const longitudes = points.map((point) => point[0]);
  const latitudes = points.map((point) => point[1]);
  return [Math.min(...longitudes), Math.min(...latitudes), Math.max(...longitudes), Math.max(...latitudes)];
}

function renderDepartmentDetails(department) {
  if (!department) {
    mapDetailsEl.textContent = "No dashboard data loaded for this department yet.";
    return;
  }
  const population = department.population.toLocaleString("en-US");
  mapDetailsEl.innerHTML = `
    <strong>${department.department_name} (${department.department_code})</strong> -
    ${department.risk_class.toUpperCase()} risk, average APL ${department.avg_apl_score ?? "n/a"},
    ${department.high_risk_communes}/${department.commune_count} high-risk communes, population ${population}.
  `;
}

async function loadDepartmentMap() {
  renderLegend();
  try {
    const [geojson, departments] = await Promise.all([
      fetch("/assets/departments.geojson").then((response) => response.json()),
      api("/dashboard/departments"),
    ]);
    const departmentByCode = new Map(departments.map((department) => [department.department_code, department]));
    const width = 10;
    const height = 10;
    const bounds = featureBounds(geojson.features);
    const shapes = geojson.features
      .map((feature) => {
        const code = feature.properties.code;
        const department = departmentByCode.get(code);
        const risk = department?.risk_class || "unknown";
        const path = polygonPath(feature.geometry.coordinates, bounds, width, height, 0.4);
        const [labelX, labelY] = projectPoint(feature.properties.label, bounds, width, height, 0.4);
        return `
          <path class="department-shape" data-code="${code}" d="${path}" fill="${riskColors[risk]}" />
          <text class="department-label" x="${labelX.toFixed(3)}" y="${labelY.toFixed(3)}">${code}</text>
        `;
      })
      .join("");
    departmentMapEl.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img">${shapes}</svg>`;
    departmentMapEl.querySelectorAll(".department-shape").forEach((shape) => {
      shape.addEventListener("click", () => {
        departmentMapEl.querySelectorAll(".department-shape").forEach((item) => item.classList.remove("selected"));
        shape.classList.add("selected");
        renderDepartmentDetails(departmentByCode.get(shape.dataset.code));
      });
    });
  } catch {
    departmentMapEl.innerHTML = "<p>Department map unavailable.</p>";
  }
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
loadDepartmentMap();
searchCommune(new Event("submit"));
