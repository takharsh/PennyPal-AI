// Global Currency Symbol
let userCurrency = '₹';
let chartIncomeVsExpense = null;
let chartCategoryDoughnut = null;

// Toast Notification Helper
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast-item';
  
  let icon = 'fa-circle-info';
  if (type === 'success') icon = 'fa-circle-check';
  if (type === 'error') icon = 'fa-circle-exclamation';

  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 200);
  }, 3500);
}

// Modal Helpers
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.style.display = 'flex';
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.style.display = 'none';
}

// View Navigation Switching
function switchNavView(viewName) {
  // Update sidebar active state
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    if (item.getAttribute('data-view') === viewName) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Toggle main sections
  document.querySelectorAll('.view-section').forEach(sec => {
    if (sec.id === `view-${viewName}`) {
      sec.classList.add('active');
    } else {
      sec.classList.remove('active');
    }
  });

  // Close mobile sidebar drawer if open
  document.getElementById('sidebar').classList.remove('show');

  // Trigger view-specific data refresh
  if (viewName === 'dashboard') loadDashboardData();
  if (viewName === 'expenses') loadTransactions();
  if (viewName === 'spending') loadAISpendingAnalysis();
  if (viewName === 'health') loadFinancialHealthPage();
  if (viewName === 'budget') loadBudgetRecommendations();
  if (viewName === 'goals') loadSavingsGoals();
  if (viewName === 'settings') loadSettingsData();
}

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
  // Bind Nav Clicks
  document.querySelectorAll('.sidebar-nav .nav-item[data-view]').forEach(item => {
    item.addEventListener('click', () => {
      const view = item.getAttribute('data-view');
      switchNavView(view);
    });
  });

  // Mobile sidebar toggle
  const mobileToggle = document.getElementById('sidebar-toggle');
  if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
      document.getElementById('sidebar').classList.toggle('show');
    });
  }

  // Logout Buttons
  const logoutAction = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      showToast('Logged out successfully.', 'info');
      setTimeout(() => window.location.href = '/login', 400);
    } catch (e) {
      window.location.href = '/login';
    }
  };

  const logoutLink = document.getElementById('logout-link');
  if (logoutLink) logoutLink.addEventListener('click', logoutAction);
  const topLogoutBtn = document.getElementById('top-logout-btn');
  if (topLogoutBtn) topLogoutBtn.addEventListener('click', logoutAction);

  // Quick Add Transaction Buttons
  const quickAddBtn = document.getElementById('quick-add-tx-btn');
  if (quickAddBtn) quickAddBtn.addEventListener('click', () => {
    document.getElementById('tx-edit-id').value = '';
    document.getElementById('tx-modal-title').innerText = 'Add Transaction';
    document.getElementById('form-add-tx').reset();
    document.getElementById('tx-date').value = new Date().toISOString().split('T')[0];
    openModal('modal-add-tx');
  });

  const openAddTxBtn = document.getElementById('open-add-tx-modal');
  if (openAddTxBtn) openAddTxBtn.addEventListener('click', () => {
    document.getElementById('tx-edit-id').value = '';
    document.getElementById('tx-modal-title').innerText = 'Add Transaction';
    document.getElementById('form-add-tx').reset();
    document.getElementById('tx-date').value = new Date().toISOString().split('T')[0];
    openModal('modal-add-tx');
  });

  // Transaction Form Submit
  const formAddTx = document.getElementById('form-add-tx');
  if (formAddTx) {
    formAddTx.addEventListener('submit', async (e) => {
      e.preventDefault();
      const editId = document.getElementById('tx-edit-id').value;
      const type = document.getElementById('tx-type').value;
      const title = document.getElementById('tx-title').value.trim();
      const amount = parseFloat(document.getElementById('tx-amount').value);
      const category = document.getElementById('tx-category').value;
      const transaction_date = document.getElementById('tx-date').value;
      const description = document.getElementById('tx-desc').value.trim();

      const endpoint = editId ? `/api/transactions/${editId}` : '/api/transactions';
      const method = editId ? 'PUT' : 'POST';

      try {
        const res = await fetch(endpoint, {
          method: method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type, title, amount, category, transaction_date, description })
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, 'success');
          closeModal('modal-add-tx');
          loadDashboardData();
          loadTransactions();
        } else {
          showToast(data.message || 'Failed to save transaction.', 'error');
        }
      } catch (err) {
        showToast('Network error saving transaction.', 'error');
      }
    });
  }

  // Transaction Table Filter Event Listeners
  ['tx-filter-search', 'tx-filter-category', 'tx-filter-type', 'tx-filter-sort'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', loadTransactions);
      el.addEventListener('change', loadTransactions);
    }
  });

  // Global Search listener
  const globalSearch = document.getElementById('global-search');
  if (globalSearch) {
    globalSearch.addEventListener('input', (e) => {
      const q = e.target.value.trim();
      if (q.length > 0) {
        switchNavView('expenses');
        document.getElementById('tx-filter-search').value = q;
        loadTransactions();
      }
    });
  }

  // Create Goal Modal
  const openCreateGoalBtn = document.getElementById('open-create-goal-modal');
  if (openCreateGoalBtn) {
    openCreateGoalBtn.addEventListener('click', () => {
      document.getElementById('form-create-goal').reset();
      openModal('modal-create-goal');
    });
  }

  const formCreateGoal = document.getElementById('form-create-goal');
  if (formCreateGoal) {
    formCreateGoal.addEventListener('submit', async (e) => {
      e.preventDefault();
      const goal_name = document.getElementById('goal-name').value.trim();
      const target_amount = parseFloat(document.getElementById('goal-target').value);
      const current_amount = parseFloat(document.getElementById('goal-current').value || 0);
      const target_date = document.getElementById('goal-date').value;

      try {
        const res = await fetch('/api/goals', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ goal_name, target_amount, current_amount, target_date })
        });
        const data = await res.json();
        if (data.success) {
          showToast('Savings goal created!', 'success');
          closeModal('modal-create-goal');
          loadSavingsGoals();
        } else {
          showToast(data.message, 'error');
        }
      } catch (err) {
        showToast('Error creating goal.', 'error');
      }
    });
  }

  // Add Funds Form Submit
  const formAddFunds = document.getElementById('form-add-funds');
  if (formAddFunds) {
    formAddFunds.addEventListener('submit', async (e) => {
      e.preventDefault();
      const goalId = document.getElementById('add-funds-goal-id').value;
      const amount = parseFloat(document.getElementById('add-funds-amount').value);

      try {
        const res = await fetch(`/api/goals/${goalId}/add-funds`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ amount })
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, 'success');
          closeModal('modal-add-funds');
          loadSavingsGoals();
          loadDashboardData();
        } else {
          showToast(data.message, 'error');
        }
      } catch (err) {
        showToast('Error adding funds.', 'error');
      }
    });
  }

  // Accept All Budget Recommendations Button
  const acceptBudgetsBtn = document.getElementById('accept-all-budgets-btn');
  if (acceptBudgetsBtn) {
    acceptBudgetsBtn.addEventListener('click', async () => {
      try {
        const res = await fetch('/api/budget/accept-recommendations', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, 'success');
          loadBudgetRecommendations();
        }
      } catch (err) {
        showToast('Failed to apply recommended budgets.', 'error');
      }
    });
  }

  // Investment Guidance Form Submit
  const invForm = document.getElementById('investment-form');
  if (invForm) {
    invForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const available_amount = parseFloat(document.getElementById('inv-amount').value);
      const risk_level = document.getElementById('inv-risk').value;
      const investment_horizon = document.getElementById('inv-horizon').value;

      const submitBtn = document.getElementById('inv-submit-btn');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i> Generating AI Suggestions...';

      try {
        const res = await fetch('/api/investments/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ available_amount, risk_level, investment_horizon })
        });
        const data = await res.json();

        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles me-1"></i> Generate Guidance';

        if (data.success) {
          document.getElementById('investment-results-area').style.display = 'block';

          // Render Allocation Cards
          const grid = document.getElementById('inv-allocations-grid');
          grid.innerHTML = data.allocations.map(a => `
            <div style="background: #FFFFFF; padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 0.95rem; color: var(--text-main);">${a.category}</span>
                <span class="badge-custom" style="background: var(--primary-light); color: var(--primary); font-size: 0.85rem;">${a.percentage}%</span>
              </div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 6px;">Risk: ${a.risk} • Horizon: ${a.horizon}</div>
              <p style="font-size: 0.85rem; color: var(--text-main); line-height: 1.4;">${a.reason}</p>
            </div>
          `).join('');

          document.getElementById('inv-ai-text').innerText = data.ai_guidance;
          document.getElementById('inv-disclaimer').innerText = data.disclaimer;
          showToast('Investment guidance generated!', 'success');
        } else {
          showToast(data.message, 'error');
        }
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles me-1"></i> Generate Guidance';
        showToast('Error generating investment suggestions.', 'error');
      }
    });
  }

  // Settings Forms
  const settingsProfileForm = document.getElementById('settings-profile-form');
  if (settingsProfileForm) {
    settingsProfileForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('setting-name').value.trim();
      const currency = document.getElementById('setting-currency').value;
      const monthly_income = parseFloat(document.getElementById('setting-income').value || 0);
      const emergency_fund = parseFloat(document.getElementById('setting-emergency').value || 0);
      const risk_tolerance = document.getElementById('setting-risk').value;

      try {
        const res = await fetch('/api/settings/profile', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, currency, monthly_income, emergency_fund, risk_tolerance })
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, 'success');
          userCurrency = currency;
          loadUserProfile();
          loadDashboardData();
        } else {
          showToast(data.message, 'error');
        }
      } catch (err) {
        showToast('Error updating profile settings.', 'error');
      }
    });
  }

  const settingsPwdForm = document.getElementById('settings-password-form');
  if (settingsPwdForm) {
    settingsPwdForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const old_password = document.getElementById('setting-old-pwd').value;
      const new_password = document.getElementById('setting-new-pwd').value;

      try {
        const res = await fetch('/api/settings/change-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ old_password, new_password })
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message, 'success');
          settingsPwdForm.reset();
        } else {
          showToast(data.message, 'error');
        }
      } catch (err) {
        showToast('Error updating password.', 'error');
      }
    });
  }

  // Initial Data Load
  loadUserProfile();
  loadDashboardData();
});

