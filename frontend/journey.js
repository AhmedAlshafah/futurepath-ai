/* The browser presents Python's results. It never calculates matching scores. */
(() => {
  "use strict";
  const DATA = JSON.parse(document.getElementById("futurepath-data").textContent);
  const pages = {home: "page-home", skills: "page-profile", matches: "page-matches", plan: "page-reskilling", market: "page-market"};
  const profile = DATA.profile || {};
  const view = DATA.uiState || {};
  const state = {
    step: Object.keys(pages).find(key => pages[key] === view.page) || "home",
    name: profile.name || "", degree: profile.degree || DATA.degrees[0],
    skills: new Set((profile.skills || []).map(skill => skill.toLowerCase())),
    interests: new Set(profile.interests || []), custom: profile.custom || [],
    tiers: profile.tiers || {}, persona: profile.persona || null,
    role: view.selectedRole || null, weeks: view.runway || 8,
    budget: view.budget || "free", pace: view.pace || "steady",
    completed: view.completed || {}, cvFound: view.cvFound || [],
  };
  const $ = selector => document.querySelector(selector);
  const esc = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[char]));
  const signature = skills => [...skills].map(skill => skill.toLowerCase()).sort().join("|");
  const scoredSignature = signature(profile.skills || []);
  let pending = false, toastTimer;

  function toast(message) {
    $("#toast-region").innerHTML = `<div class="toast">${esc(message)}</div>`;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => $("#toast-region").replaceChildren(), 3000);
  }
  function scoresCurrent() { return signature(state.skills) === scoredSignature; }
  function rank(){
    if (!state.skills.size || !scoresCurrent()) return [];
    return (DATA.backendMatches || []).map(result => ({
      ...result, match_pct: Number(result.match_pct),
    }));
  }
  function allSkills() {
    return [...new Set([...DATA.skills, ...state.custom])].sort((a, b) => a.localeCompare(b));
  }
  function activeRole() { return rank().find(result => result.role === state.role) || rank()[0]; }
  function invalidate() { state.role = null; state.completed = {}; state.persona = null; }
  function componentValue() {
    return {
      profile: {
        name: state.name, degree: state.degree,
        skills: allSkills().filter(skill => state.skills.has(skill.toLowerCase())).map(skill => DATA.skillValues?.[skill] || skill),
        interests: [...state.interests], custom: state.custom, tiers: state.tiers, persona: state.persona,
      },
      uiState: {
        page: pages[state.step], selectedRole: state.role, runway: state.weeks,
        budget: state.budget, pace: state.pace, completed: state.completed, cvFound: state.cvFound,
      },
    };
  }
  function publish() {
    window.parent.postMessage({type: "futurepath:state", value: componentValue()}, "*");
  }
  function go(step) {
    if (!(step in pages) || pending) return;
    if ((step === "matches" || step === "plan") && !state.skills.size) {
      state.step = "skills"; render();
      toast("Choose at least one skill before seeing matches.");
      window.scrollTo(0, 0);
      return;
    }
    // Ask Python for results after any skill edit. Never reuse old scores.
    if ((step === "matches" || step === "plan") && !scoresCurrent()) {
      state.step = step;
      pending = true;
      render();
      publish();
      window.scrollTo(0, 0);
      return;
    }
    state.step = step;
    render();
    window.scrollTo(0, 0);
    $("#main").focus({preventScroll: true});
    // Navigation and draft edits stay in this document. Sending every click to
    // Streamlit would reload the iframe and could overwrite a fast user's edits.
    // Submit the full current state when requesting scores or exporting a plan.
  }
  function tags(skills, kind = "") {
    return skills.map(skill => `<span class="tag ${kind}">${esc(skill)}</span>`).join("");
  }
  function skillsView() {
    return `
      <p class="eyebrow">Step 1 · start with what you know</p>
      <h1>Your skills, in your words.</h1>
      <p class="lede">Tell us a little about yourself and choose skills you have used. Then see which careers they connect to.</p>
      <section class="panel">
        <div class="panel-head"><div><h2>A little about you</h2><p>Optional context—not part of your match score.</p></div></div>
        <div class="field-grid">
          <div class="field"><label for="student-name">Name · optional</label><input id="student-name" maxlength="60" value="${esc(state.name)}" placeholder="Your name"></div>
          <div class="field"><label for="degree">Study area</label><select id="degree">${DATA.degrees.map(degree => `<option ${degree === state.degree ? "selected" : ""}>${esc(degree)}</option>`).join("")}</select></div>
        </div>
        <details class="disclosure"><summary>Add your interests · optional</summary><div class="disclosure-body">
          <div class="interests">${DATA.interests.map(interest => `<button class="pill ${state.interests.has(interest) ? "selected" : ""}" data-interest="${esc(interest)}" aria-pressed="${state.interests.has(interest)}">${esc(interest)}</button>`).join("")}</div>
          <p class="footnote">Interests help reflection but do not change backend scores.</p>
        </div></details>
      </section>
      <section class="panel">
        <div class="panel-head"><div><h2>What have you worked with?</h2><p>Self-reported skills only. Change them whenever you like.</p></div><span class="selected-flag">${state.skills.size} selected</span></div>
        <label class="label" for="skill-search">Find a skill</label><input class="search-input" id="skill-search" type="search" placeholder="Search the team’s skill catalog">
        <div class="skills-grid">${allSkills().map(skill => `<button class="skill ${state.skills.has(skill.toLowerCase()) ? "selected" : ""}" data-skill="${esc(skill)}" aria-pressed="${state.skills.has(skill.toLowerCase())}"><span>${esc(skill)}</span><span>${state.skills.has(skill.toLowerCase()) ? "Selected" : "Add"}</span></button>`).join("")}</div>
        <p class="helper" id="search-empty" hidden>No skills found. You can add a custom skill below.</p>
        ${DATA.skills.length ? "" : '<p class="error">No role-skill catalog is loaded. Add role data before comparing careers.</p>'}
        <p class="footnote">Catalog choices come from the team’s role-skill CSV. Custom skills only match if the backend recognizes them.</p>
        <details class="disclosure"><summary>Add a custom skill</summary><div class="disclosure-body">
          <form id="custom-form" class="inline-form"><input id="custom-input" maxlength="80" placeholder="e.g. Figma" aria-label="Custom skill"><button class="secondary" type="submit">Add</button></form>
          <p class="helper">Added to your selected skills. Unlisted terms do not increase your score.</p>
          <div class="skill-list spaced">${state.custom.map(skill => `<button class="pill" data-remove-custom="${esc(skill)}" aria-label="Remove custom skill ${esc(skill)}">${esc(skill)} · remove</button>`).join("")}</div>
        </div></details>
        <details class="disclosure"><summary>Use the CV / TXT keyword helper</summary><div class="disclosure-body">
          <p>Choose a plain-text CV. Recognized terms are suggestions, not verified skills.</p>
          <p class="helper">The file is read in your browser, not uploaded. Only confirmed skill selections are sent to the app.</p>
          <input class="file spaced" id="txt-file" aria-label="Plain-text CV" type="file" accept=".txt,text/plain">
          <div id="txt-status" class="helper" role="status"></div><div id="txt-found" class="skill-list spaced"></div>
        </div></details>
        <details class="disclosure"><summary>Self-assess your experience · optional</summary><div class="disclosure-body">
          <p>These levels are for reflection only and do not change matching.</p>
          <div class="snapshot-list">${allSkills().filter(skill => state.skills.has(skill.toLowerCase())).map((skill, i) => `<div class="snapshot-row"><label for="tier-${i}">${esc(skill)}</label><select id="tier-${i}" data-tier="${esc(skill)}"><option value="">Not set</option>${["Beginner", "Intermediate", "Advanced"].map(level => `<option ${state.tiers[skill] === level ? "selected" : ""}>${level}</option>`).join("")}</select></div>`).join("") || '<p class="helper">Select skills to add experience levels.</p>'}</div>
        </div></details>
        <details class="disclosure"><summary>Try an example profile</summary><div class="disclosure-body"><div class="opts">${Object.entries(DATA.personas).map(([key, example]) => `<button class="secondary" data-persona="${esc(key)}">${esc(example.degree)}</button>`).join("")}</div><p class="helper">Choosing an example replaces current selections with that sample. New sessions start empty.</p></div></details>
      </section>
      <div class="error" id="skill-error" role="alert" hidden></div>
      <div class="actions"><button class="secondary" data-go="home">← Introduction</button><div class="actions-right"><button class="primary" id="to-matches">See career matches →</button></div></div>`;
  }
  function resultEmpty(step) {
    return `<p class="eyebrow">${step === "plan" ? "Learning plan" : "Career matches"}</p>
      <h1>${pending ? "Comparing your skills…" : "Let’s start with your skills."}</h1>
      <section class="panel"><p role="status">${esc(pending ? "Waiting for the backend’s updated results." : DATA.matchError || "No backend matches are available for this profile.")}</p>
      ${pending ? "" : '<button class="secondary spaced" data-go="skills">Edit skills</button>'}</section>`;
  }
  function matchesView() {
    const list = rank(), active = activeRole();
    if (!active) return resultEmpty("matches");
    state.role = active.role;
    return `
      <p class="eyebrow">Step 2 · compare possibilities</p><h1>Here’s where your skills connect.</h1>
      <p class="lede">Choose a role to see what matched and what could be next.</p>
      <div class="notice">A weighted comparison against team-supplied role skills—not verified ability, career readiness, or a hiring guarantee.</div>
      <section class="panel"><div class="panel-head"><div><h2>Your closest matches</h2><p>${state.skills.size} selected skills · ranked by the backend</p></div><button class="quiet-link" data-go="skills">Edit skills</button></div>
        <div class="match-grid">${list.map((result, index) => `<button class="match ${result.role === active.role ? "active" : ""}" data-role="${esc(result.role)}" aria-pressed="${result.role === active.role}">
          <span class="rank">${result.role === active.role ? "Selected · " : ""}Match ${String(index + 1).padStart(2, "0")}</span><span class="match-name">${esc(result.role)}</span>
          <span class="match-bottom"><span class="pct">${result.match_pct}%</span><span class="subtle">${result.matched_skills.length} matched · ${result.missing_skills.length} gaps</span></span></button>`).join("")}</div>
      </section>
      <section class="panel"><div class="panel-head"><div><p class="eyebrow">Selected role</p><h2>${esc(active.role)}</h2><p>${active.match_pct}% backend match</p></div><span class="selected-flag">${active.matched_skills.length} of ${active.matched_skills.length + active.missing_skills.length} matched</span></div>
        <div class="detail"><div class="skill-state"><h3>Selected skills that matched</h3><div class="tags">${tags(active.matched_skills) || '<span class="subtle">No selected skills overlap yet.</span>'}</div></div>
          <div class="skill-state"><h3>Skills to learn for this role</h3><div class="tags">${tags(active.missing_skills, "gap") || '<span class="subtle">No listed benchmark gaps.</span>'}</div></div></div>
        <p class="footnote">Scores, order, and skill gaps come directly from the backend matching function. A listed gap is a benchmark comparison, not a verified deficiency.</p>
      </section>
      <div class="actions"><button class="secondary" data-go="skills">← Back to skills</button><div class="actions-right"><button class="primary" id="to-plan">Build my plan →</button></div></div>`;
  }
  function weekRange(index, count) {
    const first = Math.floor(index * state.weeks / count) + 1;
    const last = Math.max(first, Math.floor((index + 1) * state.weeks / count));
    return first === last ? `Week ${first}` : `Weeks ${first}–${last}`;
  }
  function resourceLink(resource, label) {
    if (!resource?.url?.startsWith("https://")) return "";
    return `<a class="resource" href="${esc(resource.url)}" target="_blank" rel="noopener noreferrer">${label} ↗</a>`;
  }
  function paidDescription(course) {
    return `${course.provider} · ${course.title} · ${Number(course.price).toFixed(2)} ${course.currency} · checked ${course.checked_on}`;
  }
  function planView() {
    const active = activeRole();
    if (!active) return resultEmpty("plan");
    state.role = active.role;
    const gaps = active.missing_skills;
    return `
      <p class="eyebrow">Step 3 · make it attainable</p><h1>A plan around your gaps.</h1>
      <p class="lede">Suggested study pace for ${esc(active.role)}. Each focus area comes from this role’s backend gap list.</p>
      <section class="panel"><div class="panel-head"><div><h2>Your plan settings</h2><p>Preferences change the plan, not your match scores.</p></div><button class="quiet-link" data-go="matches">Change role</button></div>
        <div class="field-grid"><div><div class="label">Time horizon</div><div class="opts">${[4, 8, 12].map(weeks => `<button class="pill ${state.weeks === weeks ? "selected" : ""}" data-weeks="${weeks}" aria-pressed="${state.weeks === weeks}">${weeks} weeks</button>`).join("")}</div></div>
          <div><div class="label">Resource preference</div><div class="opts">${[["free", "Free only"], ["lowcost", "Include low-cost"]].map(([value, label]) => `<button class="pill ${state.budget === value ? "selected" : ""}" data-budget="${value}" aria-pressed="${state.budget === value}">${label}</button>`).join("")}</div></div></div>
        <p class="footnote">The timeline is suggested pacing, not course duration. Check current course access and prices with the provider.</p>
      </section>
      <section class="panel"><div class="panel-head"><div><h2>${esc(active.role)} · ${gaps.length} focus ${gaps.length === 1 ? "area" : "areas"}</h2><p>Resources are loaded from the team’s course CSV.</p></div><span class="selected-flag">${state.weeks}-week pace</span></div>
        ${gaps.map((skill, index) => {
          const resource = DATA.resources[skill], paid = DATA.lowCost[skill], id = active.role + "|" + skill;
          return `<article class="plan-row"><span class="number">${String(index + 1).padStart(2, "0")}</span><div><div class="section-kicker">${weekRange(index, gaps.length)} · focus area</div><div class="plan-title">${esc(skill)}</div>
            <div class="plan-meta">${resource ? `${esc(resource.provider)} · ${esc(resource.title)}${resource.duration ? " · provider-listed " + esc(resource.duration) : ""}` : "No free learning resource is currently mapped for this skill."}</div>
            ${resourceLink(resource, "Open free learning resource")}
            ${state.budget === "lowcost" ? paid ? `<div class="plan-meta spaced">Optional paid course: ${esc(paidDescription(paid))}. Confirm current price.</div>${resourceLink(paid, "View course details")}` : '<div class="plan-meta spaced">No reviewed paid course is currently mapped.</div>' : ""}
            </div><label class="checkline"><input type="checkbox" data-complete="${esc(id)}" ${state.completed[id] ? "checked" : ""}>Done · self-reported</label></article>`;
        }).join("") || '<div class="notice">No listed benchmark gaps based on your self-reported selections. This is not a proficiency verification.</div>'}
      </section>
      <section class="panel soft"><div class="panel-head"><div><h2>Take your plan with you</h2><p>Download your role, pacing, learning links, and self-reported progress.</p></div></div>
        <div class="download-row"><button class="secondary" id="btn-export-reskill-md">Download plan · MD</button><button class="secondary" id="btn-sync-cal-reskill" ${gaps.length ? "" : "disabled"}>Download schedule · ICS</button></div>
        <p class="footnote">Selections stay in this app session; download your plan to keep a copy.</p>
      </section>
      <div class="actions"><button class="secondary" data-go="matches">← Back to matches</button><div class="actions-right"><button class="primary" data-go="skills">Edit my skills</button></div></div>`;
  }
  function snapshotRows() {
    if (!DATA.trendRows?.length) return `<p class="notice">${esc(DATA.trendError || "No job-market snapshot is available yet.")}</p>`;
    return DATA.trendRows.map(row => `<div class="snapshot-row"><span>${esc(row.role)}</span><span><strong>${esc(row.value)}</strong> listings
      · ${esc(row.retrieved_at || "Date unavailable")}${row.source_url?.startsWith("https://") ? ` · <a href="${esc(row.source_url)}" target="_blank" rel="noopener noreferrer">Source ↗</a>` : ""}</span></div>`).join("");
  }
  function marketView() {
    return `<p class="eyebrow">Context · optional</p><h1>A dated market snapshot.</h1>
      <p class="lede">Supporting context for your skills-based journey—not a forecast.</p>
      <section class="panel"><div class="panel-head"><div><h2>Saved remote listings by role</h2><p>Latest collection: ${esc(DATA.trendDate)} · ${esc(DATA.source)}</p></div></div>
        <div class="snapshot-list">${snapshotRows()}</div>
        <p class="footnote">Title-matched unique remote listings, not total vacancies or comparable measures of demand across roles. A zero is only zero matching listings in this saved collection, not zero demand. No live API feed, emerging-skill detection, or future-demand prediction is shown.</p>
      </section><div class="actions"><button class="secondary" data-go="home">← Introduction</button><button class="primary" data-go="skills">Go to my skills →</button></div>`;
  }
  function render() {
    const home = state.step === "home";
    $("#main").classList.toggle("is-home", home);
    $("#journey-header").hidden = home;
    $("#journey-progress").hidden = home;
    $("#journey-nav").hidden = home;
    const index = ["skills", "matches", "plan"].indexOf(state.step);
    $("#progress-label").textContent = state.step === "market" ? "Optional context" : `Step ${index + 1} of 3`;
    $("#progress-title").textContent = {skills: "Your skills", matches: "Career matches", plan: "Learning plan", market: "Market snapshot"}[state.step] || "";
    document.querySelectorAll(".step-line").forEach((element, i) => element.classList.toggle("done", index >= i));
    document.querySelectorAll("[data-step]").forEach(button => button.setAttribute("aria-current", String(button.dataset.step === state.step)));
    Object.values(pages).forEach(id => { document.getElementById(id).hidden = id !== pages[state.step]; });
    if (home) {
      $("#landing-snapshot").innerHTML = snapshotRows();
      $("#landing-snapshot-date").textContent = DATA.trendDate || "No data loaded";
      $("#landing-snapshot-source").textContent = DATA.source || "Source unavailable";
    } else {
      document.getElementById(pages[state.step]).innerHTML =
        state.step === "skills" ? skillsView() : state.step === "matches" ? matchesView() : state.step === "plan" ? planView() : marketView();
    }
    bind();
  }
  function download(name, type, text) {
    const url = URL.createObjectURL(new Blob([text], {type})), anchor = document.createElement("a");
    anchor.href = url; anchor.download = name; document.body.append(anchor); anchor.click(); anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 500);
  }
  function planText() {
    const active = activeRole();
    if (!active) return "";
    const lines = [
      `# FuturePath suggested study plan: ${active.role}`, "",
      `Profile: ${state.name || "Student"} · ${state.degree}`,
      `Pace: ${state.weeks} weeks`,
      `Resource preference: ${state.budget === "free" ? "Free only" : "Free + low-cost"}`,
      "Self-reported profile; backend benchmark comparisons are not proficiency or hiring verification.",
      "Timeline is suggested pace, not provider duration.", "",
    ];
    active.missing_skills.forEach((skill, index, gaps) => {
      const resource = DATA.resources[skill], paid = DATA.lowCost[skill];
      lines.push(`## ${weekRange(index, gaps.length)} — ${skill}${state.completed[active.role + "|" + skill] ? " [self-reported complete]" : ""}`);
      if (resource) {
        lines.push(`${resource.title} — ${resource.provider}`, resource.url);
        if (resource.duration) lines.push("Provider-listed time: " + resource.duration);
      } else lines.push("No free resource currently mapped.");
      if (state.budget === "lowcost" && paid) lines.push("Optional paid course: " + paidDescription(paid), paid.url);
      lines.push("");
    });
    if (!active.missing_skills.length) lines.push("No listed benchmark gaps.");
    return lines.join("\n");
  }
  function escapeICS(text) { return String(text).replace(/\\/g, "\\\\").replace(/\r\n|\r|\n/g, "\\n").replace(/,/g, "\\,").replace(/;/g, "\\;"); }
  function calendarText() {
    const active = activeRole();
    if (!active?.missing_skills.length) return "";
    const now = new Date(), start = new Date(now);
    start.setDate(start.getDate() + 1);
    const stamp = date => date.toISOString().slice(0, 19).replace(/[-:]/g, "") + "Z";
    const dateOnly = date => `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, "0")}${String(date.getDate()).padStart(2, "0")}`;
    const lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//FuturePath//Study Plan//EN", "CALSCALE:GREGORIAN"];
    active.missing_skills.forEach((skill, index, gaps) => {
        const resource = DATA.resources[skill], paid = DATA.lowCost[skill];
        const day = new Date(start); day.setDate(start.getDate() + Math.floor(index * state.weeks / gaps.length) * 7);
        const end = new Date(day); end.setDate(day.getDate() + 1);
        const description = [
          `Role: ${active.role} · ${state.weeks} weeks · ${weekRange(index, gaps.length)}`,
          state.budget === "free" ? "Free only" : "Free + low-cost",
          resource ? `${resource.title} — ${resource.url}` : "No free resource currently mapped.",
          state.budget === "lowcost" && paid ? `Optional paid: ${paidDescription(paid)} — ${paid.url}` : "",
          state.completed[active.role + "|" + skill] ? "Marked complete (self-reported)." : "",
          "Suggested study reminder, not provider duration or verified completion.",
        ].filter(Boolean).join("\n");
        lines.push("BEGIN:VEVENT", `UID:futurepath-${index}-${now.getTime()}@local`,
          "DTSTAMP:" + stamp(now), "DTSTART;VALUE=DATE:" + dateOnly(day), "DTEND;VALUE=DATE:" + dateOnly(end),
          "SUMMARY:" + escapeICS("FuturePath study: " + skill), "DESCRIPTION:" + escapeICS(description), "END:VEVENT");
    });
    lines.push("END:VCALENDAR");
    // RFC 5545 folding: limit physical lines to 75 UTF-8 octets.
    return lines.map(line => {
      const encoder = new TextEncoder(), chunks = []; let current = "", bytes = 0;
      for (const char of line) {
        const size = encoder.encode(char).length;
        if (bytes + size > 75) { chunks.push(current); current = " "; bytes = 1; }
        current += char; bytes += size;
      }
      chunks.push(current); return chunks.join("\r\n");
    }).join("\r\n") + "\r\n";
  }
  function renderFound() {
    const container = $("#txt-found");
    if (!container) return;
    container.innerHTML = state.cvFound.map(skill => `<button class="pill" data-found="${esc(skill)}" ${state.skills.has(skill.toLowerCase()) ? "disabled" : ""}>${esc(skill)} · ${state.skills.has(skill.toLowerCase()) ? "selected" : "add as self-reported"}</button>`).join("");
    container.querySelectorAll("[data-found]").forEach(button => button.onclick = () => {
      state.skills.add(button.dataset.found.toLowerCase()); invalidate(); render();
      $("#txt-file").closest("details").open = true;
      toast(button.dataset.found + " added as self-reported.");
    });
  }
  function readTxt(file) {
    if (!file) return;
    const status = $("#txt-status");
    if (!file.name.toLowerCase().endsWith(".txt") || file.size > 500000) {
      status.textContent = "Choose a plain-text .txt file under 500 KB."; return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result || "");
      state.cvFound = DATA.skills.filter(skill => {
        const pattern = skill.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        const aliases = skill === "Excel" ? [pattern, "Microsoft Excel"] : skill === "Power BI" ? [pattern, "Microsoft Power BI"] : [pattern];
        return aliases.some(term => new RegExp("(^|[^a-z0-9])" + term + "([^a-z0-9]|$)", "i").test(text));
      });
      status.textContent = state.cvFound.length + " keyword(s) found. Confirm only skills you actually have.";
      renderFound();
    };
    reader.onerror = () => { status.textContent = "Could not read that file. Choose another plain-text CV."; };
    reader.readAsText(file);
  }
  function bind() {
    document.querySelectorAll("[data-go]").forEach(button => button.onclick = () => go(button.dataset.go));
    document.querySelectorAll("[data-step]").forEach(button => button.onclick = () => go(button.dataset.step));
    $("#start-journey").onclick = () => go("skills");
    if (state.step !== "skills") {
      document.querySelectorAll("[data-role]").forEach(button => button.onclick = () => { state.role = button.dataset.role; render(); });
      const toPlan = $("#to-plan"); if (toPlan) toPlan.onclick = () => go("plan");
      for (const [attr, property, transform] of [["weeks", "weeks", Number], ["budget", "budget", String]]) {
        document.querySelectorAll(`[data-${attr}]`).forEach(button => button.onclick = () => {
          state[property] = transform(button.dataset[attr]);
          if (attr === "weeks") state.pace = state.weeks === 4 ? "focused" : "steady";
          render();
        });
      }
      document.querySelectorAll("[data-complete]").forEach(input => input.onchange = () => { state.completed[input.dataset.complete] = input.checked; });
      const md = $("#btn-export-reskill-md");
      if (md) md.onclick = () => { publish(); download("futurepath-study-plan.md", "text/markdown;charset=utf-8", planText()); };
      const ics = $("#btn-sync-cal-reskill");
      if (ics) ics.onclick = () => { publish(); download("futurepath-study-plan.ics", "text/calendar;charset=utf-8", calendarText()); };
      return;
    }
    $("#student-name").oninput = event => { state.name = event.target.value; state.persona = null; };
    $("#degree").onchange = event => { state.degree = event.target.value; state.persona = null; };
    $("#skill-search").oninput = event => {
      const query = event.target.value.trim().toLowerCase(); let visible = 0;
      document.querySelectorAll("[data-skill]").forEach(button => { button.hidden = !button.dataset.skill.toLowerCase().includes(query); if (!button.hidden) visible++; });
      $("#search-empty").hidden = visible > 0;
    };
    document.querySelectorAll("[data-skill]").forEach(button => button.onclick = () => {
      const key = button.dataset.skill.toLowerCase();
      state.skills.has(key) ? state.skills.delete(key) : state.skills.add(key);
      invalidate(); render();
    });
    document.querySelectorAll("[data-interest]").forEach(button => button.onclick = () => {
      const key = button.dataset.interest;
      state.interests.has(key) ? state.interests.delete(key) : state.interests.add(key);
      state.persona = null; button.classList.toggle("selected"); button.setAttribute("aria-pressed", String(state.interests.has(key)));
    });
    document.querySelectorAll("[data-tier]").forEach(select => select.onchange = () => {
      if (select.value) state.tiers[select.dataset.tier] = select.value;
      else delete state.tiers[select.dataset.tier];
    });
    document.querySelectorAll("[data-persona]").forEach(button => button.onclick = () => {
      const example = DATA.personas[button.dataset.persona];
      state.name = example.name; state.degree = example.degree;
      state.skills = new Set(example.skills.filter(skill => DATA.skills.some(value => value.toLowerCase() === skill.toLowerCase())).map(skill => skill.toLowerCase()));
      state.interests = new Set(example.interests); state.custom = []; state.tiers = {}; state.cvFound = [];
      invalidate(); state.persona = button.dataset.persona; render(); toast("Example profile loaded.");
    });
    $("#custom-form").onsubmit = event => {
      event.preventDefault();
      const skill = $("#custom-input").value.trim();
      if (!skill) return;
      const existing = allSkills().find(value => value.toLowerCase() === skill.toLowerCase());
      if (existing) { state.skills.add(existing.toLowerCase()); }
      else { state.custom.push(skill); state.skills.add(skill.toLowerCase()); }
      invalidate(); render(); toast("Skill selected. Only backend-recognized skills contribute to matching.");
    };
    document.querySelectorAll("[data-remove-custom]").forEach(button => button.onclick = () => {
      state.custom = state.custom.filter(skill => skill !== button.dataset.removeCustom);
      state.skills.delete(button.dataset.removeCustom.toLowerCase()); delete state.tiers[button.dataset.removeCustom];
      invalidate(); render();
    });
    $("#txt-file").onchange = event => readTxt(event.target.files?.[0]);
    renderFound();
    $("#to-matches").onclick = () => {
      if (!state.skills.size) {
        $("#skill-error").hidden = false; $("#skill-error").textContent = "Choose at least one skill before seeing matches."; return;
      }
      go("matches");
    };
  }
  // Parent bridge reloads this document only when Python sends a changed payload.
  render();
})();
