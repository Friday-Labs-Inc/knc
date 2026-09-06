/* KNC — portal client script (paste into Builder Protected Page).
   Renders project state; gate buttons -> decide_gate; comments -> post_comment. */

(function () {
  const $ = (id) => document.getElementById(id);

  async function call(method, args) {
    const r = await fetch("/api/method/" + method, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Frappe-CSRF-Token": (window.csrf_token || ""),
      },
      body: JSON.stringify(args || {}),
    });
    const body = await r.json();
    if (!r.ok) throw new Error(body.exception || "Request failed");
    return body.message;
  }

  function renderTimeline(state) {
    const el = $("knc-timeline");
    if (!el) return;
    el.innerHTML = state.tasks.map((t) => {
      const cls = t.status === "Completed" ? "done" : t.status === "Working" ? "active" : "upcoming";
      return `<div class="knc-task knc-${cls}">
        <span class="knc-task-status">${t.status === "Completed" ? "✓" : ""}</span>
        <span class="knc-task-subject">${t.subject}</span>
      </div>`;
    }).join("");
  }

  function renderGate(state) {
    const el = $("knc-gate");
    if (!el) return;
    if (!state.gate.open) { el.style.display = "none"; return; }
    el.style.display = "";
    const isG1 = state.gate.which === "Gate 1";
    el.innerHTML = `
      <h3>${state.gate.task}</h3>
      ${state.gate.paused ? "<p class='knc-paused'>Timeline paused — waiting on you.</p>" : ""}
      ${isG1 ? `
        <div class="knc-directions">
          ${["A", "B", "C"].map((d) => `<button class="knc-choose" data-d="${d}">Choose direction ${d}</button>`).join("")}
        </div>` : `
        <button id="knc-approve">Approve</button>
        <button id="knc-refine">Request refinements</button>`}
      <textarea id="knc-gate-comments" placeholder="Comments (optional)"></textarea>`;

    el.querySelectorAll(".knc-choose").forEach((b) =>
      b.addEventListener("click", () => decide("Gate 1", "Direction Selected", b.dataset.d)));
    if ($("knc-approve")) $("knc-approve").addEventListener("click", () => decide("Gate 2", "Approved"));
    if ($("knc-refine")) $("knc-refine").addEventListener("click", () => decide("Gate 2", "Refinement Requested"));
  }

  let PROJECT = null;

  async function decide(gate, decision, direction) {
    try {
      await call("knc.api.v1.decide_gate", {
        project: PROJECT, gate: gate, decision: decision,
        chosen_direction: direction || null,
        comments: ($("knc-gate-comments") || {}).value || null,
      });
      load();
    } catch (e) { alert(e.message); }
  }

  async function load() {
    try {
      const state = await call("knc.api.v1.get_project_state", {});
      if (!state.projects.length) {
        if ($("knc-phase")) $("knc-phase").textContent = "No active engagement.";
        return;
      }
      PROJECT = state.project.name;
      if ($("knc-phase")) {
        const active = state.tasks.find((t) => t.status === "Working");
        $("knc-phase").textContent = active ? active.subject : state.project.status;
      }
      renderTimeline(state);
      renderGate(state);
      if ($("knc-decisions")) {
        $("knc-decisions").innerHTML = state.decisions.map((d) =>
          `<div class="knc-decision">${d.gate} · round ${d.round} · ${d.decision}${d.chosen_direction ? " — " + d.chosen_direction : ""}</div>`
        ).join("");
      }
    } catch (e) {
      if ($("knc-phase")) $("knc-phase").textContent = "Could not load — are you logged in?";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    load();
    if ($("knc-comment-send")) $("knc-comment-send").addEventListener("click", async () => {
      const box = $("knc-comment-box");
      if (!box || !box.value.trim()) return;
      await call("knc.api.v1.post_comment", { project: PROJECT, content: box.value.trim() });
      box.value = "";
      load();
    });
  });
})();