// Load Current User Profile
async function loadUserProfile() {
  try {
    const res = await fetch('/api/auth/me');
    const data = await res.json();
    if (data.success) {
      const user = data.user;
      userCurrency = user.currency || '₹';
      document.getElementById('user-name-display').innerText = user.name;
      document.getElementById('user-email-display').innerText = user.email;
      document.getElementById('user-avatar').innerText = user.name.charAt(0).toUpperCase();

      // Pre-fill settings form
      if (document.getElementById('setting-name')) {
        document.getElementById('setting-name').value = user.name;
        document.getElementById('setting-currency').value = userCurrency;
        document.getElementById('setting-income').value = user.profile.monthly_income || '';
        document.getElementById('setting-emergency').value = user.profile.emergency_fund || '';
        document.getElementById('setting-risk').value = user.profile.risk_tolerance || 'Moderate';
      }
    } else {
      window.location.href = '/login';
    }
  } catch (e) {
    console.error("Auth check notice:", e);
  }
}

// Load Dashboard Metrics, Health Gauge & Charts
async function loadDashboardData() {
  try {
    const res = await fetch('/api/dashboard');
    const data = await res.json();
    if (data.success) {
      const m = data.metrics;
      document.getElementById('metric-balance').innerText = `${userCurrency}${m.total_balance.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
      document.getElementById('metric-income').innerText = `${userCurrency}${m.monthly_income.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
      document.getElementById('metric-expenses').innerText = `${userCurrency}${m.monthly_expenses.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
      document.getElementById('metric-savings').innerText = `${userCurrency}${m.monthly_savings.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;

      // Health Score Gauge Widget
      const score = data.health_score;
      document.getElementById('dashboard-gauge-score').innerText = score;
      document.getElementById('dashboard-gauge-circle').style.setProperty('--score-pct', score);
      document.getElementById('dashboard-health-rating').innerText = data.health_rating;
      document.getElementById('dashboard-health-desc').innerText = `Financial Health Score: ${score}/100 (${data.health_rating}).`;

      // Smart Alerts
      const alertsContainer = document.getElementById('smart-alerts-list');
      alertsContainer.innerHTML = data.alerts.map(a => `
        <div style="padding: 10px 14px; background: ${a.type === 'danger' ? 'var(--red-light)' : a.type === 'warning' ? 'var(--orange-light)' : 'var(--green-light)'}; border-radius: var(--radius-sm); border-left: 4px solid ${a.type === 'danger' ? 'var(--red)' : a.type === 'warning' ? 'var(--orange)' : 'var(--green)'};">
          <div style="font-weight: 600; font-size: 0.85rem; color: var(--text-main);"><i class="fa-solid fa-${a.icon} me-1"></i> ${a.title}</div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">${a.message}</div>
        </div>
      `).join('');

      // Recent Transactions Table
      const recentTbody = document.getElementById('dashboard-recent-tx-tbody');
      if (data.recent_transactions.length === 0) {
        recentTbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No transactions logged yet. Add your first expense to begin!</td></tr>`;
      } else {
        recentTbody.innerHTML = data.recent_transactions.map(t => `
          <tr>
            <td>${t.transaction_date}</td>
            <td><strong>${t.title}</strong></td>
            <td><span class="badge-custom badge-category">${t.category}</span></td>
            <td><span class="badge-custom ${t.type === 'income' ? 'badge-income' : 'badge-expense'}">${t.type.toUpperCase()}</span></td>
            <td style="font-weight: 600; color: ${t.type === 'income' ? 'var(--green)' : 'var(--red)'};">
              ${t.type === 'income' ? '+' : '-'}${userCurrency}${t.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}
            </td>
          </tr>
        `).join('');
      }

      // Render Charts
      loadAnalyticsCharts();
    }
  } catch (err) {
    console.error("Dashboard data load error:", err);
  }
}

// Render Chart.js Analytics
async function loadAnalyticsCharts() {
  try {
    const res = await fetch('/api/analytics');
    const data = await res.json();
    if (!data.success) return;

    const charts = data.charts;

    // 1. Income vs Expense Trend Line Chart
    const ctxTrend = document.getElementById('chart-income-vs-expense');
    if (ctxTrend) {
      if (chartIncomeVsExpense) chartIncomeVsExpense.destroy();
      chartIncomeVsExpense = new Chart(ctxTrend, {
        type: 'bar',
        data: {
          labels: charts.income_vs_expense.labels,
          datasets: [
            { label: 'Income', data: charts.income_vs_expense.income, backgroundColor: '#10B981', borderRadius: 4 },
            { label: 'Expenses', data: charts.income_vs_expense.expense, backgroundColor: '#EF4444', borderRadius: 4 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } },
          scales: { y: { beginAtZero: true } }
        }
      });
    }

    // 2. Category Breakdown Doughnut Chart
    const ctxDoughnut = document.getElementById('chart-category-doughnut');
    if (ctxDoughnut) {
      if (chartCategoryDoughnut) chartCategoryDoughnut.destroy();
      chartCategoryDoughnut = new Chart(ctxDoughnut, {
        type: 'doughnut',
        data: {
          labels: charts.category_doughnut.labels,
          datasets: [{
            data: charts.category_doughnut.series,
            backgroundColor: ['#635BFF', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#64748B']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'right' } }
        }
      });
    }
  } catch (e) {
    console.error("Chart load notice:", e);
  }
}

// Load Full Transactions Table
async function loadTransactions() {
  const search = document.getElementById('tx-filter-search') ? document.getElementById('tx-filter-search').value.trim() : '';
  const category = document.getElementById('tx-filter-category') ? document.getElementById('tx-filter-category').value : 'All';
  const type = document.getElementById('tx-filter-type') ? document.getElementById('tx-filter-type').value : 'All';
  const sort = document.getElementById('tx-filter-sort') ? document.getElementById('tx-filter-sort').value : 'date_desc';

  const params = new URLSearchParams({ search, category, type, sort });

  try {
    const res = await fetch(`/api/transactions?${params.toString()}`);
    const data = await res.json();
    const tbody = document.getElementById('full-tx-tbody');

    if (!data.success || data.transactions.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 24px;">No matching transactions found. Add a transaction or clear filters.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.transactions.map(t => `
      <tr>
        <td>${t.transaction_date}</td>
        <td>
          <strong>${t.title}</strong>
          ${t.description ? `<div style="font-size: 0.775rem; color: var(--text-muted);">${t.description}</div>` : ''}
        </td>
        <td><span class="badge-custom badge-category">${t.category}</span></td>
        <td><span class="badge-custom ${t.type === 'income' ? 'badge-income' : 'badge-expense'}">${t.type.toUpperCase()}</span></td>
        <td style="font-weight: 600; color: ${t.type === 'income' ? 'var(--green)' : 'var(--red)'};">
          ${t.type === 'income' ? '+' : '-'}${userCurrency}${t.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}
        </td>
        <td>
          <button style="background: none; border: none; color: var(--primary); cursor: pointer; margin-right: 8px;" onclick="editTransaction(${t.id}, '${t.type}', '${t.title.replace(/'/g, "\\'")}', ${t.amount}, '${t.category}', '${t.transaction_date}', '${(t.description||'').replace(/'/g, "\\'")}')" title="Edit">
            <i class="fa-solid fa-pen-to-square"></i>
          </button>
          <button style="background: none; border: none; color: var(--red); cursor: pointer;" onclick="deleteTransaction(${t.id})" title="Delete">
            <i class="fa-solid fa-trash"></i>
          </button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error("Transactions load error:", err);
  }
}

// Edit Transaction Trigger
function editTransaction(id, type, title, amount, category, date, desc) {
  document.getElementById('tx-edit-id').value = id;
  document.getElementById('tx-modal-title').innerText = 'Edit Transaction';
  document.getElementById('tx-type').value = type;
  document.getElementById('tx-title').value = title;
  document.getElementById('tx-amount').value = amount;
  document.getElementById('tx-category').value = category;
  document.getElementById('tx-date').value = date;
  document.getElementById('tx-desc').value = desc;
  openModal('modal-add-tx');
}

// Delete Transaction Trigger
async function deleteTransaction(id) {
  if (!confirm('Are you sure you want to delete this transaction?')) return;

  try {
    const res = await fetch(`/api/transactions/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast('Transaction deleted.', 'info');
      loadTransactions();
      loadDashboardData();
    } else {
      showToast(data.message, 'error');
    }
  } catch (e) {
    showToast('Failed to delete transaction.', 'error');
  }
}

// Load AI Spending Analysis
async function loadAISpendingAnalysis() {
  const container = document.getElementById('spending-ai-narrative');
  container.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i> Gemini API is analyzing your financial records...';

  try {
    const res = await fetch('/api/ai/spending-analysis', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      container.innerText = data.ai_insights;
      document.getElementById('ai-top-cat').innerText = data.metrics.top_category;
      document.getElementById('ai-sub-total').innerText = `${userCurrency}${data.metrics.subscription_total.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
      document.getElementById('ai-mom-shift').innerText = `${data.metrics.mom_change_pct}%`;

      const obsList = document.getElementById('ai-key-observations-list');
      obsList.innerHTML = data.key_observations.map(o => `
        <div style="padding: 12px 16px; background: var(--bg-app); border-radius: var(--radius-sm); border-left: 3px solid var(--primary); font-size: 0.9rem;">
          <i class="fa-solid fa-arrow-right-long me-2" style="color: var(--primary);"></i> ${o}
        </div>
      `).join('');
    }
  } catch (err) {
    container.innerText = 'Unable to connect to AI Spending Analysis API.';
  }
}

// Load Financial Health Score Page
async function loadFinancialHealthPage() {
  try {
    const res = await fetch('/api/financial-health');
    const data = await res.json();
    if (data.success) {
      const h = data.health;
      document.getElementById('full-gauge-score').innerText = h.score;
      document.getElementById('full-gauge-circle').style.setProperty('--score-pct', h.score);
      document.getElementById('full-health-rating').innerText = `Rating: ${h.rating}`;
      document.getElementById('full-health-ai-narrative').innerText = h.ai_explanation;

      // Breakdown bars
      const b = h.breakdown;
      document.getElementById('score-savings-val').innerText = `${b.savings_rate_score} / 30`;
      document.getElementById('score-savings-bar').style.width = `${(b.savings_rate_score / 30 * 100)}%`;

      document.getElementById('score-budget-val').innerText = `${b.budget_control_score} / 20`;
      document.getElementById('score-budget-bar').style.width = `${(b.budget_control_score / 20 * 100)}%`;

      document.getElementById('score-expense-val').innerText = `${b.expense_ratio_score} / 20`;
      document.getElementById('score-expense-bar').style.width = `${(b.expense_ratio_score / 20 * 100)}%`;

      document.getElementById('score-emergency-val').innerText = `${b.emergency_fund_score} / 15`;
      document.getElementById('score-emergency-bar').style.width = `${(b.emergency_fund_score / 15 * 100)}%`;

      // Positives & Improvements
      const posUl = document.getElementById('health-positives-ul');
      posUl.innerHTML = h.positives.map(p => `<li style="margin-bottom: 6px;">${p}</li>`).join('');

      const impUl = document.getElementById('health-improvements-ul');
      impUl.innerHTML = h.improvements.map(i => `<li style="margin-bottom: 6px;">${i}</li>`).join('');
    }
  } catch (err) {
    console.error("Health score load error:", err);
  }
}

// Load AI Budget Recommendations
async function loadBudgetRecommendations() {
  try {
    const res = await fetch('/api/budget/recommendations');
    const data = await res.json();
    if (data.success) {
      const recs = data.data.categories;
      const tbody = document.getElementById('budget-rec-tbody');

      tbody.innerHTML = recs.map(r => `
        <tr>
          <td><strong>${r.category}</strong></td>
          <td>${userCurrency}${r.actual.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
          <td style="font-weight: 600; color: var(--primary);">${userCurrency}${r.recommended.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
          <td style="color: ${r.difference > 0 ? 'var(--red)' : 'var(--green)'};">
            ${r.difference > 0 ? '+' : ''}${userCurrency}${r.difference.toLocaleString('en-IN', {minimumFractionDigits: 2})}
          </td>
          <td>
            <span class="badge-custom ${r.status === 'Over Budget' ? 'badge-expense' : 'badge-income'}">${r.status}</span>
          </td>
          <td>
            <button style="background: var(--primary-light); color: var(--primary); border: none; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; cursor: pointer;" onclick="saveCustomBudget('${r.category}', ${r.recommended})">
              Apply Limit
            </button>
          </td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error("Budget recommendation error:", err);
  }
}

// Save Custom Category Budget
async function saveCustomBudget(category, limit) {
  try {
    const res = await fetch('/api/budget', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category, monthly_limit: limit })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      loadBudgetRecommendations();
    }
  } catch (e) {
    showToast('Failed to update budget limit.', 'error');
  }
}

// Load Savings Goals
async function loadSavingsGoals() {
  try {
    const res = await fetch('/api/goals');
    const data = await res.json();
    if (data.success) {
      const container = document.getElementById('goals-grid-container');
      if (data.goals.length === 0) {
        container.innerHTML = `<div class="panel-card" style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 36px;">You don't have a savings goal yet. Click 'Create Savings Goal' to start tracking your progress!</div>`;
        return;
      }

      container.innerHTML = data.goals.map(g => `
        <div class="panel-card" style="margin-bottom: 0;">
          <div class="panel-header">
            <div class="panel-title">${g.goal_name}</div>
            <span class="badge-custom ${g.is_completed ? 'badge-income' : 'badge-category'}">${g.is_completed ? 'Completed 🎉' : 'In Progress'}</span>
          </div>

          <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-main); margin-bottom: 4px;">
            ${userCurrency}${g.current_amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}
            <span style="font-size: 0.9rem; font-weight: 500; color: var(--text-muted);">/ ${userCurrency}${g.target_amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
          </div>

          <div style="font-size: 0.825rem; color: var(--text-muted); margin-bottom: 12px;">
            Target Date: ${g.target_date} (${g.months_left} months remaining)
          </div>

          <div class="progress-bar-container" style="margin-bottom: 12px; height: 10px;">
            <div class="progress-bar-fill" style="width: ${g.progress_percentage}%; background-color: ${g.is_completed ? 'var(--green)' : 'var(--primary)'};"></div>
          </div>

          <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 16px;">
            Required saving: <strong>${userCurrency}${g.monthly_required.toLocaleString('en-IN', {minimumFractionDigits: 2})}/month</strong>
          </div>

          <div style="display: flex; gap: 8px;">
            <button class="btn-primary-custom" style="padding: 6px 12px; font-size: 0.825rem;" onclick="triggerAddFunds(${g.id})">
              + Add Funds
            </button>
            <button class="btn-demo-custom" style="margin-top: 0; padding: 6px 12px; font-size: 0.825rem; color: var(--red); border-color: rgba(239,68,68,0.2);" onclick="deleteGoal(${g.id})">
              Delete
            </button>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error("Goals load error:", err);
  }
}

function triggerAddFunds(goalId) {
  document.getElementById('add-funds-goal-id').value = goalId;
  document.getElementById('form-add-funds').reset();
  openModal('modal-add-funds');
}

async function deleteGoal(goalId) {
  if (!confirm('Are you sure you want to delete this goal?')) return;
  try {
    const res = await fetch(`/api/goals/${goalId}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast('Savings goal deleted.', 'info');
      loadSavingsGoals();
    }
  } catch (e) {
    showToast('Failed to delete goal.', 'error');
  }
}

// Load Settings Data
function loadSettingsData() {
  loadUserProfile();
}
