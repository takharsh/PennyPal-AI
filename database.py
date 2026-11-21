import os
import sqlite3
import logging
import re
from config import Config

logger = logging.getLogger(__name__)

HAS_PYMYSQL = False
HAS_MYSQL_CONNECTOR = False

try:
    import pymysql
    import pymysql.cursors
    HAS_PYMYSQL = True
except ImportError:
    pass

try:
    import mysql.connector
    HAS_MYSQL_CONNECTOR = True
except ImportError:
    pass

DB_ENGINE = None

def get_db_connection():
    global DB_ENGINE
    
    # Try MySQL first
    if HAS_PYMYSQL or HAS_MYSQL_CONNECTOR:
        try:
            if HAS_PYMYSQL:
                conn = pymysql.connect(
                    host=Config.DB_HOST,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    port=Config.DB_PORT,
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True,
                    connect_timeout=3,
                    ssl={"ca": os.path.join(os.path.dirname(__file__), "isrgrootx1.pem")}
                )
                DB_ENGINE = 'mysql'
                return conn, 'mysql'
            elif HAS_MYSQL_CONNECTOR:
                conn = mysql.connector.connect(
                    host=Config.DB_HOST,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    port=Config.DB_PORT,
                    autocommit=True,
                    connection_timeout=3
                )
                DB_ENGINE = 'mysql'
                return conn, 'mysql_connector'
        except Exception as e:
            logger.warning(f"MySQL connection attempt failed ({e}). Using SQLite engine.")

    # SQLite fallback
    DB_ENGINE = 'sqlite'
    os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)
    sqlite_db_path = os.path.join(os.path.dirname(__file__), 'database', 'pennypal_ai.db')
    conn = sqlite3.connect(sqlite_db_path)
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'

def adapt_sql(sql, engine):
    """
    Adapts SQL syntax between MySQL (%s, AUTO_INCREMENT) and SQLite (?, AUTOINCREMENT).
    """
    if engine == 'sqlite':
        sql = sql.replace('%s', '?')
        sql = sql.replace('INT AUTO_INCREMENT PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
        sql = sql.replace('AUTO_INCREMENT', 'AUTOINCREMENT')
        sql = re.sub(r'ENGINE=InnoDB.*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'CHARACTER SET \w+ COLLATE \w+', '', sql, flags=re.IGNORECASE)
        sql = sql.replace('ON UPDATE CURRENT_TIMESTAMP', '')
        sql = re.sub(r"ENUM\([^)]+\)", "VARCHAR(50)", sql, flags=re.IGNORECASE)
        sql = sql.replace('UNIQUE KEY uq_user_category (user_id, category)', 'UNIQUE(user_id, category)')
    return sql

def execute_db(sql, params=()):
    conn, engine = get_db_connection()
    try:
        adapted_sql = adapt_sql(sql, engine)
        if engine == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute(adapted_sql, params)
                last_id = cursor.lastrowid
            conn.close()
            return last_id
        elif engine == 'mysql_connector':
            cursor = conn.cursor(dictionary=True)
            cursor.execute(adapted_sql, params)
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        else: # sqlite
            cursor = conn.cursor()
            cursor.execute(adapted_sql, params)
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
    except Exception as e:
        logger.error(f"Database execute error: {e}")
        try:
            conn.close()
        except Exception:
            pass
        raise e

def query_db(sql, params=(), one=False):
    conn, engine = get_db_connection()
    try:
        adapted_sql = adapt_sql(sql, engine)
        if engine == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute(adapted_sql, params)
                rv = cursor.fetchall()
            conn.close()
            return (rv[0] if rv else None) if one else rv
        elif engine == 'mysql_connector':
            cursor = conn.cursor(dictionary=True)
            cursor.execute(adapted_sql, params)
            rv = cursor.fetchall()
            conn.close()
            return (rv[0] if rv else None) if one else rv
        else: # sqlite
            cursor = conn.cursor()
            cursor.execute(adapted_sql, params)
            rv = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return (rv[0] if rv else None) if one else rv
    except Exception as e:
        logger.error(f"Database query error: {e}")
        try:
            conn.close()
        except Exception:
            pass
        raise e

def init_db():
    """Initializes schema for both MySQL and SQLite"""
    conn, engine = get_db_connection()
    
    if engine == 'sqlite':
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                currency VARCHAR(10) DEFAULT '₹',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT NOT NULL,
                type VARCHAR(20) NOT NULL,
                title VARCHAR(255) NOT NULL,
                amount DECIMAL(12, 2) NOT NULL,
                category VARCHAR(100) NOT NULL,
                description TEXT,
                transaction_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT NOT NULL,
                category VARCHAR(100) NOT NULL,
                monthly_limit DECIMAL(12, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, category),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT NOT NULL,
                goal_name VARCHAR(255) NOT NULL,
                target_amount DECIMAL(12, 2) NOT NULL,
                current_amount DECIMAL(12, 2) DEFAULT 0.00,
                target_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS financial_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT NOT NULL UNIQUE,
                monthly_income DECIMAL(12, 2) DEFAULT 0.00,
                risk_tolerance VARCHAR(50) DEFAULT 'Moderate',
                financial_goal VARCHAR(255) DEFAULT 'Wealth Accumulation',
                emergency_fund DECIMAL(12, 2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS ai_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT NOT NULL,
                insight_type VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS investment_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT NOT NULL,
                risk_level VARCHAR(50) NOT NULL,
                investment_goal VARCHAR(255) NOT NULL,
                investment_horizon VARCHAR(50) NOT NULL,
                amount DECIMAL(12, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        conn.commit()
        conn.close()
        print("Database schema initialized successfully (SQLite Engine).")
    else:
        schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            with conn.cursor() as cursor:
                for stmt in statements:
                    cursor.execute(stmt)
            conn.close()
            print("Database schema initialized successfully (MySQL Engine).")

if __name__ == '__main__':
    init_db()
