// 代碼轉中文的對照表只在這裡定義（SDS UI-01）。
const LABELS = {
  leave_type: { annual: "特休", personal: "事假", sick: "病假" },
  period: { full_day: "整天", am: "上午", pm: "下午" },
  status: { pending: "待審核" },
};

const READ_FAILED_MESSAGE = "系統暫時無法讀取資料，請稍後再試";
const SELECT_EMPLOYEE_HINT = "請先選擇員工";

const statusEl = document.getElementById("health-status");
const employeeSelect = document.getElementById("employee-select");
const employeeError = document.getElementById("employee-error");
const submitButton = document.getElementById("submit-button");
const submitHint = document.getElementById("submit-hint");
const leavesMessage = document.getElementById("leaves-message");
const leavesList = document.getElementById("leaves-list");

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

function labelOf(group, code) {
  return LABELS[group][code] ?? code;
}

function formatDateRange(start, end) {
  return start === end ? start : `${start} ～ ${end}`;
}

function firstErrorMessage(body, fallback) {
  return body?.errors?.[0]?.message ?? fallback;
}

function showEmployeeError(message) {
  employeeError.textContent = message;
  employeeError.hidden = false;
}

function selectedEmployeeId() {
  return employeeSelect.value;
}

// 未選員工時停用送出；送出中的停用由送出流程（U2）處理。
function updateSubmitAvailability() {
  const hasEmployee = selectedEmployeeId() !== "";
  submitButton.disabled = !hasEmployee;
  submitHint.hidden = hasEmployee;
}

async function loadEmployees() {
  try {
    const response = await fetch("/api/employees");
    const body = await response.json();
    if (!response.ok) {
      showEmployeeError(firstErrorMessage(body, READ_FAILED_MESSAGE));
      return;
    }
    for (const employee of body.employees) {
      const option = document.createElement("option");
      option.value = employee.id;
      option.textContent = employee.name;
      employeeSelect.append(option);
    }
  } catch (error) {
    showEmployeeError(READ_FAILED_MESSAGE);
  }
}

function renderLeave(leave) {
  const item = document.createElement("li");
  item.className = "leave";

  const summary = document.createElement("p");
  summary.textContent = [
    labelOf("leave_type", leave.leave_type),
    formatDateRange(leave.start_date, leave.end_date),
    labelOf("period", leave.period),
    `${leave.days} 天`,
    labelOf("status", leave.status),
  ].join("｜");
  item.append(summary);

  // 理由空白時顯示「--」，不省略這一行（SDS v0.2 UI-01）。
  const reason = document.createElement("p");
  reason.className = "reason";
  reason.textContent = `理由：${leave.reason || "--"}`;
  item.append(reason);
  return item;
}

function showLeavesMessage(message) {
  leavesList.replaceChildren();
  leavesMessage.textContent = message;
  leavesMessage.hidden = false;
}

// 選員工、送出成功與送出失敗後都呼叫這裡重新讀取列表（SDS UI-01）。
async function loadLeaves() {
  const employeeId = selectedEmployeeId();
  if (employeeId === "") {
    showLeavesMessage(SELECT_EMPLOYEE_HINT);
    return;
  }
  try {
    const response = await fetch(`/api/employees/${encodeURIComponent(employeeId)}/leaves`);
    const body = await response.json();
    if (employeeId !== selectedEmployeeId()) {
      return; // 回應回來前已改選其他員工，丟棄舊結果。
    }
    if (!response.ok) {
      showLeavesMessage(firstErrorMessage(body, READ_FAILED_MESSAGE));
      return;
    }
    if (body.leaves.length === 0) {
      showLeavesMessage("目前沒有假單");
      return;
    }
    leavesMessage.hidden = true;
    leavesList.replaceChildren(...body.leaves.map(renderLeave));
  } catch (error) {
    if (employeeId === selectedEmployeeId()) {
      showLeavesMessage(READ_FAILED_MESSAGE);
    }
  }
}

employeeSelect.addEventListener("change", () => {
  updateSubmitAvailability();
  loadLeaves();
});

// ---- 送出流程（U2）：送出中停用、成功、驗證失敗、伺服器或網路失敗（SDS UI-01）----

const SUBMIT_LABEL = "送出";
const SUBMITTING_LABEL = "送出中…";
const SUBMIT_FAILED_MESSAGE = "系統暫時無法處理，資料沒有存檔，請稍後再試";
const FORM_FIELDS = ["leave_type", "start_date", "end_date", "period", "reason"];

const leaveForm = document.getElementById("leave-form");
const formMessage = document.getElementById("form-message");

let submitting = false;

function setFormMessage(message, isError) {
  formMessage.textContent = message;
  formMessage.className = isError ? "message error" : "message";
}

function clearFormErrors() {
  setFormMessage("", false);
  for (const el of leaveForm.querySelectorAll(".field-error")) {
    el.textContent = "";
  }
}

// 有 field 的錯誤放在對應欄位旁；field 為 null 或畫面上沒有該欄位的，放在表單頂端。
function showErrors(errors) {
  const topMessages = [];
  const fieldMessages = new Map();
  for (const error of errors) {
    const target = error.field
      ? leaveForm.querySelector(`.field-error[data-field="${CSS.escape(error.field)}"]`)
      : null;
    if (target) {
      fieldMessages.set(target, [...(fieldMessages.get(target) ?? []), error.message]);
    } else {
      topMessages.push(error.message);
    }
  }
  for (const [target, messages] of fieldMessages) {
    target.textContent = messages.join("；");
  }
  setFormMessage(topMessages.join("；"), true);
}

function readLeavePayload() {
  // 一律送出 6 個欄位，永遠不送 status、days（SDS API-03）。
  const payload = { employee_id: selectedEmployeeId() };
  for (const name of FORM_FIELDS) {
    payload[name] = leaveForm.elements[name].value;
  }
  return payload;
}

function resetLeaveFields() {
  // 保留所選員工，只清空表單欄位（Q-5）。
  for (const name of FORM_FIELDS) {
    leaveForm.elements[name].value = "";
  }
}

function setSubmitting(value) {
  submitting = value;
  submitButton.textContent = value ? SUBMITTING_LABEL : SUBMIT_LABEL;
  if (value) {
    submitButton.disabled = true;
  } else {
    updateSubmitAvailability();
  }
}

async function submitLeave(event) {
  event.preventDefault();
  if (submitting || selectedEmployeeId() === "") {
    return; // 收到回應前不再發出請求（FR-10）。
  }
  setSubmitting(true);
  clearFormErrors();
  try {
    const response = await fetch("/api/leaves", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(readLeavePayload()),
    });
    const body = await response.json().catch(() => null);
    if (response.status === 201 && body?.leave) {
      const leave = body.leave;
      setFormMessage(
        `已送出：${formatDateRange(leave.start_date, leave.end_date)}，共 ${leave.days} 天，${labelOf("status", leave.status)}`,
        false,
      );
      resetLeaveFields();
    } else if ((response.status === 400 || response.status === 422) && body?.errors) {
      showErrors(body.errors);
    } else {
      setFormMessage(SUBMIT_FAILED_MESSAGE, true);
    }
  } catch (error) {
    setFormMessage(SUBMIT_FAILED_MESSAGE, true);
  } finally {
    setSubmitting(false);
    loadLeaves(); // 成功或失敗都重新讀取，讓員工看見實際存檔結果。
  }
}

leaveForm.addEventListener("submit", submitLeave);

checkHealth();
updateSubmitAvailability();
loadEmployees();
