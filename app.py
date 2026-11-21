from flask import Flask, render_template, redirect, url_for, session
from flask_cors import CORS
from config import Config
from database import init_db

# Import API blueprints
from routes.auth import auth_bp
from routes.transactions import transactions_bp
from routes.analytics import analytics_bp
from routes.budget import budget_bp
from routes.goals import goals_bp
from routes.investments import investments_bp
from routes.assistant import assistant_bp
from routes.settings import settings_bp

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for local APIs
CORS(app, supports_credentials=True)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
app.register_blueprint(analytics_bp, url_prefix='/api')
app.register_blueprint(budget_bp, url_prefix='/api/budget')
app.register_blueprint(goals_bp, url_prefix='/api/goals')
app.register_blueprint(investments_bp, url_prefix='/api/investments')
app.register_blueprint(assistant_bp, url_prefix='/api/ai')
app.register_blueprint(settings_bp, url_prefix='/api/settings')

# Page Routes
@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup')
def signup():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Initialize DB tables on startup
try:
    init_db()
except Exception as e:
    print(f"DB Startup notice: {e}")

if __name__ == '__main__':
    print("Starting PennyPal AI server on http://127.0.0.1:5000/ ...")
    app.run(host='127.0.0.1', port=5000, debug=True)
