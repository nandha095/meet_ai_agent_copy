// ✅ Automatically detect server URL
const BASE_URL = window.location.origin;

let proposalsVisible = false;


/****************************
 * HANDLE SESSION EXPIRY
 ****************************/
function handleSessionExpired() {
  alert("Session expired. Please login again.");
  localStorage.removeItem("token");
  window.location.href = "index.html";
}


/****************************
 * GOOGLE CONNECT
 ****************************/
function connectGoogle() {
  const token = localStorage.getItem("token");
  if (!token) return handleSessionExpired();

  document.getElementById("ai-status").innerText =
    "🤖 Connecting to Google...";

  window.location.href = `${BASE_URL}/auth/google/login`;
}


/****************************
 * OUTLOOK CONNECT
 ****************************/
function connectOutlook() {
  const token = localStorage.getItem("token");
  if (!token) return handleSessionExpired();

  document.getElementById("ai-status").innerText =
    "🤖 Connecting to Outlook...";

  window.location.href =
    `${BASE_URL}/auth/outlook/login?token=${token}`;
}


/****************************
 * CHECK EMAIL CONNECTION STATUS
 ****************************/
async function checkEmailConnectionStatus() {
  const token = localStorage.getItem("token");
  if (!token) return;

  let google = false;
  let outlook = false;

  try {
    const g = await fetch(
      `${BASE_URL}/auth/google/status`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    google = (await g.json()).connected;
  } catch {}

  try {
    const o = await fetch(
      `${BASE_URL}/auth/outlook/status`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    outlook = (await o.json()).connected;
  } catch {}

  updateAIStatus(google, outlook);
}


/****************************
 * UPDATE AI STATUS + BUTTONS
 ****************************/
function updateAIStatus(google, outlook) {
  const statusEl = document.getElementById("ai-status");

  const googleConnect = document.getElementById("google-connect-btn");
  const googleDisconnect = document.getElementById("google-disconnect-btn");

  const outlookConnect = document.getElementById("outlook-connect-btn");
  const outlookDisconnect = document.getElementById("outlook-disconnect-btn");

  if (!googleConnect || !googleDisconnect || !outlookConnect || !outlookDisconnect) {
    console.error("Connect / Disconnect buttons not found in DOM");
    return;
  }

  if (google && outlook) {
    statusEl.innerText = "✅ Google & Outlook connected — AI is active";
  } else if (google) {
    statusEl.innerText = "✅ Google connected — AI is active";
  } else if (outlook) {
    statusEl.innerText = "✅ Outlook connected — AI is active";
  } else {
    statusEl.innerText = "🔌 No email connected";
  }

  googleConnect.style.display = google ? "none" : "inline-flex";
  googleDisconnect.style.display = google ? "inline-flex" : "none";

  outlookConnect.style.display = outlook ? "none" : "inline-flex";
  outlookDisconnect.style.display = outlook ? "inline-flex" : "none";
}


/****************************
 * DISCONNECT
 ****************************/
async function disconnectGoogle() {
  const token = localStorage.getItem("token");
  if (!token) return;

  if (!confirm("Disconnect Google account?")) return;

  await fetch(`${BASE_URL}/auth/google/disconnect`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  });

  checkEmailConnectionStatus();
}

async function disconnectOutlook() {
  const token = localStorage.getItem("token");
  if (!token) return;

  if (!confirm("Disconnect Outlook account?")) return;

  await fetch(`${BASE_URL}/auth/outlook/disconnect`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  });

  checkEmailConnectionStatus();
}


/****************************
 * SEND PROPOSAL
 ****************************/
async function sendProposal() {
  const token = localStorage.getItem("token");
  if (!token) return handleSessionExpired();

  const formData = new FormData();
  formData.append("email", to_email.value);
  formData.append("subject", subject.value);
  formData.append("body", body.value);
  formData.append("provider", provider.value);

  for (const f of attachment.files) {
    formData.append("attachments", f);
  }

  const res = await fetch(
    `${BASE_URL}/emails/emails/send-proposal`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    }
  );

  if (res.status === 401) return handleSessionExpired();

  document.getElementById("ai-action").innerText =
    res.ok ? "✅ Proposal sent successfully." : "❌ Failed to send proposal";

  if (res.ok) loadProposals();
}


/****************************
 * LOAD + RENDER PROPOSALS
 ****************************/
async function loadProposals() {
  const token = localStorage.getItem("token");
  if (!token) return;

  const res = await fetch(
    `${BASE_URL}/emails/emails/`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  renderProposals(await res.json());
}


function renderProposals(proposals) {
  const container = document.getElementById("proposal-list");
  container.innerHTML = "";

  if (!proposals.length) {
    container.innerHTML = "<p>No proposals sent yet.</p>";
    return;
  }

  proposals.forEach(p => {
    const cls = p.status.toLowerCase().replaceAll(" ", "_");
    container.innerHTML += `
      <div class="proposal-card">
        <b>${p.client_email}</b><br/>
        ${p.subject}<br/>
        <span class="status ${cls}">${p.status}</span>

        <button class="view-btn" onclick="toggleProposalDetails(${p.id})">
          View Details
        </button>

        <div id="details-${p.id}" class="proposal-details" style="display:none">
          <p>${p.body || "—"}</p>
        </div>
      </div>
    `;
  });
}


function toggleProposalDetails(id) {
  const el = document.getElementById(`details-${id}`);
  el.style.display = el.style.display === "none" ? "block" : "none";
}


/****************************
 * TOGGLE PROPOSALS LIST
 ****************************/
function toggleProposals() {
  const list = document.getElementById("proposal-list");
  const btn = document.getElementById("toggle-proposals-btn");

  if (!proposalsVisible) {
    list.style.display = "block";
    btn.innerText = "🙈 Hide Proposals";
    loadProposals();
  } else {
    list.style.display = "none";
    btn.innerText = "👁 View Proposals";
  }

  proposalsVisible = !proposalsVisible;
}


/****************************
 * PAGE LOAD
 ****************************/
window.addEventListener("load", () => {
  checkEmailConnectionStatus();
});
