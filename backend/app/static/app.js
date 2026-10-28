const statusEl = document.getElementById("health-status");

async function checkHealth() {
  try {
    const response = await fetch("/api/health");
    const body = await response.json();
    if (response.ok && body.status === "ok") {
      statusEl.textContent = "已連線";
      statusEl.className = "status ok";
      return;
    }
  } catch (error) {
    // 連線失敗或回應不是 JSON，一律視為無法連線。
  }
  statusEl.textContent = "無法連線";
  statusEl.className = "status error";
}

checkHealth();
