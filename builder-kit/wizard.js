/* KNC — /start wizard client script (paste into Builder page).
   Steps auto-save to knc.api.v1.save_step; final step calls
   submit_brief and redirects to Stripe checkout. */

(function () {
  const TOTAL_STEPS = 6;
  let step = 1;
  let brief = localStorage.getItem("knc_brief") || null;
  let token = localStorage.getItem("knc_brief_token") || null;

  const $ = (id) => document.getElementById(id);
  const stepEl = (n) => $("knc-step-" + n);

  function show(n) {
    for (let i = 1; i <= TOTAL_STEPS; i++) {
      if (stepEl(i)) stepEl(i).style.display = i === n ? "" : "none";
    }
    if ($("knc-review")) $("knc-review").style.display = n > TOTAL_STEPS ? "" : "none";
    if ($("knc-prev")) $("knc-prev").style.display = n === 1 ? "none" : "";
    if ($("knc-next")) $("knc-next").style.display = n > TOTAL_STEPS ? "none" : "";
    if ($("knc-pay")) $("knc-pay").style.display = n > TOTAL_STEPS ? "" : "none";
    step = n;
  }

  function collect(n) {
    const data = {};
    stepEl(n).querySelectorAll("[data-knc-field]").forEach((el) => {
      const f = el.getAttribute("data-knc-field");
      data[f] = el.type === "checkbox" ? (el.checked ? 1 : 0) : el.value;
    });
    // Step 5: personality checkboxes + reference rows
    if (n === 5) {
      data.personality = Array.from(
        stepEl(5).querySelectorAll("[data-knc-personality]:checked")
      ).map((el) => el.value);
      data.references = Array.from(
        stepEl(5).querySelectorAll("[data-knc-reference-url]")
      ).map((el) => ({ type: "URL", url: el.value }))
        .filter((r) => r.url);
    }
    return data;
  }

  async function call(method, args) {
    const r = await fetch("/api/method/" + method, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Frappe-CSRF-Token": (window.csrf_token || ""),
      },
      body: JSON.stringify(args),
    });
    const body = await r.json();
    if (!r.ok) throw new Error((body._server_messages || body.exception || "Request failed"));
    return body.message;
  }

  async function saveStep(n) {
    const res = await call("knc.api.v1.save_step", {
      step: n, data: JSON.stringify(collect(n)), brief: brief, token: token,
    });
    brief = res.brief;
    token = res.token;
    localStorage.setItem("knc_brief", brief);
    localStorage.setItem("knc_brief_token", token);
  }

  async function next() {
    try {
      await saveStep(step);
      show(step + 1);
    } catch (e) {
      alert(e.message || "Could not save — check required fields.");
    }
  }

  async function pay() {
    try {
      $("knc-pay").disabled = true;
      const res = await call("knc.api.v1.submit_brief", { brief: brief, token: token });
      localStorage.removeItem("knc_brief");
      localStorage.removeItem("knc_brief_token");
      window.location.href = res.payment_url; // Stripe checkout
    } catch (e) {
      $("knc-pay").disabled = false;
      alert(e.message || "Could not submit.");
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    show(1);
    if ($("knc-next")) $("knc-next").addEventListener("click", next);
    if ($("knc-prev")) $("knc-prev").addEventListener("click", () => show(step - 1));
    if ($("knc-pay")) $("knc-pay").addEventListener("click", pay);
    // Capacity notice
    call("knc.api.v1.check_capacity", {}).then((c) => {
      if (!c.available && $("knc-capacity")) $("knc-capacity").textContent = c.message;
    }).catch(() => {});
  });
})();
