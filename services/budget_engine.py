def generate_budget_recommendations(monthly_income, category_expenses):
    """
    Generates recommended monthly budget per category based on monthly income
    and standard benchmark allocations (50/30/20 framework).
    Compares against user's actual category spending.
    """
    income = float(monthly_income or 0.0)
    
    # If no income set, derive estimate from total category expenses or baseline 25000
    if income <= 0:
        total_spent = sum(category_expenses.values())
        income = max(total_spent * 1.25, 30000.0)
        
    # Standard allocation multipliers
    allocations = {
        'Food': 0.20,          # 20% Needs
        'Bills': 0.25,         # 25% Utilities / Housing / Phone
        'Shopping': 0.12,      # 12% Lifestyle
        'Travel': 0.10,        # 10% Commute / Transport
        'Education': 0.08,     # 8% Books, Courses, Self-improvement
        'Entertainment': 0.05, # 5% Leisure
        'Healthcare': 0.05,    # 5% Health & Wellness
        'Subscription': 0.03,  # 3% Digital Subscriptions
        'Other': 0.02          # 2% Miscellaneous
    }
    
    recommendations = []
    
    for category, ratio in allocations.items():
        recommended_amount = round(income * ratio, 2)
        actual_spent = round(category_expenses.get(category, 0.0), 2)
        difference = round(actual_spent - recommended_amount, 2)
        
        if difference > 0:
            status = 'Over Budget'
            alert = f"₹{difference:,.2f} over recommended limit"
        elif actual_spent == 0:
            status = 'Unused'
            alert = "No spending recorded"
        else:
            status = 'Within Budget'
            alert = f"₹{abs(difference):,.2f} buffer remaining"

        recommendations.append({
            "category": category,
            "recommended": recommended_amount,
            "actual": actual_spent,
            "difference": difference,
            "status": status,
            "alert": alert
        })
        
    # Savings target recommendation (Remainder ~ 10-20%)
    recommended_savings = round(income * 0.20, 2)
    
    return {
        "monthly_income": income,
        "recommended_savings": recommended_savings,
        "categories": recommendations
    }
