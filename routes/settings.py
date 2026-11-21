from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import query_db, execute_db

settings_bp = Blueprint('settings', __name__)

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@settings_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    user_id = session['user_id']
    data = request.get_json() or {}

    name = data.get('name', '').strip()
    currency = data.get('currency', '₹').strip()
    monthly_income = data.get('monthly_income')
    risk_tolerance = data.get('risk_tolerance', 'Moderate').strip()
    financial_goal = data.get('financial_goal', 'Wealth Accumulation').strip()
    emergency_fund = data.get('emergency_fund')

    if not name:
        return jsonify({"success": False, "message": "Name is required."}), 400

    execute_db("UPDATE users SET name = %s, currency = %s WHERE id = %s", (name, currency, user_id))
    session['user_name'] = name

    try:
        m_income = float(monthly_income or 0.0)
        e_fund = float(emergency_fund or 0.0)
    except (ValueError, TypeError):
        m_income = 0.0
        e_fund = 0.0

    existing = query_db("SELECT id FROM financial_profiles WHERE user_id = %s", (user_id,), one=True)
    if existing:
        execute_db("""
            UPDATE financial_profiles
            SET monthly_income = %s, risk_tolerance = %s, financial_goal = %s, emergency_fund = %s
            WHERE user_id = %s
        """, (m_income, risk_tolerance, financial_goal, e_fund, user_id))
    else:
        execute_db("""
            INSERT INTO financial_profiles (user_id, monthly_income, risk_tolerance, financial_goal, emergency_fund)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, m_income, risk_tolerance, financial_goal, e_fund))

    return jsonify({"success": True, "message": "Profile and financial preferences updated successfully!"})

@settings_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    user_id = session['user_id']
    data = request.get_json() or {}

    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({"success": False, "message": "Current and new password are required."}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "New password must be at least 6 characters."}), 400

    user = query_db("SELECT password_hash FROM users WHERE id = %s", (user_id,), one=True)
    if not check_password_hash(user['password_hash'], old_password):
        return jsonify({"success": False, "message": "Current password is incorrect."}), 401

    new_hash = generate_password_hash(new_password)
    execute_db("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))

    return jsonify({"success": True, "message": "Password changed successfully!"})
