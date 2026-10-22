// AgroGuard AI frontend. The backend is the source of truth for verification results.
const API_BASE = "http://127.0.0.1:5000";

const form = document.getElementById("check-form");
const resultCard = document.getElementById("result-card");
const submitButton = document.getElementById("submit-button");
const sampleButton = document.getElementById("sample-button");

function renderError(message) {
  resultCard.className = "result-card";
  resultCard.innerHTML = `
    <span class="result-status unknown">CANNOT CONNECT</span>
    <h3>Verification unavailable</h3>
    <p class="result-summary">${escapeHtml(message)}</p>
    <div class="result-warning">Check that the Flask backend is running and that API_BASE in script.js points to your deployed Render service.</div>`;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  })[char]);
}

function renderReport(data) {
  const statusClass = data.status === "match" ? "match" : data.status === "mismatch" ? "mismatch" : "unknown";
  const title = data.status === "match" ? "Demo reference match found" :
                data.status === "mismatch" ? "Mismatch detected" : "Insufficient evidence";
  const label = data.status === "match" ? "DEMO MATCH FOUND" :
                data.status === "mismatch" ? "MISMATCH DETECTED" : "CANNOT VERIFY";
  const bullets = (data.checks || []).map(item => `
    <li><span class="report-bullet">${item.passed === true ? "?" : item.passed === false ? "!" : "?"}</span>
    <span><strong>${escapeHtml(item.name)}:</strong> ${escapeHtml(item.detail)}</span></li>`).join("");
  const source = data.reference
    ? `<div class="report-source"><strong>Reference record</strong>${escapeHtml(data.reference.id)} — ${escapeHtml(data.reference.title)}<br>${escapeHtml(data.reference.source)}<br><em>${escapeHtml(data.reference.note)}</em></div>`
    : `<div class="report-source"><strong>Reference record</strong>No matching record was found in the local demo database.</div>`;
  resultCard.className = "result-card";
  resultCard.innerHTML = `
    <span class="result-status ${statusClass}">${label}</span>
    <div class="eyebrow">YOUR VERIFICATION REPORT</div>
    <h3>${title}</h3>
    <p class="result-summary">${escapeHtml(data.summary)}</p>
    <ul class="report-list">${bullets}</ul>
    ${source}
    <div class="result-warning">${escapeHtml(data.safety_notice)}</div>`;
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  submitButton.disabled = true;
  submitButton.textContent = "Checking demo records…";
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  try {
    const response = await fetch(`${API_BASE}/api/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The server could not process this request.");
    renderReport(data);
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (error) {
    renderError(error.message || "Could not reach the verification service.");
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = 'Verify proposed treatment <span aria-hidden="true">?</span>';
  }
});

sampleButton.addEventListener("click", () => {
  document.getElementById("crop").value = "tomato";
  document.getElementById("stage").value = "vegetative";
  document.getElementById("problem").value = "early_blight";
  document.getElementById("product").value = "DEMO-TOMATO-01";
  document.getElementById("source").value = "DEMO-REF-001";
  document.getElementById("checker").scrollIntoView({ behavior: "smooth", block: "start" });
});

// Friendly startup check. The UI remains usable if the backend is temporarily asleep.
fetch(`${API_BASE}/api/health`).catch(() => {});
