"use strict";

const choices = document.querySelectorAll('input[name="stage"]');
const views = document.querySelectorAll("[data-view]");
const reasoning = document.getElementById("reasoning");
const diagram = document.querySelector(".diagram");
const title = document.getElementById("graph-title");
const description = document.getElementById("graph-description");
const diagramMode = document.getElementById("diagram-mode");
const diagramScope = document.getElementById("diagram-scope");
const answerKey = document.getElementById("answer-key");
const scenes = document.querySelectorAll("[data-scene]");
const caseCopy = document.querySelectorAll("[data-case-copy]");
const jumps = Array.from(document.querySelectorAll("[data-jump]"));
const previous = document.getElementById("previous");
const next = document.getElementById("next");
const position = document.getElementById("position");
const headings = ["opening-title", "case-title", "change-title", "purpose", "requirements-title"];
const actions = [
  "Open a saved apartment case →", "See what measurements add →", "Return to the window question →",
  "See what Crucis has to solve →"
];
const comparisonStages = ["Read the diagram", "Meet the method", "Compare the arrows"];
const comparisonHeadings = ["case-title", "method-title", "proposal-title"];
const comparisonActions = ["Meet the method →", "See its proposed arrows →"];
const measurementStages = ["Add a clue", "Earlier proposal", "Final diagram"];
const measurementActions = ["Compare the diagrams →", "Show the final diagram →"];
const measurementViews = ["measurements", "earlier", "final"];
let current = 0;
let comparisonPhase = 0;
let measurementPhase = 0;

function showGraph() {
  const referenceOnly = current === 1 && comparisonPhase < 2;
  const selected = current === 2 ? measurementViews[measurementPhase] : "proposal";
  const final = selected === "final";
  const checkingTwoArrows = current === 2 && measurementPhase > 0;
  diagram.style.alignSelf = checkingTwoArrows ? "start" : "";
  diagramScope.textContent = checkingTwoArrows ? "Other arrows omitted" : "Only relevant arrows shown";
  for (const view of views) {
    view.toggleAttribute("hidden", referenceOnly || !view.dataset.view.split(" ").includes(selected));
  }
  for (const choice of choices) choice.checked = choice.value === (final ? "final" : "intermediate");
  const compared = (final ? "Final diagram" : "Earlier proposal") + " against the simulation";
  diagramMode.textContent = referenceOnly ? "How the simulation works" :
    current === 2 ? compared : "Compare the two explanations";
  title.textContent = referenceOnly ? "How opening time can affect heat in the simulation" : compared;
  description.textContent = referenceOnly
    ? "The simulation links opening time to window opening, ventilation and heat exposure."
    : final
      ? "Of the two arrows being checked, the one from heat exposure to first opening time is gone. The remaining arrow points from how much the window is open to first opening time. The simulation points the other way."
      : "The earlier proposal points from heat exposure back to first opening time." +
        (selected === "earlier" ? " Its arrow from first opening time to how much the window is open was left out of the first check. It agrees with the simulation." :
          " The simulation has a chain of arrows from first opening time to heat exposure.");
  answerKey.textContent = final ? "From the final diagram" : "From the earlier proposal";
  answerKey.hidden = referenceOnly;
  reasoning.hidden = referenceOnly || selected !== "proposal";
  reasoning.open = false;
}

function showScene(index, focus = true) {
  current = index;
  let heading = headings[index];
  if (index === 1) heading = comparisonHeadings[comparisonPhase];
  if (index === 2 && measurementPhase === 0) heading = "measure-title";
  for (const scene of scenes) scene.hidden = !scene.dataset.scene.split(" ").includes(String(index));
  for (const copy of caseCopy) {
    const phases = index === 1 ? copy.dataset.comparePhase : copy.dataset.measurementPhase;
    const phase = index === 1 ? comparisonPhase : measurementPhase;
    const phaseApplies = !phases || phases.split(" ").includes(String(phase));
    copy.hidden = copy.dataset.caseCopy !== String(index) || !phaseApplies;
  }
  for (const [step, jump] of jumps.entries()) {
    if (step === index) jump.setAttribute("aria-current", "step");
    else jump.removeAttribute("aria-current");
  }
  if (index === 1 || index === 2) {
    document.querySelector(".exhibit").setAttribute("aria-labelledby", heading);
    showGraph();
  }
  updateControls();
  const atHandoff = index === jumps.length - 1;
  const handoffHash = "#next-questions";
  if (atHandoff !== (location.hash === handoffHash)) {
    const url = new URL(location.href);
    url.hash = atHandoff ? handoffHash : "";
    history.replaceState(null, "", url);
  }
  if (focus) document.getElementById(heading).focus({preventScroll: true});
}

function updateControls() {
  previous.disabled = current === 0;
  next.hidden = current === jumps.length - 1;
  let action = actions[current];
  if (current === 1) action = comparisonActions[comparisonPhase] ?? action;
  if (current === 2) action = measurementActions[measurementPhase] ?? action;
  if (!next.hidden) next.textContent = action;
  position.textContent = "Step " + (current + 1) + " of " + jumps.length +
    (current === 1 ? " · " + comparisonStages[comparisonPhase] : "") +
    (current === 2 ? " · " + measurementStages[measurementPhase] : "");
}

function move(direction) {
  const phase = comparisonPhase + direction;
  if (current === 1 && phase >= 0 && phase < comparisonStages.length) {
    comparisonPhase = phase;
    showScene(current);
  } else if (current === 2 && measurementPhase + direction >= 0 &&
      measurementPhase + direction < measurementStages.length) {
    measurementPhase += direction;
    showScene(current);
  } else {
    if (current === 1 && direction === 1) measurementPhase = 0;
    if (current === 2 && direction === -1) comparisonPhase = comparisonStages.length - 1;
    showScene(current + direction);
  }
}

for (const choice of choices) choice.addEventListener("change", () => {
  measurementPhase = choice.value === "final" ? 2 : 1;
  showScene(current, false);
});
for (const [index, jump] of jumps.entries()) jump.addEventListener("click", () => {
  if (index === 2) measurementPhase = 0;
  showScene(index);
});
previous.addEventListener("click", () => move(-1));
next.addEventListener("click", () => move(1));
document.addEventListener("keydown", (event) => {
  if (event.altKey || event.ctrlKey || event.metaKey || event.target.closest("input, textarea, select")) return;
  const direction = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
  const index = current + direction;
  if (!direction || index < 0 || index >= jumps.length) return;
  event.preventDefault();
  move(direction);
});

if (location.hash === "#next-questions") showScene(jumps.length - 1, false);
