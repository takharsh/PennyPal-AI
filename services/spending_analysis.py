from datetime import datetime, timedelta

def analyze_user_spending_data(transactions, monthly_income=0.0):
    """
    Analyzes raw transactions list to compute dynamic spending metrics, MoM trends,
    subscription audit, top expenses, and saving opportunities.
    """
    monthly_income = float(monthly_income or 0.0)
    
    if not transactions:
        return {
            "has_data": False,
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net_savings": 0.0,
            "category_totals": {},
            "top_category": "None",
            "highest_expense": {"title": "None", "amount": 0.0},
            "subscription_total": 0.0,
            "mom_change_pct": 0.0,
            "saving_opportunities": ["Add your first expense or income transaction to unlock AI spending insights."]
        }
        
    total_income = 0.0
    total_expenses = 0.0
    category_totals = {}
    subscription_total = 0.0
    highest_expense = {"title": "None", "amount": 0.0}
    
    now = datetime.now()
    this_month_start = datetime(now.year, now.month, 1)
    
    # Calculate last month's date range
    if now.month == 1:
        last_month_start = datetime(now.year - 1, 12, 1)
    else:
        last_month_start = datetime(now.year, now.month - 1, 1)
        
    this_month_exp = 0.0
    last_month_exp = 0.0
    
    for t in transactions:
        t_type = t.get('type')
        amount = float(t.get('amount', 0))
        cat = t.get('category', 'Other')
        title = t.get('title', '')
        
        # Parse transaction date
        t_date_raw = t.get('transaction_date')
        if isinstance(t_date_raw, str):
            try:
                t_date = datetime.strptime(t_date_raw[:10], '%Y-%m-%d')
            except ValueError:
                t_date = now
        elif isinstance(t_date_raw, datetime):
            t_date = t_date_raw
        else:
            t_date = now

        if t_type == 'income':
            total_income += amount
        elif t_type == 'expense':
            total_expenses += amount
            category_totals[cat] = category_totals.get(cat, 0.0) + amount
            
            if amount > highest_expense['amount']:
                highest_expense = {"title": title, "amount": amount, "category": cat}
                
            # Check subscriptions
            if cat.lower() == 'subscription' or any(sub in title.lower() for sub in ['netflix', 'spotify', 'prime', 'youtube', 'gym', 'apple', 'chatgpt', 'subscription']):
                subscription_total += amount
                
            # MoM tracking
            if t_date >= this_month_start:
                this_month_exp += amount
            elif t_date >= last_month_start and t_date < this_month_start:
                last_month_exp += amount

    # Top spending category
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    top_category = sorted_categories[0][0] if sorted_categories else "None"
    
    # MoM percentage change
    if last_month_exp > 0:
        mom_change_pct = ((this_month_exp - last_month_exp) / last_month_exp) * 100.0
    else:
        mom_change_pct = 0.0

    net_savings = max(0.0, (monthly_income if monthly_income > 0 else total_income) - total_expenses)
    savings_rate = (net_savings / (monthly_income or total_income)) * 100.0 if (monthly_income or total_income) > 0 else 0.0

    # Opportunities
    saving_opps = []
    if category_totals.get('Food', 0) > (total_expenses * 0.3):
        saving_opps.append(f"Food & dining represents {(category_totals['Food']/total_expenses*100):.1f}% of total expenses. Preparing meals at home could save up to 25% of this budget.")
        
    if subscription_total > 0:
        saving_opps.append(f"Active recurring subscriptions total ₹{subscription_total:,.2f}. Audit unused memberships to reduce fixed overhead.")
        
    if category_totals.get('Shopping', 0) > (total_expenses * 0.25):
        saving_opps.append(f"Shopping is your second largest expense. Implementing a 48-hour pause before non-essential purchases can curb impulse buys.")
        
    if not saving_opps:
        saving_opps.append("Maintain your current spending discipline while allocating extra surplus into high-yield savings or emergency reserves.")

    return {
        "has_data": True,
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_savings": round(net_savings, 2),
        "savings_rate": round(savings_rate, 1),
        "category_totals": {k: round(v, 2) for k, v in category_totals.items()},
        "top_category": top_category,
        "top_category_amount": round(category_totals.get(top_category, 0.0), 2),
        "highest_expense": highest_expense,
        "subscription_total": round(subscription_total, 2),
        "this_month_exp": round(this_month_exp, 2),
        "last_month_exp": round(last_month_exp, 2),
        "mom_change_pct": round(mom_change_pct, 1),
        "saving_opportunities": saving_opps
    }
