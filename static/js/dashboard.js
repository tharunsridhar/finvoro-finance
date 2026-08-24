Auth.requireLogin();

async function loadDashboard() {
  const now = new Date();
  const month = now.getMonth() + 1;
  const year = now.getFullYear();

  try {
    const [summary, budgets] = await Promise.all([
      apiJson(`/reports/summary/?month=${month}&year=${year}`),
      apiJson(`/budgets/?month=${month}&year=${year}`),
    ]);

    document.getElementById("stat-balance").textContent = `₹${summary.total_balance}`;
    document.getElementById("stat-income").textContent = `₹${summary.monthly_income}`;
    document.getElementById("stat-expenses").textContent = `₹${summary.monthly_expenses}`;

    const totalRemaining = budgets.results.reduce(
      (sum, b) => sum + parseFloat(b.remaining), 0
    );
    document.getElementById("stat-budget-remaining").textContent =
      budgets.results.length ? `₹${totalRemaining.toFixed(2)}` : "No budgets set";

    const tbody = document.getElementById("recent-body");
    tbody.innerHTML = "";
    if (summary.recent_transactions.length === 0) {
      document.getElementById("recent-empty").style.display = "block";
    } else {
      for (const t of summary.recent_transactions) {
        const row = document.createElement("tr");
        const amountClass = t.transaction_type === "INCOME" ? "amount-income" : "amount-expense";
        const sign = t.transaction_type === "INCOME" ? "+" : "-";
        row.innerHTML = `
          <td>${t.date}</td>
          <td>${t.description || "-"}</td>
          <td>${t.category}</td>
          <td>${t.account}</td>
          <td class="${amountClass}">${sign}₹${t.amount}</td>
        `;
        tbody.appendChild(row);
      }
    }

    document.getElementById("loading").style.display = "none";
    document.getElementById("dashboard-content").style.display = "block";
  } catch (err) {
    document.getElementById("loading").textContent = "Could not load dashboard data.";
  }
}

loadDashboard();
