from flask import Blueprint, request, jsonify, session
from database import query_db, execute_db
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@transactions_bp.route('', methods=['GET'])
@login_required
def get_transactions():
    user_id = session['user_id']
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    t_type = request.args.get('type', '').strip()
    sort_by = request.args.get('sort', 'date_desc').strip()

    sql = "SELECT * FROM transactions WHERE user_id = %s"
    params = [user_id]

    if search:
        sql += " AND (title LIKE %s OR category LIKE %s OR description LIKE %s)"
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    if category and category != 'All':
        sql += " AND category = %s"
        params.append(category)

    if t_type and t_type != 'All':
        sql += " AND type = %s"
        params.append(t_type)

    if sort_by == 'date_asc':
        sql += " ORDER BY transaction_date ASC, id ASC"
    elif sort_by == 'amount_desc':
        sql += " ORDER BY amount DESC"
    elif sort_by == 'amount_asc':
        sql += " ORDER BY amount ASC"
    else:  # date_desc
        sql += " ORDER BY transaction_date DESC, id DESC"

    rows = query_db(sql, params)
    
    # Format transactions for JSON
    transactions = []
    for r in rows:
        transactions.append({
            "id": r['id'],
            "type": r['type'],
            "title": r['title'],
            "amount": float(r['amount']),
            "category": r['category'],
            "description": r['description'] or '',
            "transaction_date": str(r['transaction_date']),
            "created_at": str(r['created_at']) if r.get('created_at') else None
        })

    return jsonify({"success": True, "count": len(transactions), "transactions": transactions})

@transactions_bp.route('', methods=['POST'])
@login_required
def add_transaction():
    user_id = session['user_id']
    data = request.get_json() or {}

    t_type = data.get('type', '').strip().lower()
    title = data.get('title', '').strip()
    amount = data.get('amount')
    category = data.get('category', '').strip()
    description = data.get('description', '').strip()
    t_date = data.get('transaction_date', '').strip()

    if t_type not in ['income', 'expense']:
        return jsonify({"success": False, "message": "Invalid transaction type. Must be income or expense."}), 400

    if not title or amount is None or not category:
        return jsonify({"success": False, "message": "Title, amount, and category are required."}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"success": False, "message": "Amount must be greater than zero."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid amount format."}), 400

    if not t_date:
        t_date = datetime.now().strftime('%Y-%m-%d')

    t_id = execute_db("""
        INSERT INTO transactions (user_id, type, title, amount, category, description, transaction_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, t_type, title, amount, category, description, t_date))

    return jsonify({
        "success": True,
        "message": "Transaction added successfully!",
        "transaction_id": t_id
    }), 201

@transactions_bp.route('/<int:tx_id>', methods=['PUT'])
@login_required
def update_transaction(tx_id):
    user_id = session['user_id']
    
    existing = query_db("SELECT id FROM transactions WHERE id = %s AND user_id = %s", (tx_id, user_id), one=True)
    if not existing:
        return jsonify({"success": False, "message": "Transaction not found."}), 404

    data = request.get_json() or {}
    t_type = data.get('type', '').strip().lower()
    title = data.get('title', '').strip()
    amount = data.get('amount')
    category = data.get('category', '').strip()
    description = data.get('description', '').strip()
    t_date = data.get('transaction_date', '').strip()

    if t_type not in ['income', 'expense']:
        return jsonify({"success": False, "message": "Invalid transaction type."}), 400

    if not title or amount is None or not category:
        return jsonify({"success": False, "message": "Title, amount, and category are required."}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"success": False, "message": "Amount must be positive."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid amount format."}), 400

    execute_db("""
        UPDATE transactions
        SET type = %s, title = %s, amount = %s, category = %s, description = %s, transaction_date = %s
        WHERE id = %s AND user_id = %s
    """, (t_type, title, amount, category, description, t_date, tx_id, user_id))

    return jsonify({"success": True, "message": "Transaction updated successfully!"})

@transactions_bp.route('/<int:tx_id>', methods=['DELETE'])
@login_required
def delete_transaction(tx_id):
    user_id = session['user_id']
    
    existing = query_db("SELECT id FROM transactions WHERE id = %s AND user_id = %s", (tx_id, user_id), one=True)
    if not existing:
        return jsonify({"success": False, "message": "Transaction not found."}), 404

    execute_db("DELETE FROM transactions WHERE id = %s AND user_id = %s", (tx_id, user_id))
    return jsonify({"success": True, "message": "Transaction deleted successfully!"})
