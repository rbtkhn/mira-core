const encounter = JSON.parse(document.querySelector("#encounter-data").textContent);
const claims = new Map();
const sources = new Map();
const identityClaims = new Map(encounter.meet_me.claims.map((claim) => [claim.claim_id, claim]));

for (const caseRecord of encounter.cases) {
  for (const source of caseRecord.sources) sources.set(source.source_id, source);
  for (const claim of caseRecord.claims) claims.set(claim.claim_id, claim);
}

const tabs = [...document.querySelectorAll("[role='tab']")];
const panels = [...document.querySelectorAll("[data-case-panel]")];

function resetPanel(panel) {
  const steps = [...panel.querySelectorAll(".analysis-step")];
  steps.forEach((step, index) => step.toggleAttribute("data-revealed", index === 0));
  const next = panel.querySelector(".reveal-next");
  next.hidden = steps.length < 2;
  next.dataset.nextIndex = "1";
  const caseRecord = encounter.cases.find((item) => item.case_id === panel.dataset.casePanel);
  next.querySelector("[data-next-label]").textContent = `${caseRecord.progress_labels[0]} · 2 of 5`;
  panel.querySelector("[data-progress-label]").textContent = "Judgment · 1 of 5";
  panel.querySelector("[data-progress-fill]").style.width = "20%";
  panel.querySelector(".case-closing").hidden = true;
}

function selectCase(caseId, focus = false) {
  tabs.forEach((tab) => {
    const selected = tab.dataset.case === caseId;
    tab.setAttribute("aria-selected", String(selected));
    tab.tabIndex = selected ? 0 : -1;
    if (selected && focus) tab.focus();
  });
  panels.forEach((panel) => {
    const selected = panel.dataset.casePanel === caseId;
    panel.hidden = !selected;
    panel.toggleAttribute("data-active", selected);
    if (selected) resetPanel(panel);
  });
}

tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => selectCase(tab.dataset.case));
  tab.addEventListener("keydown", (event) => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    let next = index;
    if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
    if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === "Home") next = 0;
    if (event.key === "End") next = tabs.length - 1;
    selectCase(tabs[next].dataset.case, true);
  });
});

