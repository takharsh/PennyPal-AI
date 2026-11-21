from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import query_db, execute_db
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

def seed_demo_data(user_id):
    """Seeds sample transactions, budgets, goals, and profile for demo user if empty."""
    tx_check = query_db("SELECT COUNT(*) as cnt FROM transactions WHERE user_id = %s", (user_id,), one=True)
    if tx_check and tx_check['cnt'] > 0:
        return  # Data already exists
        
    print(f"Seeding demo financial dataset for user_id={user_id}...")
    
    # Financial profile check & upsert
    existing_prof = query_db("SELECT id FROM financial_profiles WHERE user_id = %s", (user_id,), one=True)
    if existing_prof:
        execute_db("UPDATE financial_profiles SET monthly_income = 65000.00, emergency_fund = 120000.00 WHERE user_id = %s", (user_id,))
    else:
        execute_db("INSERT INTO financial_profiles (user_id, monthly_income, risk_tolerance, financial_goal, emergency_fund) VALUES (%s, 65000.00, 'Moderate', 'Wealth Accumulation', 120000.00)", (user_id,))
    
    today = datetime.now()
    
    sample_txs = [
        # Income
        ('income', 'Monthly Salary Credit', 65000.00, 'Salary', 'Tech company salary credit', (today - timedelta(days=2)).strftime('%Y-%m-%d')),
        ('income', 'Freelance UI Project', 12000.00, 'Side Income', 'UI Design contract work', (today - timedelta(days=15)).strftime('%Y-%m-%d')),
        
        # Expenses
        ('expense', 'Organic Grocery & Staples', 4500.00, 'Food', 'Weekly grocery store shopping', (today - timedelta(days=1)).strftime('%Y-%m-%d')),
        ('expense', 'Restaurant & Weekend Dining', 2200.00, 'Food', 'Dinner with friends', (today - timedelta(days=3)).strftime('%Y-%m-%d')),
        ('expense', 'Electricity & Internet Bills', 3400.00, 'Bills', 'Monthly apartment utility bills', (today - timedelta(days=5)).strftime('%Y-%m-%d')),
        ('expense', 'Fuel & Metro Transport Pass', 2800.00, 'Travel', 'Monthly commuting expense', (today - timedelta(days=7)).strftime('%Y-%m-%d')),
        ('expense', 'Online Learning Subscription', 1499.00, 'Education', 'Coursera & Udemy certification', (today - timedelta(days=10)).strftime('%Y-%m-%d')),
        ('expense', 'Netflix & Spotify Premium', 799.00, 'Subscription', 'Monthly streaming subscriptions', (today - timedelta(days=12)).strftime('%Y-%m-%d')),
        ('expense', 'Shopping & Apparel', 5200.00, 'Shopping', 'New footwear and clothes', (today - timedelta(days=14)).strftime('%Y-%m-%d')),
        ('expense', 'Gym Membership', 1500.00, 'Healthcare', 'Fitness club monthly fee', (today - timedelta(days=18)).strftime('%Y-%m-%d')),
        ('expense', 'Movie Tickets & Snacks', 1100.00, 'Entertainment', 'Weekend IMAX movie', (today - timedelta(days=20)).strftime('%Y-%m-%d')),
        ('expense', 'Food Delivery Order', 650.00, 'Food', 'Swiggy dinner order', (today - timedelta(days=22)).strftime('%Y-%m-%d')),
        ('expense', 'Tech Gadget Accessories', 2900.00, 'Shopping', 'Wireless earphones', (today - timedelta(days=25)).strftime('%Y-%m-%d'))
    ]
    
    for t_type, title, amt, cat, desc, t_date in sample_txs:
        execute_db("""
            INSERT INTO transactions (user_id, type, title, amount, category, description, transaction_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, t_type, title, amt, cat, desc, t_date))
        
    # Sample budgets
    sample_budgets = [
        ('Food', 8000.00),
        ('Bills', 5000.00),
        ('Shopping', 6000.00),
        ('Travel', 4000.00),
        ('Education', 3000.00),
        ('Entertainment', 2500.00),
        ('Subscription', 1500.00),
        ('Healthcare', 3000.00)
    ]
    for cat, limit in sample_budgets:
        existing_b = query_db("SELECT id FROM budgets WHERE user_id = %s AND category = %s", (user_id, cat), one=True)
        if existing_b:
            execute_db("UPDATE budgets SET monthly_limit = %s WHERE id = %s", (limit, existing_b['id']))
        else:
            execute_db("INSERT INTO budgets (user_id, category, monthly_limit) VALUES (%s, %s, %s)", (user_id, cat, limit))

    # Sample Savings Goals
    sample_goals = [
        ('New Developer Laptop', 85000.00, 45000.00, (today + timedelta(days=120)).strftime('%Y-%m-%d')),
        ('Emergency Shield Fund', 150000.00, 120000.00, (today + timedelta(days=180)).strftime('%Y-%m-%d')),
        ('Tech Conference Trip', 35000.00, 18000.00, (today + timedelta(days=90)).strftime('%Y-%m-%d'))
    ]
    for g_name, target, current, t_date in sample_goals:
        execute_db("""
            INSERT INTO savings_goals (user_id, goal_name, target_amount, current_amount, target_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, g_name, target, current, t_date))

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not name or not email or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400
        
    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400
        
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400
        
    # Check duplicate email
    existing = query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
    if existing:
        return jsonify({"success": False, "message": "Email is already registered. Please log in."}), 409
        
    pwd_hash = generate_password_hash(password)
    user_id = execute_db("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)", (name, email, pwd_hash))
    
    # Initialize profile
    execute_db("INSERT INTO financial_profiles (user_id, monthly_income) VALUES (%s, 0.00)", (user_id,))
    
    # Set session
    session.clear()
    session['user_id'] = user_id
    session['user_name'] = name
    session['user_email'] = email
    
    return jsonify({
        "success": True,
        "message": "Account created successfully!",
        "user": {"id": user_id, "name": name, "email": email}
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember = data.get('remember', False)
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    user = query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)
    
    # Auto-create demo user if logging in as demo and doesn't exist
    if not user and email == 'demo@pennypal.ai' and password == 'Demo@123':
        pwd_hash = generate_password_hash('Demo@123')
        user_id = execute_db("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)", ('Demo User', 'demo@pennypal.ai', pwd_hash))
        seed_demo_data(user_id)
        user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    if email == 'demo@pennypal.ai':
        seed_demo_data(user['id'])

    session.clear()
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    if remember:
        session.permanent = True

    return jsonify({
        "success": True,
        "message": "Logged in successfully.",
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "currency": user.get('currency', '₹')
        }
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
        
    user = query_db("SELECT id, name, email, currency, created_at FROM users WHERE id = %s", (user_id,), one=True)
    if not user:
        session.clear()
        return jsonify({"success": False, "message": "User not found"}), 404
        
    profile = query_db("SELECT * FROM financial_profiles WHERE user_id = %s", (user_id,), one=True) or {}

    return jsonify({
        "success": True,
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "currency": user.get('currency', '₹'),
            "profile": {
                "monthly_income": float(profile.get('monthly_income', 0.0)),
                "risk_tolerance": profile.get('risk_tolerance', 'Moderate'),
                "financial_goal": profile.get('financial_goal', 'Wealth Accumulation'),
                "emergency_fund": float(profile.get('emergency_fund', 0.0))
            }
        }
    })
