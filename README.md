# PennyPal AI
> **Tagline:** *"Your money. Smarter decisions."*  
> **Final-Year B.Tech Computer Science Major Project**

PennyPal AI is a production-style full-stack financial intelligence application built using Python, Flask, MySQL, Vanilla JavaScript, Chart.js, and the Google Gemini API. It empowers users to make smarter financial decisions through real-time expense tracking, deterministic health score evaluations, automated 50/30/20 budget recommendations, educational investment suggestions, and an interactive AI financial assistant.

---

## 🌟 Key Features

1. **Secure Session Authentication:**
   - Password hashing with Werkzeug (`pbkdf2:sha256`).
   - Registration with duplicate email prevention and form validation.
   - Quick Evaluator Demo Login (`demo@pennypal.ai` / `Demo@123`) with automatic financial data seeding.

2. **Full Transaction Management (Expense Tracking):**
   - Real-time CRUD operations for Income and Expenses with parameterized SQL queries.
   - Live search, category filtering, type filtering, and multi-field sorting.
   - Immediate recalculation of total balance, monthly income, expenses, and savings.

3. **Deterministic Financial Health Score (0–100):**
   - Backend mathematical calculation based on 5 weighted metrics:
     - **Savings Rate** (30%)
     - **Budget Control** (20%)
     - **Expense-to-Income Ratio** (20%)
     - **Emergency Fund Coverage** (15%)
     - **Spending Stability & Balance** (15%)
   - Interactive circular gauge UI, breakdown metrics, and Gemini narrative explanation.

4. **AI Spending Analysis (Google Gemini API Integration):**
   - Aggregates user transaction data from MySQL.
   - Analyzes category distribution, subscription costs, and month-over-month shifts.
   - Identifies actionable saving opportunities and subscription traps.

5. **AI Budget Recommendation Engine:**
   - Evaluates monthly income and spending patterns using the 50/30/20 benchmark rule.
   - Generates category budget limits and highlights over-budget items.
   - Allows users to accept recommended budgets in bulk or customize limits.

6. **Savings Goals Tracker:**
   - Milestone tracking with progress bars, target dates, and remaining balance calculations.
   - Computes required monthly saving rates to meet targets on schedule.
   - Add funds modal that updates dashboard totals dynamically.

7. **Educational Investment Suggestions:**
   - Tailored asset allocation recommendations (Fixed Deposits, Index Funds, Debt Funds, Gold ETFs) based on risk tolerance (Low, Moderate, High) and horizon.
   - Includes educational explanations and clear compliance disclaimers.

8. **PennyPal AI Financial Assistant Chatbot:**
   - Interactive chatbot powered by Gemini API with real-time MySQL database context.
   - Answers questions regarding savings targets, affordability checks, and spending trends.
   - Includes suggested prompt pills and typing indicator.

9. **Interactive Charts & Analytics (Chart.js):**
   - Monthly Income vs Expense Bar Chart.
   - Expense Category Breakdown Doughnut Chart.
   - Budget vs Actual Spending Comparison.

---

## 🛠️ Technology Stack

- **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+), Chart.js, Font Awesome 6
- **Backend:** Python 3.13, Flask 3.0+, Flask-CORS, Werkzeug, python-dotenv
- **Database:** MySQL (Primary engine) with seamless SQLite fallback (`pennypal_ai.db`) for immediate out-of-the-box local testing
- **AI Engine:** Google Gemini API (`google-generativeai` & direct REST fallback)

---

## 📁 Project Structure

```text
PennyPal-AI/
│
├── app.py                      # Main Flask application entry point
├── config.py                   # Environment & app configuration
├── database.py                 # MySQL database connection manager & fallback
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment variables file
├── .env                        # Local environment variables file
├── README.md                   # Comprehensive project documentation
│
├── database/
│   └── schema.sql              # Complete MySQL database schema & indexes
│
├── services/
│   ├── gemini_service.py       # Google Gemini AI API integration & prompt engine
│   ├── financial_health.py     # Deterministic Financial Health Score engine
│   ├── spending_analysis.py    # Metric aggregation & MoM analysis service
│   └── budget_engine.py        # 50/30/20 budget recommendation engine
│
├── routes/
│   ├── auth.py                 # Login, signup, logout & demo data seeder
│   ├── transactions.py         # Transaction CRUD API endpoints
│   ├── analytics.py            # Dashboard metrics & Chart.js data endpoints
│   ├── budget.py               # Budget recommendation & management APIs
│   ├── goals.py                # Savings goals CRUD & add funds APIs
│   ├── investments.py          # Educational investment guidance APIs
│   ├── assistant.py            # AI Spending Analysis & Chatbot APIs
│   └── settings.py             # User profile, currency & password update APIs
│
├── templates/
│   ├── login.html              # Human-designed login page
│   ├── signup.html             # User registration page
│   └── dashboard.html          # Main interactive single-page dashboard
│
└── static/
    ├── css/
    │   └── style.css           # Modern professional financial dashboard styling
    └── js/
        ├── login.js            # Auth AJAX & validation script
        ├── dashboard.js        # Core dashboard controller & Chart.js integration
        └── assistant.js        # Interactive AI chatbot handler
```

