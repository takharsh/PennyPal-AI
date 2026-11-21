from flask import Blueprint, request, jsonify, session
from database import query_db, execute_db
from datetime import datetime, date

goals_bp = Blueprint('goals', __name__)

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@goals_bp.route('', methods=['GET'])
@login_required
def get_goals():
    user_id = session['user_id']
    rows = query_db("SELECT * FROM savings_goals WHERE user_id = %s ORDER BY target_date ASC", (user_id,))

    today = date.today()
    goals = []

    for r in rows:
        target = float(r['target_amount'])
        current = float(r['current_amount'])
        remaining = max(0.0, target - current)
        progress_pct = round((current / target * 100.0), 1) if target > 0 else 0.0
        
        target_date_raw = str(r['target_date'])
        try:
            target_d = datetime.strptime(target_date_raw[:10], '%Y-%m-%d').date()
            months_left = max(1, (target_d.year - today.year) * 12 + (target_d.month - today.month))
        except ValueError:
            months_left = 1

        monthly_required = round(remaining / months_left, 2) if months_left > 0 else remaining

        goals.append({
            "id": r['id'],
            "goal_name": r['goal_name'],
            "target_amount": target,
            "current_amount": current,
            "remaining_amount": remaining,
            "progress_percentage": min(100.0, progress_pct),
            "target_date": str(r['target_date']),
            "months_left": months_left,
            "monthly_required": monthly_required,
            "is_completed": current >= target
        })

    return jsonify({"success": True, "goals": goals})

@goals_bp.route('', methods=['POST'])
@login_required
def create_goal():
    user_id = session['user_id']
    data = request.get_json() or {}

    goal_name = data.get('goal_name', '').strip()
    target_amount = data.get('target_amount')
    current_amount = data.get('current_amount', 0.0)
    target_date = data.get('target_date', '').strip()

    if not goal_name or target_amount is None or not target_date:
        return jsonify({"success": False, "message": "Goal name, target amount, and target date are required."}), 400

    try:
        target_amount = float(target_amount)
        current_amount = float(current_amount)
        if target_amount <= 0:
            return jsonify({"success": False, "message": "Target amount must be greater than zero."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid numeric format."}), 400

    g_id = execute_db("""
        INSERT INTO savings_goals (user_id, goal_name, target_amount, current_amount, target_date)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, goal_name, target_amount, current_amount, target_date))

    return jsonify({"success": True, "message": "Savings goal created successfully!", "goal_id": g_id}), 201

@goals_bp.route('/<int:goal_id>', methods=['PUT'])
@login_required
def update_goal(goal_id):
    user_id = session['user_id']
    existing = query_db("SELECT id FROM savings_goals WHERE id = %s AND user_id = %s", (goal_id, user_id), one=True)
    if not existing:
        return jsonify({"success": False, "message": "Goal not found."}), 404

    data = request.get_json() or {}
    goal_name = data.get('goal_name', '').strip()
    target_amount = data.get('target_amount')
    current_amount = data.get('current_amount')
    target_date = data.get('target_date', '').strip()

    if not goal_name or target_amount is None or not target_date:
        return jsonify({"success": False, "message": "Goal name, target amount, and target date are required."}), 400

    try:
        target_amount = float(target_amount)
        current_amount = float(current_amount or 0.0)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid numeric format."}), 400

    execute_db("""
        UPDATE savings_goals
        SET goal_name = %s, target_amount = %s, current_amount = %s, target_date = %s
        WHERE id = %s AND user_id = %s
    """, (goal_name, target_amount, current_amount, target_date, goal_id, user_id))

    return jsonify({"success": True, "message": "Savings goal updated successfully!"})

@goals_bp.route('/<int:goal_id>/add-funds', methods=['POST'])
@login_required
def add_funds_to_goal(goal_id):
    user_id = session['user_id']
    existing = query_db("SELECT * FROM savings_goals WHERE id = %s AND user_id = %s", (goal_id, user_id), one=True)
    if not existing:
        return jsonify({"success": False, "message": "Goal not found."}), 404

    data = request.get_json() or {}
    amount_to_add = data.get('amount')

    try:
        amount_to_add = float(amount_to_add)
        if amount_to_add <= 0:
            return jsonify({"success": False, "message": "Amount must be positive."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid amount format."}), 400

    new_current = float(existing['current_amount']) + amount_to_add
    execute_db("UPDATE savings_goals SET current_amount = %s WHERE id = %s AND user_id = %s", (new_current, goal_id, user_id))

    return jsonify({
        "success": True,
        "message": f"Added ₹{amount_to_add:,.2f} to {existing['goal_name']}!",
        "new_total": new_current,
        "is_completed": new_current >= float(existing['target_amount'])
    })

@goals_bp.route('/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_goal(goal_id):
    user_id = session['user_id']
    existing = query_db("SELECT id FROM savings_goals WHERE id = %s AND user_id = %s", (goal_id, user_id), one=True)
    if not existing:
        return jsonify({"success": False, "message": "Goal not found."}), 404

    execute_db("DELETE FROM savings_goals WHERE id = %s AND user_id = %s", (goal_id, user_id))
    return jsonify({"success": True, "message": "Goal deleted successfully!"})
