from flask import Blueprint, request, jsonify, session
from database import query_db, execute_db
from services.budget_engine import generate_budget_recommendations

budget_bp = Blueprint('budget', __name__)

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@budget_bp.route('', methods=['GET'])
@login_required
def get_budgets():
    user_id = session['user_id']
    budgets = query_db("SELECT * FROM budgets WHERE user_id = %s ORDER BY category ASC", (user_id,))
    
    # Calculate actual spent for each budget category
    tx_rows = query_db("SELECT category, SUM(amount) as total_spent FROM transactions WHERE user_id = %s AND type = 'expense' GROUP BY category", (user_id,))
    spent_map = {r['category']: float(r['total_spent']) for r in tx_rows}

    result = []
    for b in budgets:
        cat = b['category']
        limit = float(b['monthly_limit'])
        spent = spent_map.get(cat, 0.0)
        diff = spent - limit
        result.append({
            "id": b['id'],
            "category": cat,
            "monthly_limit": limit,
            "actual_spent": spent,
            "difference": round(diff, 2),
            "is_over": spent > limit
        })

    return jsonify({"success": True, "budgets": result})

@budget_bp.route('/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    user_id = session['user_id']
    profile = query_db("SELECT monthly_income FROM financial_profiles WHERE user_id = %s", (user_id,), one=True) or {}
    income = float(profile.get('monthly_income', 0.0))

    tx_rows = query_db("SELECT category, SUM(amount) as total_spent FROM transactions WHERE user_id = %s AND type = 'expense' GROUP BY category", (user_id,))
    cat_expenses = {r['category']: float(r['total_spent']) for r in tx_rows}

    data = generate_budget_recommendations(monthly_income=income, category_expenses=cat_expenses)
    return jsonify({"success": True, "data": data})

@budget_bp.route('', methods=['POST'])
@login_required
def save_budget():
    user_id = session['user_id']
    data = request.get_json() or {}
    category = data.get('category', '').strip()
    limit = data.get('monthly_limit')

    if not category or limit is None:
        return jsonify({"success": False, "message": "Category and monthly_limit are required."}), 400

    try:
        limit = float(limit)
        if limit <= 0:
            return jsonify({"success": False, "message": "Limit must be greater than zero."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid limit format."}), 400

    existing = query_db("SELECT id FROM budgets WHERE user_id = %s AND category = %s", (user_id, category), one=True)
    if existing:
        execute_db("UPDATE budgets SET monthly_limit = %s WHERE id = %s", (limit, existing['id']))
    else:
        execute_db("INSERT INTO budgets (user_id, category, monthly_limit) VALUES (%s, %s, %s)", (user_id, category, limit))

    return jsonify({"success": True, "message": f"Budget for {category} updated to ₹{limit:,.2f}."})

@budget_bp.route('/accept-recommendations', methods=['POST'])
@login_required
def accept_all_recommendations():
    user_id = session['user_id']
    profile = query_db("SELECT monthly_income FROM financial_profiles WHERE user_id = %s", (user_id,), one=True) or {}
    income = float(profile.get('monthly_income', 0.0))

    tx_rows = query_db("SELECT category, SUM(amount) as total_spent FROM transactions WHERE user_id = %s AND type = 'expense' GROUP BY category", (user_id,))
    cat_expenses = {r['category']: float(r['total_spent']) for r in tx_rows}

    rec_data = generate_budget_recommendations(monthly_income=income, category_expenses=cat_expenses)

    for item in rec_data['categories']:
        cat = item['category']
        recommended = item['recommended']
        existing = query_db("SELECT id FROM budgets WHERE user_id = %s AND category = %s", (user_id, cat), one=True)
        if existing:
            execute_db("UPDATE budgets SET monthly_limit = %s WHERE id = %s", (recommended, existing['id']))
        else:
            execute_db("INSERT INTO budgets (user_id, category, monthly_limit) VALUES (%s, %s, %s)", (user_id, cat, recommended))

    return jsonify({"success": True, "message": "All recommended category budgets applied successfully!"})
