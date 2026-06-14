const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const percent = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 0,
});

const snapshotTime = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  hour: "numeric",
  minute: "2-digit",
  timeZoneName: "short",
});

const $ = (selector) => document.querySelector(selector);
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function formatSnapshotTime(metadata) {
  const timestamp = metadata.sourceUpdatedAt || metadata.generatedAt;
  const parsed = timestamp ? new Date(timestamp) : null;
  if (parsed && !Number.isNaN(parsed.valueOf())) {
    return snapshotTime.format(parsed);
  }
  return metadata.dataAsOf;
}

/* Animate a currency value from 0 → target for the video flip.
   The final value is set immediately so the number is always correct even if
   requestAnimationFrame never fires (e.g. a throttled background tab). */
function countUp(el, target) {
  if (!el) return;
  el.textContent = money.format(target);
  if (reducedMotion) return;
  const duration = 900;
  const start = performance.now();
  const step = (now) => {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = money.format(Math.round(target * eased));
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

function renderHeader(pipeline) {
  const { metadata } = pipeline;
  const source = metadata.sourceSystem || "CRM";
  const revision = metadata.sourceRevision ? `rev ${metadata.sourceRevision}` : "snapshot";
  $("#lastRefresh").textContent = `Data as of ${formatSnapshotTime(metadata)}`;
  $("#crmSource").textContent = `${source} ${revision}`;
}

function renderGoal(pipeline) {
  const m = pipeline.metrics;
  const ahead = m.closedWonDelta >= 0;

  const delta = $("#goalDelta");
  delta.textContent = `${money.format(Math.abs(m.closedWonDelta))} ${ahead ? "ahead of goal" : "behind goal"}`;
  delta.className = `delta-pill ${ahead ? "ahead" : "behind"}`;

  $("#goalValue").textContent = `Goal ${money.format(m.closedWonGoal)}`;
  $("#attainmentValue").textContent = `${percent.format(m.closedWonAttainment)} of goal`;

  countUp($("#closedWonValue"), m.closedWon);

  const fill = $("#goalProgress");
  fill.classList.toggle("ahead", ahead);
  const width = Math.min(100, Math.round(m.closedWonAttainment * 100));
  // The 0% start is painted from the inline style on load, so setting the target
  // here transitions via CSS — no requestAnimationFrame needed.
  fill.style.width = `${width}%`;
}

function renderKpis(pipeline) {
  const m = pipeline.metrics;
  countUp($("#pipelineValue"), m.pipelineValue);
  countUp($("#weightedValue"), m.weightedPipeline);
  countUp($("#openValue"), m.openPipeline);
  $("#recordCount").textContent = `${m.totalRecords} opportunities`;
  $("#openMeta").textContent = `${m.topRegion} region leads`;
}

function sourceChips(sources) {
  return sources.map((source) => `<code>${source}</code>`).join("");
}

function renderChange(summary) {
  const banner = $("#changeBanner");
  if (!summary.change) {
    banner.hidden = true;
    return;
  }
  banner.hidden = false;
  $("#changeHeadline").textContent = summary.change.headline;
  $("#changeBody").textContent = summary.change.body;
  $("#changeSources").innerHTML = sourceChips(summary.change.sources);
}

function renderAI(summary) {
  $("#copyHeadline").textContent = summary.hero.headline;
  $("#copyBody").textContent = summary.hero.body;
  $("#copySources").innerHTML = sourceChips(summary.hero.sources);

  $("#cardGrid").innerHTML = summary.cards
    .map(
      (card) => `
      <article class="ai-card">
        <h4>${card.title}</h4>
        <p>${card.body}</p>
        <div class="source-row">${sourceChips(card.sources)}</div>
      </article>`,
    )
    .join("");
}

function stageClass(name) {
  if (name === "Closed Won") return "won";
  if (name === "Closed Lost") return "lost";
  return "";
}

function renderStageBars(pipeline) {
  const stages = pipeline.summaries.byStage;
  const max = Math.max(...stages.map((s) => s.amount), 1);
  $("#stageBars").innerHTML = stages
    .map((s) => {
      const amountPct = (s.amount / max) * 100;
      const weightedPct = (s.weightedAmount / max) * 100;
      return `
        <div class="bar-row ${stageClass(s.name)}">
          <div class="bar-label">${s.name}<small>${s.count} ${s.count === 1 ? "deal" : "deals"}</small></div>
          <div class="bar-track">
            <div class="bar-amount" data-w="${amountPct}"></div>
            <div class="bar-weighted" data-w="${weightedPct}"></div>
          </div>
          <div class="bar-value">${money.format(s.amount)}</div>
        </div>`;
    })
    .join("");

  // Flush layout so the freshly-inserted 0%-width bars paint before we set the
  // target width — that makes the CSS transition animate, without needing rAF.
  void $("#stageBars").offsetHeight;
  document.querySelectorAll("#stageBars [data-w]").forEach((el) => {
    el.style.width = `${el.dataset.w}%`;
  });
}

function renderOppTable(pipeline) {
  const opps = [...pipeline.opportunities].sort((a, b) => b.amount - a.amount);
  $("#oppCount").textContent = `${opps.length} records`;
  $("#oppRows").innerHTML = opps
    .map(
      (o) => `
      <tr>
        <td class="acct">${o.account}</td>
        <td>${o.owner}</td>
        <td><span class="stage-tag ${stageClass(o.stage)}">${o.stage}</span></td>
        <td class="num">${money.format(o.amount)}</td>
        <td class="num">${percent.format(o.probability)}</td>
      </tr>`,
    )
    .join("");
}

function renderLineage(audit, pipeline) {
  const passing = audit.checks.filter((c) => c.status === "pass").length;
  $("#auditStatus").textContent = `${passing} validation checks passed`;
  $("#sourceHash").textContent = `sha256 ${pipeline.metadata.sourceSha256.slice(0, 12)}…`;
}

function showError(error) {
  document.querySelector("main").innerHTML = `
    <div class="error-state">
      <strong>Could not load CRM demo data.</strong>
      <p>${error.message}</p>
    </div>`;
}

async function init() {
  try {
    // Cache-bust so a refresh always shows the latest CRM data, even though
    // GitHub Pages caches static assets for ~10 minutes.
    const bust = `?t=${Date.now()}`;
    const noStore = { cache: "no-store" };
    const responses = await Promise.all([
      fetch(`./data/pipeline.json${bust}`, noStore),
      fetch(`./data/audit-log.json${bust}`, noStore),
      fetch(`./data/ai-summary.json${bust}`, noStore),
    ]);
    if (responses.some((r) => !r.ok)) {
      throw new Error("Run npm run generate, then refresh the page.");
    }
    const [pipeline, audit, summary] = await Promise.all(responses.map((r) => r.json()));

    renderHeader(pipeline);
    renderChange(summary);
    renderGoal(pipeline);
    renderKpis(pipeline);
    renderAI(summary);
    renderStageBars(pipeline);
    renderOppTable(pipeline);
    renderLineage(audit, pipeline);
  } catch (error) {
    showError(error);
  }
}

init();
