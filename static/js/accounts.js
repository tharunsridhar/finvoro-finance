Auth.requireLogin();

function showError(message) {
  const box = document.getElementById("error-box");
  box.textContent = message;
  box.style.display = "block";
}

function hideError() {
  document.getElementById("error-box").style.display = "none";
}

async function loadAccounts() {
  const loading = document.getElementById("loading");
  const table = document.getElementById("accounts-table");
  const empty = document.getElementById("accounts-empty");
  loading.style.display = "block";
  table.style.display = "none";
  empty.style.display = "none";

  try {
    const data = await apiJson("/accounts/");
    loading.style.display = "none";

    if (data.results.length === 0) {
      empty.style.display = "block";
      return;
    }

    const tbody = document.getElementById("accounts-body");
    tbody.innerHTML = "";
    for (const account of data.results) {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${account.name}</td>
        <td>${account.account_type}</td>
        <td>₹${account.initial_balance}</td>
        <td>₹${account.current_balance}</td>
        <td><button class="secondary" data-id="${account.id}">Delete</button></td>
      `;
      row.querySelector("button").addEventListener("click", () => deleteAccount(account.id));
      tbody.appendChild(row);
    }
    table.style.display = "table";
  } catch (err) {
    loading.textContent = "Could not load accounts.";
  }
}

async function deleteAccount(id) {
  if (!confirm("Delete this account? This will also delete its transactions.")) return;
  try {
    await apiFetch(`/accounts/${id}/`, { method: "DELETE" });
    loadAccounts();
  } catch (err) {
    showError("Could not delete account.");
  }
}

document.getElementById("account-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError();
  const submitBtn = document.getElementById("submit-btn");
  submitBtn.disabled = true;

  try {
    await apiJson("/accounts/", {
      method: "POST",
      body: JSON.stringify({
        name: document.getElementById("name").value,
        account_type: document.getElementById("account_type").value,
        initial_balance: document.getElementById("initial_balance").value || "0",
      }),
    });
    document.getElementById("account-form").reset();
    loadAccounts();
  } catch (err) {
    showError(formatErrors(err.data));
  } finally {
    submitBtn.disabled = false;
  }
});

loadAccounts();
