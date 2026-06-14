const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const percent = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 0,
});

const $ = (selector) => document.querySelector(selector);

function goalStatus(delta) {
  const direction = delta >= 0 ? "ahead of goal" : "behind goal";
  return `${money.format(Math.abs(delta))} ${direction}`;
}

function renderFacts(pipeline) {
  const { metadata, metrics } = pipeline;
  const source = metadata.sourceSystem || "CRM";
  const revision = metadata.sourceRevision ? `rev ${metadata.sourceRevision}` : "snapshot";

  $("#revisionBadge").textContent = `${source} ${revision}`;
  $("#lastRefresh").textContent = `Data as of ${metadata.dataAsOf}`;
  $("#crmSource").textContent = `${source} ${revision}`;
  $("#closedWonValue").textContent = money.format(metrics.closedWon);
  $("#goalDelta").textContent = goalStatus(metrics.closedWonDelta);
  $("#goalDelta").className = metrics.closedWonDelta >= 0 ? "positive" : "negative";
  $("#goalValue").textContent = money.format(metrics.closedWonGoal);
  $("#attainmentValue").textContent = `${percent.format(metrics.closedWonAttainment)} attainment`;
  $("#pipelineValue").textContent = money.format(metrics.pipelineValue);
  $("#recordCount").textContent = `${metrics.totalRecords} CRM records`;
  $("#sourceHash").textContent = `sha256 ${metadata.sourceSha256.slice(0, 12)}`;
}

function renderCopy(summary) {
  $("#aiStatus").textContent = summary.metadata.generatedBy;
  $("#copyHeadline").textContent = summary.hero.headline;
  $("#copyBody").textContent = summary.hero.body;
  $("#copySources").innerHTML = summary.hero.sources
    .map((source) => `<code>${source}</code>`)
    .join("");
}

function renderAudit(audit) {
  const passing = audit.checks.filter((check) => check.status === "pass").length;
  $("#auditStatus").textContent = `${passing} validation checks passed`;
}

function showError(error) {
  document.querySelector("main").innerHTML = `
    <div class="error-state">
      <strong>Could not load CRM demo data.</strong>
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
      throw new Error("Run npm run generate, then refresh the page.");
    }

    const [pipeline, audit, summary] = await Promise.all([
      pipelineResponse.json(),
      auditResponse.json(),
      aiResponse.json(),
    ]);

    renderFacts(pipeline);
    renderCopy(summary);
    renderAudit(audit);
  } catch (error) {
    showError(error);
  }
}

init();
