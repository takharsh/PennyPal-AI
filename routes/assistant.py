from flask import Blueprint, request, jsonify, session
from database import query_db
from services.spending_analysis import analyze_user_spending_data
from services.gemini_service import analyze_spending, financial_chat

assistant_bp = Blueprint('assistant', __name__)

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@assistant_bp.route('/spending-analysis', methods=['POST'])
@login_required
def get_ai_spending_analysis():
    user_id = session['user_id']
    profile = query_db("SELECT monthly_income FROM financial_profiles WHERE user_id = %s", (user_id,), one=True) or {}
    income = float(profile.get('monthly_income', 0.0))

    tx_rows = query_db("SELECT * FROM transactions WHERE user_id = %s ORDER BY transaction_date DESC", (user_id,))
    
    # Analyze raw data
    spending_summary = analyze_user_spending_data(tx_rows, monthly_income=income)
    
    # Get Gemini analysis
    gemini_result = analyze_spending(spending_summary)
    
    return jsonify({
        "success": True,
        "metrics": spending_summary,
        "ai_insights": gemini_result['ai_insights'],
        "key_observations": gemini_result['key_observations']
    })

@assistant_bp.route('/chat', methods=['POST'])
@login_required
def chat_with_assistant():
    user_id = session['user_id']
    data = request.get_json() or {}
    user_prompt = data.get('prompt', '').strip()
    history = data.get('history', '')

    if not user_prompt:
        return jsonify({"success": False, "message": "Prompt cannot be empty."}), 400

    # Build DB Context for Gemini
    profile = query_db("SELECT * FROM financial_profiles WHERE user_id = %s", (user_id,), one=True) or {}
    income = float(profile.get('monthly_income', 0.0))
    emergency_fund = float(profile.get('emergency_fund', 0.0))

    tx_rows = query_db("SELECT * FROM transactions WHERE user_id = %s ORDER BY transaction_date DESC", (user_id,))
    budgets = query_db("SELECT * FROM budgets WHERE user_id = %s", (user_id,))
    goals = query_db("SELECT * FROM savings_goals WHERE user_id = %s", (user_id,))

    spending_summary = analyze_user_spending_data(tx_rows, monthly_income=income)

    db_context = {
        "user_name": session.get('user_name', 'User'),
        "monthly_income": income,
        "total_income": spending_summary['total_income'],
        "total_expenses": spending_summary['total_expenses'],
        "net_savings": spending_summary['net_savings'],
        "savings_rate_pct": spending_summary.get('savings_rate', 0),
        "top_category": spending_summary['top_category'],
        "highest_expense": spending_summary['highest_expense'],
        "subscription_total": spending_summary['subscription_total'],
        "emergency_fund": emergency_fund,
        "active_budgets": [{"category": b['category'], "limit": float(b['monthly_limit'])} for b in budgets],
        "active_goals": [{"name": g['goal_name'], "target": float(g['target_amount']), "saved": float(g['current_amount'])} for g in goals]
    }

    # Call Gemini Financial Assistant
    ai_response = financial_chat(history, db_context, user_prompt)

    return jsonify({
        "success": True,
        "response": ai_response
    })
