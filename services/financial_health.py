def calculate_financial_health_score(income, total_expenses, category_expenses, budgets, emergency_fund):
    """
    Calculates transparent 0-100 Financial Health Score based on user's real DB data.
    
    Weights:
    1. Savings Rate: 30%
    2. Budget Control: 20%
    3. Expense-to-Income Ratio: 20%
    4. Emergency Preparedness: 15%
    5. Spending Stability: 15%
    """
    income = float(income or 0.0)
    total_expenses = float(total_expenses or 0.0)
    emergency_fund = float(emergency_fund or 0.0)
    
    if income <= 0:
        return {
            "score": 50,
            "rating": "Baseline",
            "breakdown": {
                "savings_rate_score": 10,
                "budget_control_score": 10,
                "expense_ratio_score": 10,
                "emergency_fund_score": 10,
                "stability_score": 10
            },
            "positives": ["Account initialized."],
            "negatives": ["No income recorded yet for calculation."],
            "improvements": ["Add monthly income in Settings to get an accurate Health Score."]
        }
        
    net_savings = max(0.0, income - total_expenses)
    savings_rate = (net_savings / income) * 100.0 if income > 0 else 0.0
    expense_ratio = (total_expenses / income) * 100.0 if income > 0 else 0.0
    
    # 1. Savings Rate Score (Max 30)
    # Ideal savings rate is >= 20%
    if savings_rate >= 30:
        savings_score = 30.0
    elif savings_rate >= 20:
        savings_score = 25.0
    elif savings_rate >= 10:
        savings_score = 18.0
    elif savings_rate > 0:
        savings_score = 10.0
    else:
        savings_score = 0.0
        
    # 2. Expense to Income Ratio Score (Max 20)
    # Ideal expense ratio <= 50-60%
    if expense_ratio <= 50:
        expense_score = 20.0
    elif expense_ratio <= 70:
        expense_score = 15.0
    elif expense_ratio <= 85:
        expense_score = 10.0
    elif expense_ratio <= 100:
        expense_score = 5.0
    else:
        expense_score = 0.0
        
    # 3. Budget Control Score (Max 20)
    # Compare category expenses to monthly limits in budgets dict/list
    if not budgets:
        budget_score = 12.0  # Neutral default
    else:
        within_budget = 0
        total_budgets = len(budgets)
        for b in budgets:
            cat = b.get('category')
            limit = float(b.get('monthly_limit', 0))
            spent = float(category_expenses.get(cat, 0))
            if limit > 0 and spent <= limit:
                within_budget += 1
        budget_score = round((within_budget / total_budgets) * 20.0, 1) if total_budgets > 0 else 12.0

    # 4. Emergency Fund Score (Max 15)
    # Target: 3 to 6 months of expenses
    monthly_exp = total_expenses if total_expenses > 0 else income * 0.5
    months_covered = (emergency_fund / monthly_exp) if monthly_exp > 0 else 0
    if months_covered >= 6:
        emergency_score = 15.0
    elif months_covered >= 3:
        emergency_score = 12.0
    elif months_covered >= 1:
        emergency_score = 7.0
    elif emergency_fund > 0:
        emergency_score = 4.0
    else:
        emergency_score = 0.0

    # 5. Stability & Debt Control Score (Max 15)
    if expense_ratio < 90 and savings_rate >= 10:
        stability_score = 15.0
    elif expense_ratio <= 100:
        stability_score = 10.0
    else:
        stability_score = 3.0
        
    total_score = int(round(savings_score + expense_score + budget_score + emergency_score + stability_score))
    total_score = max(0, min(100, total_score))
    
    # Rating label
    if total_score >= 85:
        rating = "Excellent"
    elif total_score >= 70:
        rating = "Good"
    elif total_score >= 50:
        rating = "Fair"
    else:
        rating = "Needs Attention"

    # Positives & Negatives
    positives = []
    negatives = []
    improvements = []
    
    if savings_rate >= 20:
        positives.append(f"Strong savings rate of {savings_rate:.1f}% of income.")
    else:
        negatives.append(f"Savings rate is low ({savings_rate:.1f}%). Target at least 20%.")
        improvements.append("Automate a monthly transfer of 15-20% of income directly into savings on payday.")

    if expense_ratio <= 65:
        positives.append(f"Healthy expense-to-income ratio ({expense_ratio:.1f}%).")
    else:
        negatives.append(f"High expense-to-income ratio ({expense_ratio:.1f}%).")
        improvements.append("Audit recurring subscriptions and eating out to trim monthly cash outflow.")

    if emergency_score >= 12:
        positives.append(f"Solid emergency fund covering {months_covered:.1f} months of expenses.")
    else:
        negatives.append(f"Emergency fund covers only {months_covered:.1f} months of expenses.")
        improvements.append("Build emergency savings until it covers 3 to 6 months of living expenses.")

    if budget_score >= 15:
        positives.append("Most spending categories are strictly within assigned budget limits.")
    else:
        improvements.append("Set realistic monthly budgets for high-frequency categories like Food and Shopping.")

    return {
        "score": total_score,
        "rating": rating,
        "breakdown": {
            "savings_rate_score": round(savings_score, 1),
            "budget_control_score": round(budget_score, 1),
            "expense_ratio_score": round(expense_score, 1),
            "emergency_fund_score": round(emergency_score, 1),
            "stability_score": round(stability_score, 1)
        },
        "metrics": {
            "savings_rate": round(savings_rate, 1),
            "expense_ratio": round(expense_ratio, 1),
            "months_emergency": round(months_covered, 1)
        },
        "positives": positives,
        "negatives": negatives,
        "improvements": improvements
    }
