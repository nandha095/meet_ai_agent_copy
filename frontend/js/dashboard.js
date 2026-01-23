/****************************
 * HANDLE SESSION EXPIRY
 ****************************/
function handleSessionExpired() {
  alert("Session expired. Please login again.");
  localStorage.removeItem("token");
  window.location.href = "index.html"; // login page
}
/****************************
 * GOOGLE CONNECT
 ****************************/
function connectGoogle() {
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please login first");
    window.location.href = "index.html";
    return;
  }

  const statusEl = document.getElementById("ai-status");
  if (statusEl) {
    statusEl.innerText = "🤖 Connecting to Google...";
  }

  window.location.href = "http://127.0.0.1:8000/auth/google/login";
}

/****************************
 * OUTLOOK CONNECT
 ****************************/
function connectOutlook() {
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please login first");
    return;
  }

  const statusEl = document.getElementById("ai-status");
  if (statusEl) {
    statusEl.innerText = "🤖 Connecting to Outlook...";
  }

  window.location.href =
    `http://127.0.0.1:8000/auth/outlook/login?token=${token}`;
}

/****************************
 * SEND PROPOSAL
 ****************************/
async function sendProposal() {
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please login first");
    window.location.href = "index.html";
    return;
  }

  const email = document.getElementById("to_email").value.trim();
  const subject = document.getElementById("subject").value.trim();
  const body = document.getElementById("body").value.trim();
  const provider = document.getElementById("provider").value;
  const files = document.getElementById("attachment").files;

  if (!email || !subject || !body) {
    alert("Please fill all required fields.");
    return;
  }

  // File validation
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  for (let i = 0; i < files.length; i++) {
    if (files[i].size > MAX_FILE_SIZE) {
      alert(`File "${files[i].name}" exceeds 10MB limit.`);
      return;
    }
  }

  const actionEl = document.getElementById("ai-action");
  actionEl.innerText =
    "🧠 AI is sending proposal and monitoring replies...";

  const formData = new FormData();
  formData.append("email", email);
  formData.append("subject", subject);
  formData.append("body", body);
  formData.append("provider", provider);

  for (let i = 0; i < files.length; i++) {
    formData.append("attachments", files[i]);
  }

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/emails/emails/send-proposal",
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData
      }
    );

    if (response.status === 401) {
      alert("Session expired. Please login again.");
      localStorage.removeItem("token");
      window.location.href = "index.html";
      return;
    }

    const data = await response.json();

    if (response.ok) {
      actionEl.innerText = "✅ Proposal sent successfully.";

      // Clear form
      document.getElementById("to_email").value = "";
      document.getElementById("subject").value = "";
      document.getElementById("body").value = "";
      document.getElementById("attachment").value = "";
      document.getElementById("file-list").innerHTML = "";

      // 🔥 Refresh proposal list
      loadProposals();
    } else {
      actionEl.innerText = "❌ Failed to send proposal.";
      alert(data.detail || "Failed to send proposal");
    }
  } catch (error) {
    console.error(error);
    actionEl.innerText = "❌ Network error.";
  }
}

/****************************
 * LOAD PROPOSALS (FETCH)
 ****************************/
async function loadProposals() {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/emails/emails/",
      {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      console.error("Failed to fetch proposals");
      return;
    }

    const proposals = await response.json();
    renderProposals(proposals);
  } catch (err) {
    console.error("Error loading proposals", err);
  }
}

/****************************
 * RENDER PROPOSALS (DYNAMIC UI)
 ****************************/
function renderProposals(proposals) {
  const container = document.getElementById("proposal-list");
  container.innerHTML = "";

  if (!proposals || proposals.length === 0) {
    container.innerHTML = "<p>No proposals sent yet.</p>";
    return;
  }

  proposals.forEach(p => {
    let statusColor =
      p.status === "MEETING_SCHEDULED" ? "green" :
      p.status === "REJECTED" ? "red" :
      "orange";

    container.innerHTML += `
      <div class="proposal-card">
        <div><b>To:</b> ${p.client_email}</div>
        <div><b>Subject:</b> ${p.subject}</div>
        <div>
          <b>Status:</b>
          <span style="color:${statusColor}">
            ${p.status}
          </span>
        </div>
        <div class="proposal-meta">
          ${new Date(p.created_at).toLocaleString()}
          • ${p.provider.toUpperCase()}
        </div>
      </div>
    `;
  });
}

/****************************
 * FILE LIST PREVIEW
 ****************************/
document.getElementById("attachment").addEventListener("change", function () {
  const list = document.getElementById("file-list");
  list.innerHTML = "";

  for (const file of this.files) {
    list.innerHTML += `📎 ${file.name}<br>`;
  }
});

/****************************
 * PAGE LOAD
 ****************************/
window.onload = () => {
  loadProposals();
};
