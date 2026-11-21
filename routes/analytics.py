from flask import Blueprint, jsonify, session
from database import query_db
from services.financial_health import calculate_financial_health_score
from services.spending_analysis import analyze_user_spending_data
from services.gemini_service import generate_financial_explanation
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@analytics_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard_summary():
    user_id = session['user_id']
    
    # User Profile & Stored Monthly Income
    profile = query_db("SELECT * FROM financial_profiles WHERE user_id = %s", (user_id,), one=True) or {}
    stored_income = float(profile.get('monthly_income', 0.0))
    emergency_fund = float(profile.get('emergency_fund', 0.0))

    # All user transactions
    tx_rows = query_db("SELECT * FROM transactions WHERE user_id = %s ORDER BY transaction_date DESC", (user_id,))
    
    total_income = 0.0
    total_expenses = 0.0
    category_expenses = {}

    for t in tx_rows:
        amt = float(t['amount'])
        if t['type'] == 'income':
            total_income += amt
        else:
            total_expenses += amt
            cat = t['category']
            category_expenses[cat] = category_expenses.get(cat, 0.0) + amt

    # If transactions income is zero, fallback to stored profile income
    effective_income = total_income if total_income > 0 else stored_income
    net_savings = max(0.0, effective_income - total_expenses)
    total_balance = effective_income - total_expenses

    # Recent transactions (top 5)
    recent_txs = []
    for t in tx_rows[:5]:
        recent_txs.append({
            "id": t['id'],
            "type": t['type'],
            "title": t['title'],
            "amount": float(t['amount']),
            "category": t['category'],
            "transaction_date": str(t['transaction_date'])
        })

    # Fetch Budgets for score calculation
    budgets = query_db("SELECT * FROM budgets WHERE user_id = %s", (user_id,))
    
    # Financial Health Score
    health_result = calculate_financial_health_score(
        income=effective_income,
        total_expenses=total_expenses,
        category_expenses=category_expenses,
        budgets=budgets,
        emergency_fund=emergency_fund
    )

    # Generate Smart Alerts
    alerts = []
    if total_expenses > effective_income and effective_income > 0:
        alerts.append({"type": "danger", "icon": "exclamation-triangle", "title": "Overspending Alert", "message": f"Total expenses exceed your monthly income by ₹{(total_expenses - effective_income):,.2f}."})
    
    if category_expenses.get('Food', 0) > (total_expenses * 0.35) and total_expenses > 0:
        alerts.append({"type": "warning", "icon": "utensils", "title": "High Food Budget", "message": "Food & dining spending is 35%+ of your total expenses this period."})
        
    for b in budgets:
        cat = b['category']
        limit = float(b['monthly_limit'])
        spent = category_expenses.get(cat, 0.0)
        if limit > 0 and spent > limit:
            alerts.append({"type": "warning", "icon": "exclamation-circle", "title": f"{cat} Budget Exceeded", "message": f"Spent ₹{spent:,.2f} of ₹{limit:,.2f} limit."})

    if not alerts:
        alerts.append({"type": "success", "icon": "check-circle", "title": "Finances On Track", "message": "Your category spending and monthly savings buffers look well-balanced!"})

    return jsonify({
        "success": True,
        "metrics": {
            "total_balance": round(total_balance, 2),
            "monthly_income": round(effective_income, 2),
            "monthly_expenses": round(total_expenses, 2),
            "monthly_savings": round(net_savings, 2)
        },
        "health_score": health_result['score'],
        "health_rating": health_result['rating'],
        "recent_transactions": recent_txs,
        "alerts": alerts
    })

