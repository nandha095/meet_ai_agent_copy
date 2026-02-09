// ✅ Automatically detect server URL
const BASE_URL = window.location.origin;

let proposalsVisible = false;
const REQUIRED_SUBJECT = "Project Proposal";


/****************************
 * HANDLE SESSION EXPIRY
 ****************************/
function handleSessionExpired() {
  alert("Session expired. Please login again.");
  localStorage.removeItem("token");
  window.location.href = "login.html";
}

function logout() {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  fetch(`${BASE_URL}/auth/logout`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  }).finally(() => {
    localStorage.removeItem("token");
    window.location.href = "login.html";
  });
}
window.logout = logout;


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
    if (g.status === 401) return handleSessionExpired();
    google = (await g.json()).connected;
  } catch {}

  try {
    const o = await fetch(
      `${BASE_URL}/auth/outlook/status`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (o.status === 401) return handleSessionExpired();
    outlook = (await o.json()).connected;
  } catch {}

  updateAIStatus(google, outlook);
}


/****************************
 * UPDATE AI STATUS + BUTTONS
 ****************************/
function updateAIStatus(google, outlook) {
  const statusEl = document.getElementById("ai-status");
  const inboxEl = document.getElementById("stat-inbox");

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
    if (inboxEl) inboxEl.innerText = "Google + Outlook";
  } else if (google) {
    statusEl.innerText = "✅ Google connected — AI is active";
    if (inboxEl) inboxEl.innerText = "Google";
  } else if (outlook) {
    statusEl.innerText = "✅ Outlook connected — AI is active";
    if (inboxEl) inboxEl.innerText = "Outlook";
  } else {
    statusEl.innerText = "🔌 No email connected";
    if (inboxEl) inboxEl.innerText = "Not connected";
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

  const res = await fetch(`${BASE_URL}/auth/google/disconnect`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  });
  if (res.status === 401) return handleSessionExpired();
  checkEmailConnectionStatus();
}

async function disconnectOutlook() {
  const token = localStorage.getItem("token");
  if (!token) return;

  if (!confirm("Disconnect Outlook account?")) return;

  const res = await fetch(`${BASE_URL}/auth/outlook/disconnect`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  });
  if (res.status === 401) return handleSessionExpired();
  checkEmailConnectionStatus();
}


/****************************
 * SEND PROPOSAL
 ****************************/
async function sendProposal() {
  const token = localStorage.getItem("token");
  if (!token) return handleSessionExpired();

  const actionEl = document.getElementById("ai-action");
  const sendBtn = document.getElementById("send-proposal-btn");

  if (!to_email.value || !body.value) {
    if (actionEl) {
      actionEl.className = "ai-action error";
      actionEl.innerText = "Please enter client email and message.";
    }
    return;
  }

  subject.value = REQUIRED_SUBJECT;

  const formData = new FormData();
  formData.append("email", to_email.value);
  formData.append("subject", REQUIRED_SUBJECT);
  formData.append("body", body.value);
  formData.append("provider", provider.value);

  for (const f of attachment.files) {
    formData.append("attachments", f);
  }

  try {
    if (sendBtn) {
      sendBtn.disabled = true;
      sendBtn.textContent = "Sending...";
    }

    if (actionEl) {
      actionEl.className = "ai-action";
      actionEl.innerText = "Sending proposal...";
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

    if (actionEl) {
      actionEl.className = res.ok ? "ai-action success" : "ai-action error";
      actionEl.innerText = res.ok
        ? "✅ Proposal sent successfully."
        : "❌ Failed to send proposal";
    }

    if (res.ok) loadProposals();
  } finally {
    if (sendBtn) {
      sendBtn.disabled = false;
      sendBtn.textContent = "Send proposal";
    }
  }
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
    container.innerHTML = "<p class=\"muted\">No proposals sent yet.</p>";
    return;
  }

  proposals.forEach(p => {
    const cls = p.status.toLowerCase().replaceAll(" ", "_");
    const createdAt = p.created_at ? new Date(p.created_at).toLocaleString() : "";
    const provider = p.provider ? p.provider.toUpperCase() : "";
    container.innerHTML += `
      <div class="proposal-card">
        <div class="proposal-header">
          <div>
            <p class="proposal-email">${p.client_email}</p>
            <p class="proposal-subject">${p.subject}</p>
          </div>
          <div class="proposal-meta">
            <span class="badge provider">${provider}</span>
            <span class="status ${cls}">${p.status}</span>
          </div>
        </div>
        <div class="proposal-footer">
          <p class="proposal-date">${createdAt}</p>
          <button class="view-btn" onclick="toggleProposalDetails(${p.id})">View Details</button>
        </div>
        <div id="details-${p.id}" class="proposal-details" style="display:none">
          <p>${p.body || "—"}</p>
        </div>
      </div>
    `;
  });
}

async function loadStats() {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const res = await fetch(
      `${BASE_URL}/emails/emails/stats`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (res.status === 401) return handleSessionExpired();
    const data = await res.json();
    const proposalsEl = document.getElementById("stat-proposals");
    const meetingsEl = document.getElementById("stat-meetings");
    const updatedEl = document.getElementById("stat-updated");
    if (proposalsEl) proposalsEl.innerText = data.proposals_sent ?? 0;
    if (meetingsEl) meetingsEl.innerText = data.meetings_scheduled ?? 0;
    if (updatedEl) {
      const now = new Date();
      updatedEl.innerText = `Last updated: ${now.toLocaleTimeString()}`;
    }
  } catch {}
}

async function loadNextMeeting() {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const res = await fetch(
      `${BASE_URL}/meetings/next`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (res.status === 401) return handleSessionExpired();
    const data = await res.json();
    const container = document.getElementById("next-meeting");
    if (!container) return;
    if (!data.meeting) {
      container.innerHTML = "<p class=\"muted\">No upcoming meetings.</p>";
      return;
    }
    const start = data.meeting.start_time ? new Date(data.meeting.start_time).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }) : "";
    const end = data.meeting.end_time ? new Date(data.meeting.end_time).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }) : "";
    const link = data.meeting.meet_link || "#";
    container.innerHTML = `
      <p><strong>Start:</strong> ${start}</p>
      <p><strong>End:</strong> ${end}</p>
      <a class="link" href="${link}" target="_blank">Open meeting link</a>
    `;
  } catch {}
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
  const subjectInput = document.getElementById("subject");
  if (subjectInput) {
    subjectInput.value = REQUIRED_SUBJECT;
    subjectInput.readOnly = true;
  }
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", logout);
  }
  checkEmailConnectionStatus();
  loadStats();
  loadNextMeeting();
  setInterval(loadStats, 60000);
  setInterval(loadNextMeeting, 60000);
});
