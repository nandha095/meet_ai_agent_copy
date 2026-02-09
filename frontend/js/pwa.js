function showUpdateToast(onClick) {
  const toast = document.getElementById("update-toast");
  const btn = document.getElementById("update-btn");
  if (toast) toast.style.display = "flex";
  if (btn) btn.onclick = onClick;
}

function initPwaUpdates() {
  if (!("serviceWorker" in navigator)) return;

  navigator.serviceWorker.register("/sw.js").then((reg) => {
    // If a worker is already waiting, show the toast immediately
    if (reg.waiting) {
      showUpdateToast(() => reg.waiting.postMessage({ type: "SKIP_WAITING" }));
    }

    reg.addEventListener("updatefound", () => {
      const newWorker = reg.installing;
      if (!newWorker) return;
      newWorker.addEventListener("statechange", () => {
        if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
          showUpdateToast(() => newWorker.postMessage({ type: "SKIP_WAITING" }));
        }
      });
    });
  });

  let refreshing = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (refreshing) return;
    refreshing = true;
    window.location.reload();
  });
}

document.addEventListener("DOMContentLoaded", initPwaUpdates);
