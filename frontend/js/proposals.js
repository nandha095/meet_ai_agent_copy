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

async function loadProposals() {
  const token = localStorage.getItem("token");
  if (!token) return handleSessionExpired();

  const res = await fetch(
    `${BASE_URL}/emails/emails/paged?page=${currentPage}&size=${pageSize}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (res.status === 401) return handleSessionExpired();
  const data = await res.json();
  window._allProposals = data.items || [];
  window._totalProposals = data.total || 0;
  updatePagination();
  applyFilters();
}

function applyFilters() {
  const proposals = window._allProposals || [];
  const search = (document.getElementById("filter-search")?.value || "").toLowerCase().trim();
  const status = document.getElementById("filter-status")?.value || "";
  const provider = document.getElementById("filter-provider")?.value || "";
  const from = document.getElementById("filter-from")?.value;
  const to = document.getElementById("filter-to")?.value;

  const fromDate = from ? new Date(from + "T00:00:00") : null;
  const toDate = to ? new Date(to + "T23:59:59") : null;

  const filtered = proposals.filter(p => {
    const hay = `${p.client_email} ${p.subject}`.toLowerCase();
    if (search && !hay.includes(search)) return false;
    if (status && p.status.toLowerCase().replaceAll(" ", "_") !== status) return false;
    if (provider && (p.provider || "").toLowerCase() !== provider) return false;
    if (fromDate || toDate) {
      const created = p.created_at ? new Date(p.created_at) : null;
      if (!created) return false;
      if (fromDate && created < fromDate) return false;
      if (toDate && created > toDate) return false;
    }
    return true;
  });

  renderProposals(filtered);
}

function updatePagination() {
  const total = window._totalProposals || 0;
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

function renderProposals(proposals) {
  const container = document.getElementById("proposal-list");
  container.innerHTML = "";

  if (!proposals.length) {
    container.innerHTML = "<p class=\"muted\">No proposals sent yet.</p>";
    return;
  }

  proposals.forEach(p => {
    const cls = p.status.toLowerCase().replaceAll(" ", "_");
    const createdAt = p.created_at ? formatInKolkata(p.created_at) : "";
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

function formatInKolkata(dateStr) {
  const normalized = /Z$|[+-]\d{2}:\d{2}$/.test(dateStr) ? dateStr : `${dateStr}Z`;
  const dt = new Date(normalized);
  return dt.toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
}

function toggleProposalDetails(id) {
  const el = document.getElementById(`details-${id}`);
  el.style.display = el.style.display === "none" ? "block" : "none";
}

window.toggleProposalDetails = toggleProposalDetails;

window.addEventListener("load", () => {
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) logoutBtn.addEventListener("click", logout);
  const searchEl = document.getElementById("filter-search");
  const statusEl = document.getElementById("filter-status");
  const providerEl = document.getElementById("filter-provider");
  const fromEl = document.getElementById("filter-from");
  const toEl = document.getElementById("filter-to");
  const resetEl = document.getElementById("filter-reset");
  const exportEl = document.getElementById("export-csv");
  const pageSizeEl = document.getElementById("page-size");
  const pageJumpEl = document.getElementById("page-jump");

  if (searchEl) searchEl.addEventListener("input", applyFilters);
  if (statusEl) statusEl.addEventListener("change", applyFilters);
  if (providerEl) providerEl.addEventListener("change", applyFilters);
  if (fromEl) fromEl.addEventListener("change", applyFilters);
  if (toEl) toEl.addEventListener("change", applyFilters);
  if (resetEl) {
    resetEl.addEventListener("click", () => {
      if (searchEl) searchEl.value = "";
      if (statusEl) statusEl.value = "";
      if (providerEl) providerEl.value = "";
      if (fromEl) fromEl.value = "";
      if (toEl) toEl.value = "";
      applyFilters();
    });
  }
  if (exportEl) {
    exportEl.addEventListener("click", () => {
      const token = localStorage.getItem("token");
      if (!token) return handleSessionExpired();
      fetch(`${BASE_URL}/emails/emails/export`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => {
          if (res.status === 401) return handleSessionExpired();
          return res.blob();
        })
        .then(blob => {
          if (!blob) return;
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "proposals.csv";
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
        });
    });
  }
  if (pageSizeEl) {
    pageSizeEl.addEventListener("change", () => {
      pageSize = parseInt(pageSizeEl.value, 10) || 10;
      currentPage = 1;
      loadProposals();
    });
  }
  if (pageJumpEl) {
    pageJumpEl.addEventListener("change", () => {
      const next = parseInt(pageJumpEl.value, 10);
      if (!Number.isNaN(next) && next >= 1) {
        currentPage = next;
        loadProposals();
      }
    });
  }
  const prevBtn = document.getElementById("prev-page");
  const nextBtn = document.getElementById("next-page");
  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      if (currentPage > 1) {
        currentPage -= 1;
        loadProposals();
      }
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      currentPage += 1;
      loadProposals();
    });
  }
  loadProposals();
});
