Auth.requireLogin();

let currentUrl = "/transactions/";
let accountsCache = [];
let categoriesCache = [];

function toApiPath(url) {
  const parsed = new URL(url, window.location.origin);
  let path = parsed.pathname + parsed.search;
  if (path.startsWith("/api/v1")) {
    path = path.slice("/api/v1".length);
  }
  return path;
}

function showError(message) {
  const box = document.getElementById("error-box");
  box.textContent = message;
  box.style.display = "block";
}

function hideError() {
  document.getElementById("error-box").style.display = "none";
}

async function loadDropdowns() {
  const [accounts, categories] = await Promise.all([
    apiJson("/accounts/"),
    apiJson("/categories/"),
  ]);
  accountsCache = accounts.results;
  categoriesCache = categories.results;

  const accountSelect = document.getElementById("account");
  const filterAccountSelect = document.getElementById("filter_account");
  for (const account of accountsCache) {
    accountSelect.innerHTML += `<option value="${account.id}">${account.name}</option>`;
    filterAccountSelect.innerHTML += `<option value="${account.id}">${account.name}</option>`;
  }

  const categorySelect = document.getElementById("category");
  refreshCategoryOptions();
  document.getElementById("transaction_type").addEventListener("change", refreshCategoryOptions);
}

function refreshCategoryOptions() {
  const type = document.getElementById("transaction_type").value;
  const categorySelect = document.getElementById("category");
  categorySelect.innerHTML = categoriesCache
    .filter((c) => c.category_type === type)
    .map((c) => `<option value="${c.id}">${c.name}${c.is_default ? "" : " (custom)"}</option>`)
    .join("");
}

async function loadTransactions(url) {
  const loading = document.getElementById("loading");
  const table = document.getElementById("transactions-table");
  const empty = document.getElementById("transactions-empty");
  loading.style.display = "block";
  table.style.display = "none";
  empty.style.display = "none";

  try {
    const data = await apiJson(toApiPath(url));
    loading.style.display = "none";
    currentUrl = url;

    document.getElementById("prev-btn").disabled = !data.previous;
    document.getElementById("next-btn").disabled = !data.next;

    if (data.results.length === 0) {
      empty.style.display = "block";
      return;
    }

    const tbody = document.getElementById("transactions-body");
    tbody.innerHTML = "";
    for (const t of data.results) {
      const amountClass = t.transaction_type === "INCOME" ? "amount-income" : "amount-expense";
      const sign = t.transaction_type === "INCOME" ? "+" : "-";
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${t.date}</td>
        <td>${t.description || "-"}</td>
        <td>${t.category_name}</td>
        <td>${t.account_name}</td>
        <td class="${amountClass}">${sign}₹${t.amount}</td>
        <td><button class="secondary" data-id="${t.id}">Delete</button></td>
      `;
      row.querySelector("button").addEventListener("click", () => deleteTransaction(t.id));
      tbody.appendChild(row);
    }
    table.style.display = "table";
  } catch (err) {
    loading.textContent = "Could not load transactions.";
  }
}

async function deleteTransaction(id) {
  if (!confirm("Delete this transaction?")) return;
  await apiFetch(`/transactions/${id}/`, { method: "DELETE" });
  loadTransactions(buildFilterUrl());
}

function buildFilterUrl() {
  const params = new URLSearchParams();
  const type = document.getElementById("filter_type").value;
  const account = document.getElementById("filter_account").value;
  const start = document.getElementById("filter_start").value;
  const end = document.getElementById("filter_end").value;
  if (type) params.set("transaction_type", type);
  if (account) params.set("account", account);
  if (start) params.set("start_date", start);
  if (end) params.set("end_date", end);
  const query = params.toString();
  return `/transactions/${query ? "?" + query : ""}`;
}

document.getElementById("filter-form").addEventListener("submit", (event) => {
  event.preventDefault();
  loadTransactions(buildFilterUrl());
});

document.getElementById("prev-btn").addEventListener("click", async () => {
  const data = await apiJson(toApiPath(currentUrl));
  if (data.previous) loadTransactions(data.previous);
});

document.getElementById("next-btn").addEventListener("click", async () => {
  const data = await apiJson(toApiPath(currentUrl));
  if (data.next) loadTransactions(data.next);
});

document.getElementById("transaction-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError();
  const submitBtn = document.getElementById("submit-btn");
  submitBtn.disabled = true;

  try {
    await apiJson("/transactions/", {
      method: "POST",
      body: JSON.stringify({
        account: document.getElementById("account").value,
        category: document.getElementById("category").value,
        amount: document.getElementById("amount").value,
        transaction_type: document.getElementById("transaction_type").value,
        date: document.getElementById("date").value,
        description: document.getElementById("description").value,
      }),
    });
    document.getElementById("transaction-form").reset();
    refreshCategoryOptions();
    loadTransactions(buildFilterUrl());
  } catch (err) {
    showError(formatErrors(err.data));
  } finally {
    submitBtn.disabled = false;
  }
});

(async function init() {
  await loadDropdowns();
  loadTransactions(currentUrl);
})();