@analytics_bp.route('/analytics', methods=['GET'])
@login_required
def get_analytics():
    user_id = session['user_id']
    tx_rows = query_db("SELECT * FROM transactions WHERE user_id = %s ORDER BY transaction_date ASC", (user_id,))
    budgets = query_db("SELECT * FROM budgets WHERE user_id = %s", (user_id,))

    # 1. Income vs Expense Trend (by month)
    monthly_data = {}
    category_totals = {}
    weekly_totals = {"Week 1": 0.0, "Week 2": 0.0, "Week 3": 0.0, "Week 4": 0.0}
    now = datetime.now()

    for t in tx_rows:
        t_date_str = str(t['transaction_date'])
        try:
            t_date = datetime.strptime(t_date_str[:10], '%Y-%m-%d')
            m_key = t_date.strftime('%b %Y')
        except ValueError:
            m_key = 'Current'
            t_date = now

        if m_key not in monthly_data:
            monthly_data[m_key] = {"income": 0.0, "expense": 0.0}

        amt = float(t['amount'])
        if t['type'] == 'income':
            monthly_data[m_key]['income'] += amt
        else:
            monthly_data[m_key]['expense'] += amt
            cat = t['category']
            category_totals[cat] = category_totals.get(cat, 0.0) + amt

            # Weekly breakdown for current month
            if t_date.month == now.month and t_date.year == now.year:
                day = t_date.day
                if day <= 7:
                    weekly_totals['Week 1'] += amt
                elif day <= 14:
                    weekly_totals['Week 2'] += amt
                elif day <= 21:
                    weekly_totals['Week 3'] += amt
                else:
                    weekly_totals['Week 4'] += amt

    months_labels = list(monthly_data.keys())
    income_series = [round(monthly_data[m]['income'], 2) for m in months_labels]
    expense_series = [round(monthly_data[m]['expense'], 2) for m in months_labels]
    savings_series = [round(monthly_data[m]['income'] - monthly_data[m]['expense'], 2) for m in months_labels]

    # Category Doughnut Chart
    cat_labels = list(category_totals.keys())
    cat_series = [round(v, 2) for v in category_totals.values()]

    # Budget vs Actual
    budget_cats = []
    budget_limits = []
    budget_actuals = []
    for b in budgets:
        c = b['category']
        l = float(b['monthly_limit'])
        budget_cats.append(c)
        budget_limits.append(l)
        budget_actuals.append(round(category_totals.get(c, 0.0), 2))

    return jsonify({
        "success": True,
        "charts": {
            "income_vs_expense": {
                "labels": months_labels or ["Current"],
                "income": income_series or [0.0],
                "expense": expense_series or [0.0]
            },
            "category_doughnut": {
                "labels": cat_labels or ["No Expenses"],
                "series": cat_series or [1]
            },
            "weekly_spending": {
                "labels": list(weekly_totals.keys()),
                "series": [round(v, 2) for v in weekly_totals.values()]
            },
            "savings_trend": {
                "labels": months_labels or ["Current"],
                "series": savings_series or [0.0]
            },
            "budget_vs_actual": {
                "labels": budget_cats or ["Food", "Bills", "Shopping"],
                "limits": budget_limits or [5000, 4000, 3000],
                "actuals": budget_actuals or [0, 0, 0]
            }
        }
    })

@analytics_bp.route('/financial-health', methods=['GET'])
@login_required
def get_financial_health_page():
    user_id = session['user_id']
    profile = query_db("SELECT * FROM financial_profiles WHERE user_id = %s", (user_id,), one=True) or {}
    income = float(profile.get('monthly_income', 0.0))
    emergency_fund = float(profile.get('emergency_fund', 0.0))

    tx_rows = query_db("SELECT * FROM transactions WHERE user_id = %s", (user_id,))
    total_income = sum(float(t['amount']) for t in tx_rows if t['type'] == 'income')
    total_expenses = sum(float(t['amount']) for t in tx_rows if t['type'] == 'expense')
    
    category_expenses = {}
    for t in tx_rows:
        if t['type'] == 'expense':
            c = t['category']
            category_expenses[c] = category_expenses.get(c, 0.0) + float(t['amount'])

    budgets = query_db("SELECT * FROM budgets WHERE user_id = %s", (user_id,))
    effective_income = total_income if total_income > 0 else income

    health_summary = calculate_financial_health_score(
        income=effective_income,
        total_expenses=total_expenses,
        category_expenses=category_expenses,
        budgets=budgets,
        emergency_fund=emergency_fund
    )

    ai_explanation = generate_financial_explanation(health_summary)
    health_summary['ai_explanation'] = ai_explanation

    return jsonify({"success": True, "health": health_summary})