---

## ⚙️ Installation & Setup Guide (Windows / VS Code)

### Prerequisites
- Python 3.9+ installed on Windows.
- MySQL Server / XAMPP (Optional: If MySQL is not running, the application automatically uses SQLite fallback so it works immediately out-of-the-box!).

### Step 1: Open Terminal in Project Folder
Open VS Code, press ``Ctrl + ` `` to open Terminal, and navigate to the project directory:
```powershell
cd "c:\Users\harsh\OneDrive\Desktop\New folder (6)"
```

### Step 2: Create & Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Database & Environment Variables
Copy `.env.example` to `.env` or edit `.env` in the root folder:
```ini
SECRET_KEY=pennypal_super_secret_key_2026
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=pennypal_ai
DB_PORT=3306
GEMINI_API_KEY=your_google_gemini_api_key_here
```

*(Note: If you have a Google Gemini API Key, paste it into `GEMINI_API_KEY`. If left blank, the application will use structured data-driven fallbacks for AI features without crashing!)*

### Step 5: Initialize MySQL Database (If MySQL is running)
Import `database/schema.sql` into MySQL:
```bash
mysql -u root -p < database/schema.sql
```
*(Or run `python database.py` which initializes the tables automatically).*

---

## 🚀 Running the Application

Start the Flask web server:
```powershell
python app.py
```

Open your browser and visit:
👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 🔑 Demo Evaluator Credentials

Click the **"Quick Demo Login"** button on the login screen or enter manually:
- **Email:** `demo@pennypal.ai`
- **Password:** `Demo@123`

*Logging in with Demo credentials automatically populates realistic sample income, expenses, category budgets, and savings goals.*

---

## 🔌 API Reference Overview

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/auth/register` | `POST` | Create new user account |
| `/api/auth/login` | `POST` | Authenticate user & start session |
| `/api/auth/logout` | `POST` | End active session |
| `/api/auth/me` | `GET` | Get current logged-in user profile |
| `/api/dashboard` | `GET` | Fetch overview balance cards & smart alerts |
| `/api/transactions` | `GET` / `POST` | Get filtered transactions or add new transaction |
| `/api/transactions/<id>` | `PUT` / `DELETE` | Update or delete existing transaction |
| `/api/analytics` | `GET` | Get datasets for Chart.js charts |
| `/api/financial-health` | `GET` | Get 0-100 Health Score calculation & AI explanation |
| `/api/budget/recommendations`| `GET` | Compute 50/30/20 AI budget allocations |
| `/api/budget/accept-recommendations`| `POST` | Bulk save recommended budgets to DB |
| `/api/goals` | `GET` / `POST` | Manage savings goals |
| `/api/goals/<id>/add-funds`| `POST` | Deposit money into specific savings goal |
| `/api/investments/analyze`| `POST` | Educational investment guidance engine |
| `/api/ai/spending-analysis`| `POST` | Gemini spending pattern analysis |
| `/api/ai/chat` | `POST` | PennyPal AI Assistant interactive chatbot |
| `/api/settings/profile` | `PUT` | Update profile, income & emergency fund |
| `/api/settings/change-password`| `POST` | Update user account password |

---

## 🎓 Project Verification Checklist

- [x] Full-stack architecture with Flask REST APIs and MySQL schema.
- [x] Secure password hashing and protection against User A / User B record leakage.
- [x] Google Gemini API integration strictly through backend services.
- [x] Human-designed, responsive, non-generic SaaS dashboard layout.
- [x] Zero hardcoded values; all metrics derived dynamically from database records.
- [x] End-to-end runnable locally on Windows via `python app.py`.
