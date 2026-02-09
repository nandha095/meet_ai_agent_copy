const BASE_URL = window.location.origin;

function handleSessionExpired() {
  localStorage.removeItem("token");
  window.location.href = "login.html";
}

function logout() {
  const token = localStorage.getItem("token");
  if (!token) return handleSessionExpired();

  fetch(`${BASE_URL}/auth/logout`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  }).finally(() => {
    localStorage.removeItem("token");
    window.location.href = "login.html";
  });
}

let currentPage = 1;
let pageSize = 10;

async function loadActivity() {
  const token = localStorage.getItem("token");
  if (!token) return handleSessionExpired();

  const res = await fetch(
    `${BASE_URL}/emails/emails/activity-paged?page=${currentPage}&size=${pageSize}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (res.status === 401) return handleSessionExpired();
  const data = await res.json();
  renderActivity(data.items || []);
  updatePagination(data.total || 0);
}

function renderActivity(items) {
  const container = document.getElementById("activity-list");
  container.innerHTML = "";

  if (!items.length) {
    container.innerHTML = "<p class=\"muted\">No recent activity.</p>";
    return;
  }

  items.forEach(item => {
    const createdAt = item.created_at ? formatInKolkata(item.created_at) : "";
    const status = (item.status || "").toLowerCase().replaceAll(" ", "_");
    const badge = item.type === "meeting" ? "Meeting" : "Proposal";
    const provider = item.provider ? item.provider.toUpperCase() : "";

    container.innerHTML += `
      <div class="activity-card">
        <div class="activity-header">
          <span class="badge">${badge}</span>
          ${provider ? `<span class="badge provider">${provider}</span>` : ""}
          <span class="status ${status}">${item.status || ""}</span>
        </div>
        <p class="activity-title">${item.title}</p>
        <p class="activity-date">${createdAt}</p>
        ${item.meet_link ? `<a class="link" href="${item.meet_link}" target="_blank">Open meeting link</a>` : ""}
      </div>
    `;
  });
}

function formatInKolkata(dateStr) {
  const normalized = /Z$|[+-]\d{2}:\d{2}$/.test(dateStr) ? dateStr : `${dateStr}Z`;
  const dt = new Date(normalized);
  return dt.toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
}

function updatePagination(total) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const pageInfo = document.getElementById("page-info");
  const prevBtn = document.getElementById("prev-page");
  const nextBtn = document.getElementById("next-page");
  const pageJump = document.getElementById("page-jump");

  if (pageInfo) pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
  if (prevBtn) prevBtn.disabled = currentPage <= 1;
  if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
  if (pageJump) {
    pageJump.max = totalPages;
    pageJump.value = currentPage;
  }
}

window.addEventListener("load", () => {
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) logoutBtn.addEventListener("click", logout);
  const prevBtn = document.getElementById("prev-page");
  const nextBtn = document.getElementById("next-page");
  const pageSizeEl = document.getElementById("page-size");
  const pageJumpEl = document.getElementById("page-jump");
  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      if (currentPage > 1) {
        currentPage -= 1;
        loadActivity();
      }
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      currentPage += 1;
      loadActivity();
    });
  }
  if (pageSizeEl) {
    pageSizeEl.addEventListener("change", () => {
      pageSize = parseInt(pageSizeEl.value, 10) || 10;
      currentPage = 1;
      loadActivity();
    });
  }
  if (pageJumpEl) {
    pageJumpEl.addEventListener("change", () => {
      const next = parseInt(pageJumpEl.value, 10);
      if (!Number.isNaN(next) && next >= 1) {
        currentPage = next;
        loadActivity();
      }
    });
  }
  loadActivity();
});
