Auth.requireLogin();

function showError(message) {
  const box = document.getElementById("error-box");
  box.textContent = message;
  box.style.display = "block";
}

function hideError() {
  document.getElementById("error-box").style.display = "none";
}

async function loadCategoryOptions() {
  const data = await apiJson("/categories/?category_type=EXPENSE");
  const select = document.getElementById("category");
  select.innerHTML = data.results
    .map((c) => `<option value="${c.id}">${c.name}${c.is_default ? "" : " (custom)"}</option>`)
    .join("");
}

async function loadBudgets() {
  const loading = document.getElementById("loading");
  const table = document.getElementById("budgets-table");
  const empty = document.getElementById("budgets-empty");
  loading.style.display = "block";
  table.style.display = "none";
  empty.style.display = "none";

  try {
    const data = await apiJson("/budgets/");
    loading.style.display = "none";

    if (data.results.length === 0) {
      empty.style.display = "block";
      return;
    }

    const tbody = document.getElementById("budgets-body");
    tbody.innerHTML = "";
    for (const b of data.results) {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${b.category_name}</td>
        <td>${b.month}/${b.year}</td>
        <td>₹${b.amount}</td>
        <td>₹${b.spent}</td>
        <td>₹${b.remaining}</td>
        <td>${b.percentage_used}%</td>
        <td><button class="secondary" data-id="${b.id}">Delete</button></td>
      `;
      row.querySelector("button").addEventListener("click", () => deleteBudget(b.id));
      tbody.appendChild(row);
    }
    table.style.display = "table";
  } catch (err) {
    loading.textContent = "Could not load budgets.";
  }
}

async function deleteBudget(id) {
  if (!confirm("Delete this budget?")) return;
  await apiFetch(`/budgets/${id}/`, { method: "DELETE" });
  loadBudgets();
}

document.getElementById("budget-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError();
  const submitBtn = document.getElementById("submit-btn");
  submitBtn.disabled = true;

  try {
    await apiJson("/budgets/", {
      method: "POST",
      body: JSON.stringify({
        category: document.getElementById("category").value,
        amount: document.getElementById("amount").value,
        month: document.getElementById("month").value,
        year: document.getElementById("year").value,
      }),
    });
    document.getElementById("budget-form").reset();
    loadBudgets();
  } catch (err) {
    showError(formatErrors(err.data));
  } finally {
    submitBtn.disabled = false;
  }
});

(async function init() {
  const now = new Date();
  document.getElementById("month").value = now.getMonth() + 1;
  document.getElementById("year").value = now.getFullYear();
  await loadCategoryOptions();
  loadBudgets();
})();
