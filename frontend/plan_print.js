/* Standalone, escaped print document. No libraries, requests, or scoring. */
(() => {
  "use strict";
  const esc = value => String(value ?? "").replace(/[&<>"']/g, char =>
    ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[char]));
  function courseHTML(course, label) {
    if (!course) return `<p class="muted">No ${esc(label.toLowerCase())} resource currently mapped.</p>`;
    const link = typeof course.url === "string" && course.url.startsWith("https://")
      ? `<a href="${esc(course.url)}">${esc(course.url)}</a>` : "";
    return `<div class="course"><p><strong>${esc(label)}:</strong> ${esc(course.title)} — ${esc(course.provider)}</p>
      ${course.duration ? `<p>Provider-listed time: ${esc(course.duration)}</p>` : ""}
      ${course.priceNote ? `<p>${esc(course.priceNote)}</p>` : ""}${link}</div>`;
  }
  function html(plan) {
    return `<!doctype html><html lang="en"><head><meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>FuturePath — ${esc(plan.role)} reskilling plan</title>
      <style>
        @page { size: A4; margin: 17mm; }
        * { box-sizing: border-box; }
        body { margin: 0; color: #171717; background: white; font: 14px/1.55 Arial, sans-serif; }
        main, .toolbar { max-width: 840px; margin: 0 auto; padding: 28px; }
        .toolbar { background: #f3f4f6; border-bottom: 1px solid #ddd; }
        .toolbar p { margin: 8px 0 0; }
        button { background: #171717; color: white; padding: 12px 18px; border: 0; border-radius: 7px; cursor: pointer; font: inherit; }
        .brand { font-weight: 700; letter-spacing: .04em; }
        h1 { font-size: 30px; line-height: 1.2; margin: 12px 0; }
        h2 { font-size: 19px; margin: 24px 0 10px; }
        h3 { font-size: 17px; margin: 4px 0 10px; }
        p { margin: 6px 0; }
        .muted, .note { color: #555; }
        .summary { padding: 16px 0; border-block: 1px solid #ccc; margin: 20px 0; }
        .focus { padding: 16px 0; border-bottom: 1px solid #ddd; }
        .course { margin: 12px 0; }
        a { color: #171717; text-decoration: underline; overflow-wrap: anywhere; word-break: break-word; }
        .note { margin-top: 24px; font-size: 12px; }
        @media print {
          .toolbar { display: none !important; }
          main { max-width: none; padding: 0; }
          h1, h2, h3 { break-after: avoid; }
          .summary, .course { break-inside: avoid; }
          p { orphans: 3; widows: 3; }
        }
      </style></head><body>
      <div class="toolbar"><button id="print-plan" type="button">Print / Save as PDF</button>
        <p>Choose <strong>Save as PDF</strong> as the print destination. If you cancel, use this button to try again.</p></div>
      <main><div class="brand">FuturePath</div><h1>Your reskilling path</h1>
        <p class="muted">Prepared ${esc(plan.date)}</p>
        <section class="summary">
          <p><strong>Profile:</strong> ${esc(plan.name || "Student")} · ${esc(plan.degree)}</p>
          <p><strong>Target role:</strong> ${esc(plan.role)}</p>
          <p><strong>Backend benchmark match:</strong> ${esc(plan.match)}%</p>
          <p><strong>Pace:</strong> ${esc(plan.weeks)} weeks · <strong>Resources:</strong> ${esc(plan.preference)}</p>
          <p><strong>Current skills:</strong> ${plan.skills.map(esc).join(", ") || "None selected"}</p>
        </section>
        <h2>What to learn next</h2>
        ${plan.gaps.map((gap, index) => `<section class="focus">
          <p class="muted">${index + 1}. ${esc(gap.when)}</p><h3>${esc(gap.skill)}</h3>
          <p>Status: ${gap.complete ? "Complete (self-reported)" : "Not marked complete"}</p>
          ${courseHTML(gap.free, "Free")}
          ${plan.includePaid ? courseHTML(gap.paid, "Optional paid") : ""}
        </section>`).join("") || "<p>No listed benchmark gaps based on your current selections. This is not a proficiency verification.</p>"}
        <footer class="note">
          <p>The timeline is suggested study pacing, not provider duration. Check current course availability and prices with the provider.</p>
          <p>Skills and progress are self-reported. Backend benchmark comparisons are not proficiency or hiring verification.</p>
        </footer>
      </main></body></html>`;
  }
  globalThis.FuturePathPrint = {html};
})();
