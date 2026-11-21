from flask import Blueprint, request, jsonify, session
from database import query_db, execute_db
from services.gemini_service import investment_guidance

investments_bp = Blueprint('investments', __name__)

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@investments_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_investments():
    user_id = session['user_id']
    data = request.get_json() or {}

    available_amount = float(data.get('available_amount') or 0.0)
    risk_level = data.get('risk_level', 'Moderate').strip()
    investment_goal = data.get('investment_goal', 'Wealth Growth').strip()
    investment_horizon = data.get('investment_horizon', '3-5 years').strip()
    has_emergency_fund = data.get('has_emergency_fund', True)

    profile = query_db("SELECT * FROM financial_profiles WHERE user_id = %s", (user_id,), one=True) or {}
    monthly_income = float(profile.get('monthly_income', 0.0))

    if available_amount <= 0:
        return jsonify({"success": False, "message": "Please specify an available amount to invest."}), 400

    # Record preference in DB
    execute_db("""
        INSERT INTO investment_preferences (user_id, risk_level, investment_goal, investment_horizon, amount)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, risk_level, investment_goal, investment_horizon, available_amount))

    # Structured asset allocations based on risk matrix
    if risk_level == 'Low':
        allocations = [
            {"category": "Bank Fixed Deposits / Recurring Deposits", "percentage": 40, "risk": "Very Low", "liquidity": "High", "horizon": "1-3 Years", "reason": "Guaranteed principal protection and stable interest yield."},
            {"category": "Sovereign Gold Bonds / Gold ETFs", "percentage": 30, "risk": "Low-Moderate", "liquidity": "Medium", "horizon": "3-5 Years", "reason": "Inflation hedge and portfolio stability."},
            {"category": "Short-Term Debt Mutual Funds", "percentage": 30, "risk": "Low", "liquidity": "Very High", "horizon": "1-2 Years", "reason": "Higher yield than savings accounts with minimal duration risk."}
        ]
    elif risk_level == 'High':
        allocations = [
            {"category": "Nifty 50 & Large-Cap Index Funds", "percentage": 50, "risk": "Moderate-High", "liquidity": "High", "horizon": "5+ Years", "reason": "Tracks India's top 50 companies for long-term compound compounding growth."},
            {"category": "Flexi-Cap & Mid-Cap Equity Funds", "percentage": 35, "risk": "High", "liquidity": "High", "horizon": "5+ Years", "reason": "Higher growth potential in emerging market leaders."},
            {"category": "Sovereign Gold & Emergency Cash Reserve", "percentage": 15, "risk": "Low", "liquidity": "Immediate", "horizon": "Anytime", "reason": "Protective volatility buffer during market downturns."}
        ]
    else: # Moderate
        allocations = [
            {"category": "Broad Market Equity Index Funds", "percentage": 50, "risk": "Moderate", "liquidity": "High", "horizon": "3-5 Years", "reason": "Balanced exposure to Indian economic growth with low expense ratios."},
            {"category": "Corporate Bond & Target Maturity Debt Funds", "percentage": 30, "risk": "Low-Moderate", "liquidity": "High", "horizon": "2-4 Years", "reason": "Predictable fixed-income yield buffer."},
            {"category": "Gold ETFs / Sovereign Instruments", "percentage": 20, "risk": "Low", "liquidity": "Medium", "horizon": "3-5 Years", "reason": "Portfolio diversification against equity market drawdowns."}
        ]

    # Call Gemini for educational personalization
    user_context = {
        "monthly_income": monthly_income,
        "available_amount": available_amount,
        "risk_level": risk_level,
        "horizon": investment_horizon,
        "has_emergency_fund": has_emergency_fund
    }
    ai_guidance_text = investment_guidance(user_context)

    return jsonify({
        "success": True,
        "risk_level": risk_level,
        "horizon": investment_horizon,
        "available_amount": available_amount,
        "allocations": allocations,
        "ai_guidance": ai_guidance_text,
        "disclaimer": "IMPORTANT DISCLAIMER: This suggestion is strictly for educational and illustrative purposes. PennyPal AI does not guarantee financial returns or act as a licensed SEBI/SEC financial advisor. Always perform your own research before committing funds."
    })
