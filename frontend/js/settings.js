const BASE_URL = window.location.origin;

function handleSessionExpired() {
  localStorage.removeItem("token");
  window.location.href = "login.html";
}

async function changePassword() {
  const token = localStorage.getItem("token");
  if (!token) return handleSessionExpired();

  const currentEl = document.getElementById("current_password");
  const newEl = document.getElementById("new_password");
  const currentErr = document.getElementById("current-password-error");
  const newErr = document.getElementById("new-password-error");
  const msgEl = document.getElementById("settings-message");
  const btn = document.getElementById("change-password-btn");

  if (msgEl) {
    msgEl.className = "message";
    msgEl.textContent = "";
  }
  if (currentErr) currentErr.textContent = "";
  if (newErr) newErr.textContent = "";
  if (currentEl) currentEl.classList.remove("input-error");
  if (newEl) newEl.classList.remove("input-error");

  if (!currentEl.value) {
    currentEl.classList.add("input-error");
    if (currentErr) currentErr.textContent = "Please enter your current password.";
    return;
  }

  if (!newEl.value) {
    newEl.classList.add("input-error");
    if (newErr) newErr.textContent = "Please enter your new password.";
    return;
  }

  if (newEl.value.length < 8 || !/[A-Z]/.test(newEl.value) || !/[a-z]/.test(newEl.value) || !/\d/.test(newEl.value) || !/[^\w\s]/.test(newEl.value)) {
    newEl.classList.add("input-error");
    if (newErr) newErr.textContent = "8+ chars, upper, lower, number, symbol.";
    return;
  }

  try {
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Updating...";
    }

    const res = await fetch(`${BASE_URL}/auth/change-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        current_password: currentEl.value,
        new_password: newEl.value
      })
    });

    if (res.status === 401) return handleSessionExpired();
    const data = await res.json();

    if (res.ok) {
      if (msgEl) {
        msgEl.className = "message success";
        msgEl.textContent = "Password changed. Please log in again.";
      }
      localStorage.removeItem("token");
      setTimeout(() => {
        window.location.href = "login.html";
      }, 1200);
    } else {
      const msg = data.detail || "Failed to change password";
      if (msg.toLowerCase().includes("current")) {
        currentEl.classList.add("input-error");
        if (currentErr) currentErr.textContent = msg;
      } else if (msg.toLowerCase().includes("password")) {
        newEl.classList.add("input-error");
        if (newErr) newErr.textContent = msg;
      } else if (msgEl) {
        msgEl.className = "message error";
        msgEl.textContent = msg;
      }
    }
  } catch (err) {
    if (msgEl) {
      msgEl.className = "message error";
      msgEl.textContent = "Server unreachable. Please try again.";
    }
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Change password";
    }
  }
}

async function logoutEverywhere() {
  const token = localStorage.getItem("token");
  if (!token) return handleSessionExpired();

  const btn = document.getElementById("logout-all-btn");
  const msgEl = document.getElementById("settings-message");

  try {
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Logging out...";
    }

    const res = await fetch(`${BASE_URL}/auth/logout-all`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }
    });

    if (res.status === 401) return handleSessionExpired();

    localStorage.removeItem("token");
    if (msgEl) {
      msgEl.className = "message success";
      msgEl.textContent = "Logged out everywhere.";
    }
    setTimeout(() => {
      window.location.href = "login.html";
    }, 800);
  } catch (err) {
    if (msgEl) {
      msgEl.className = "message error";
      msgEl.textContent = "Server unreachable. Please try again.";
    }
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Logout everywhere";
    }
  }
}

window.changePassword = changePassword;
window.logoutEverywhere = logoutEverywhere;

async function loadProfile() {
  const token = localStorage.getItem("token");
  if (!token) return handleSessionExpired();

  try {
    const res = await fetch(`${BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.status === 401) return handleSessionExpired();
    const data = await res.json();

    const emailEl = document.getElementById("profile-email");
    const googleEl = document.getElementById("google-status");
    const outlookEl = document.getElementById("outlook-status");

    if (emailEl) emailEl.textContent = data.email || "—";
    if (googleEl) {
      googleEl.classList.toggle("connected", !!data.google_connected);
      googleEl.textContent = data.google_connected ? "Google connected" : "Google not connected";
    }
    if (outlookEl) {
      outlookEl.classList.toggle("connected", !!data.outlook_connected);
      outlookEl.textContent = data.outlook_connected ? "Outlook connected" : "Outlook not connected";
    }
  } catch {}
}

window.addEventListener("load", () => {
  loadProfile();
  loadAudit();
});

async function loadAudit() {
  const token = localStorage.getItem("token");
  if (!token) return handleSessionExpired();

  try {
    const res = await fetch(`${BASE_URL}/auth/audit`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.status === 401) return handleSessionExpired();
    const data = await res.json();
    const list = document.getElementById("audit-list");
    if (!list) return;
    if (!data.length) {
      list.innerHTML = "<p class=\"muted\">No recent activity.</p>";
      return;
    }
    list.innerHTML = data.map(item => {
      const time = item.created_at ? new Date(item.created_at).toLocaleString() : "";
      const detail = item.detail ? ` — ${item.detail}` : "";
      return `<div class="audit-item"><span class="badge">${item.action}</span><span class="audit-time">${time}${detail}</span></div>`;
    }).join("");
  } catch {}
}