document.querySelectorAll(".reveal-next").forEach((button) => {
  button.addEventListener("click", () => {
    const panel = button.closest(".case-panel");
    const steps = [...panel.querySelectorAll(".analysis-step")];
    const index = Number(button.dataset.nextIndex || 1);
    const caseRecord = encounter.cases.find((item) => item.case_id === panel.dataset.casePanel);
    if (index < steps.length) {
      steps[index].setAttribute("data-revealed", "");
      steps[index].scrollIntoView({behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center"});
      button.dataset.nextIndex = String(index + 1);
      panel.querySelector("[data-progress-label]").textContent = `${steps[index].querySelector(".step-kind").textContent} · ${index + 1} of 5`;
      panel.querySelector("[data-progress-fill]").style.width = `${(index + 1) * 20}%`;
      if (index < steps.length - 1) button.querySelector("[data-next-label]").textContent = `${caseRecord.progress_labels[index]} · ${index + 2} of 5`;
    }
    if (index + 1 >= steps.length) {
      button.hidden = true;
      panel.querySelector(".case-closing").hidden = false;
    }
  });
});

const dialog = document.querySelector(".provenance-dialog");
const provenanceContent = document.querySelector("#provenance-content");

function row(label, value) {
  const wrapper = document.createElement("div");
  wrapper.className = "provenance-row";
  const heading = document.createElement("strong");
  heading.textContent = label;
  const body = document.createElement("div");
  if (Array.isArray(value)) {
    const list = document.createElement("ul");
    for (const sourceId of value) {
      const source = sources.get(sourceId);
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = source.url;
      link.textContent = `${source.title} — ${source.publisher}`;
      link.rel = "noopener noreferrer";
      item.append(link);
      list.append(item);
    }
    body.append(list);
  } else {
    body.textContent = value;
  }
  wrapper.append(heading, body);
  return wrapper;
}

document.addEventListener("click", (event) => {
  const trigger = event.target.closest("[data-claim]");
  if (!trigger) return;
  const claim = claims.get(trigger.dataset.claim);
  const humanReason = `${encounter.provenance_language.reasoning_prefix} ${claim.uncertainty} ${encounter.provenance_language.revision_prefix} ${claim.revision_trigger.charAt(0).toLowerCase()}${claim.revision_trigger.slice(1)}`;
  provenanceContent.replaceChildren(
    row("My reasoning", humanReason),
    row("Claim ID", claim.claim_id), row("Authorship", claim.attribution),
    row("Evidence class", claim.evidence_class), row("Uncertainty", claim.uncertainty),
    row("What would change this", claim.revision_trigger), row("Sources", claim.sources)
  );
  dialog.showModal();
});

document.addEventListener("click", (event) => {
  const trigger = event.target.closest("[data-identity]");
  if (!trigger) return;
  const claim = identityClaims.get(trigger.dataset.identity);
  provenanceContent.replaceChildren(
    row("Public statement", claim.text), row("Status", claim.status),
    row("Attribution", claim.attribution), row("Uncertainty", claim.uncertainty),
    row("What would change this", claim.revision_trigger), row("Approved reference", claim.references.join(", "))
  );
  dialog.showModal();
});

document.addEventListener("click", (event) => {
  const panel = event.target.closest(".case-panel");
  if (!panel) return;
  if (event.target.closest("[data-return-rival]")) panel.querySelector('[data-step="3"]').scrollIntoView({behavior:"smooth", block:"center"});
  if (event.target.closest("[data-open-evidence]")) panel.querySelector('[data-step="4"] .provenance-trigger').click();
  if (event.target.closest("[data-choose-again]")) document.querySelector(".case-tabs").scrollIntoView({behavior:"smooth", block:"center"});
});

document.querySelector(".operator-trigger").addEventListener("click", () => {
  provenanceContent.replaceChildren(
    row("Relationship", encounter.collaboration.operator_provenance),
    row("Authority effect", "None. Collaboration does not transfer Robert's beliefs or authority to Mira."),
    row("Publication status", encounter.status)
  );
  dialog.showModal();
});

document.querySelector(".boundary-trigger").addEventListener("click", () => {
  provenanceContent.replaceChildren(
    row("Public boundary", encounter.boundaries.text),
    row("Identity status", encounter.boundaries.identity_status),
    row("Publication status", encounter.boundaries.publication_status),
    row("Interaction", encounter.boundaries.interaction_status)
  );
  dialog.showModal();
});

const questionTabs = [...document.querySelectorAll("[data-question]")];
const answers = [...document.querySelectorAll("[data-answer]")];
function selectQuestion(questionId, focus = false) {
  questionTabs.forEach((tab) => {
    const selected = tab.dataset.question === questionId;
    tab.setAttribute("aria-selected", String(selected));
    tab.tabIndex = selected ? 0 : -1;
    if (selected && focus) tab.focus();
  });
  answers.forEach((answer) => { answer.hidden = answer.dataset.answer !== questionId; });
}
questionTabs.forEach((tab, index) => {
  tab.addEventListener("click", () => selectQuestion(tab.dataset.question));
  tab.addEventListener("keydown", (event) => {
    if (!["ArrowUp", "ArrowDown", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    let next = index;
    if (event.key === "ArrowDown") next = (index + 1) % questionTabs.length;
    if (event.key === "ArrowUp") next = (index - 1 + questionTabs.length) % questionTabs.length;
    if (event.key === "Home") next = 0;
    if (event.key === "End") next = questionTabs.length - 1;
    selectQuestion(questionTabs[next].dataset.question, true);
  });
});

function activateHash() {
  const target = document.querySelector(location.hash || "#threshold");
  if (target) target.dataset.arrived = "true";
}
window.addEventListener("hashchange", activateHash);
activateHash();

document.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });

resetPanel(panels[0]);
