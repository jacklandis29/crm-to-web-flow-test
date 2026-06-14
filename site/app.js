const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const percent = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 0,
});

const shortDate = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  timeZone: "UTC",
});

const $ = (selector) => document.querySelector(selector);

function shortMoney(value) {
  if (Math.abs(value) >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(value >= 10_000_000 ? 0 : 1)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `$${(value / 1_000).toFixed(0)}K`;
  }
  return money.format(value);
}

function stageClass(stage) {
  return stage.toLowerCase().replace(/\s+/g, "-");
}

function renderMetrics(data) {
  const revision = data.metadata.sourceRevision ? ` · CRM rev ${data.metadata.sourceRevision}` : "";
  $("#refreshStatus").textContent = `Data as of ${data.metadata.dataAsOf}${revision}`;
  $("#pipelineValue").textContent = money.format(data.metrics.pipelineValue);
  $("#pipelineMeta").textContent = `${data.metrics.totalRecords} validated records`;
  $("#weightedPipeline").textContent = money.format(data.metrics.weightedPipeline);
  $("#closedWon").textContent = money.format(data.metrics.closedWon);
  $("#staleOpenCount").textContent = data.metrics.staleOpenCount.toString();
  $("#sourceHash").textContent = `${data.metadata.sourceSystem || "CRM"} sha256 ${data.metadata.sourceSha256.slice(0, 12)}`;
}

function renderStageChart(data) {
  const chart = $("#stageChart");
  const maxAmount = Math.max(...data.summaries.byStage.map((item) => item.amount), 1);
  chart.innerHTML = data.summaries.byStage
    .map((item) => {
      const width = Math.max((item.amount / maxAmount) * 100, 2);
      return `
        <div class="stage-row">
          <span>${item.name}</span>
          <span class="stage-track">
            <span class="stage-fill" style="width: ${width}%"></span>
          </span>
          <span class="amount-label">${shortMoney(item.amount)}</span>
        </div>
      `;
    })
    .join("");
}

function renderRegionChart(data) {
  const chart = $("#regionChart");
  const regions = data.summaries.byRegion.slice(0, 5);
  const maxAmount = Math.max(...regions.map((item) => item.amount), 1);
  chart.innerHTML = regions
    .map((item) => {
      const width = Math.max((item.amount / maxAmount) * 100, 2);
      return `
        <div class="region-row">
          <span>${item.name}</span>
          <span class="region-track">
            <span class="region-fill" style="width: ${width}%"></span>
          </span>
          <span class="amount-label">${shortMoney(item.amount)}</span>
        </div>
      `;
    })
    .join("");
}

function renderNarrative(summary) {
  const cards = [summary.hero, ...summary.cards];
  $("#narrativeCards").innerHTML = cards
    .map(
      (card) => `
        <article class="narrative-card">
          <h3>${card.title || card.headline}</h3>
          <p>${card.body}</p>
          <div class="source-list">
            ${card.sources.map((source) => `<code>${source}</code>`).join("")}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderRows(data) {
  const rows = data.opportunities.slice(0, 14);
  $("#opportunityRows").innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td>${row.account}</td>
          <td>${row.region}</td>
          <td><span class="stage-pill ${stageClass(row.stage)}">${row.stage}</span></td>
          <td>${row.owner}</td>
          <td>${money.format(row.amount)}</td>
          <td>${percent.format(row.probability)}</td>
          <td>${shortDate.format(new Date(`${row.lastUpdated}T00:00:00Z`))}</td>
        </tr>
      `,
    )
    .join("");
}

function renderAudit(audit) {
  $("#auditSteps").innerHTML = audit.checks
    .map(
      (check) => `
        <article class="audit-card">
          <span class="audit-status">${check.status}</span>
          <h3>${check.name}</h3>
          <p>${check.detail}</p>
        </article>
      `,
    )
    .join("");
}

function renderAiStatus(summary) {
  const badge = document.querySelector("#aiStatus");
  badge.textContent = summary.metadata.generatedBy;
  badge.title = `AI copy generated from ${summary.metadata.sourceFile}`;
}

function showError(error) {
  document.querySelector("main").innerHTML = `
    <div class="error-state">
      <strong>Could not load generated pipeline data.</strong>
      <p>${error.message}</p>
    </div>
  `;
}

async function init() {
  try {
    const [pipelineResponse, auditResponse, aiResponse] = await Promise.all([
      fetch("./data/pipeline.json"),
      fetch("./data/audit-log.json"),
      fetch("./data/ai-summary.json"),
    ]);
    if (!pipelineResponse.ok || !auditResponse.ok || !aiResponse.ok) {
      throw new Error("Run npm run generate, then serve the site from the project root.");
    }
    const [pipeline, audit, aiSummary] = await Promise.all([
      pipelineResponse.json(),
      auditResponse.json(),
      aiResponse.json(),
    ]);
    renderMetrics(pipeline);
    renderStageChart(pipeline);
    renderRegionChart(pipeline);
    renderNarrative(aiSummary);
    renderAiStatus(aiSummary);
    renderRows(pipeline);
    renderAudit(audit);
  } catch (error) {
    showError(error);
  }
}

init();
