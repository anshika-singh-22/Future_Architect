import sqlite3
from datetime import datetime

DATABASE_NAME = "data/roadmap_tracker.db"

def connect_db():
    """Connects to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def setup_database():
    """Creates the necessary tables if they don't exist."""
    with connect_db() as conn:
        cursor = conn.cursor()
        
        # 1. users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                goal TEXT,
                date_created TEXT
            )
        """)
        
        # 2. roadmap table (tasks/skills)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmap (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                skill TEXT NOT NULL,
                description TEXT,
                status INTEGER DEFAULT 0, -- 0: Pending, 1: Done
                deadline TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # 3. progress/streak table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                user_id INTEGER PRIMARY KEY,
                streak_days INTEGER DEFAULT 0,
                last_login TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()

# --- User Management Functions ---

def create_user(name, goal):
    """Creates a new user and initializes their progress/streak."""
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            date_created = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "INSERT INTO users (name, goal, date_created) VALUES (?, ?, ?)",
                (name, goal, date_created)
            )
            user_id = cursor.lastrowid
            
            # Initialize progress/streak
            cursor.execute(
                "INSERT INTO progress (user_id, last_login) VALUES (?, ?)",
                (user_id, date_created)
            )
            conn.commit()
            return user_id
    except sqlite3.IntegrityError:
        return None # User name already exists

def get_user_by_name(name):
    """Fetches user data by name."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, goal FROM users WHERE name = ?", (name,))
        return cursor.fetchone()

# --- Roadmap Task Management Functions ---

def add_task(user_id, skill, description, deadline=None):
    """Adds a new task to the roadmap."""
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO roadmap (user_id, skill, description, deadline) VALUES (?, ?, ?, ?)",
            (user_id, skill, description, deadline)
        )
        conn.commit()

def fetch_tasks(user_id):
    """Fetches all roadmap tasks for a user."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roadmap WHERE user_id = ?", (user_id,))
        return cursor.fetchall()

def update_task_status(task_id, status):
    """Marks a task as complete (1) or pending (0)."""
    with connect_db() as conn:
        conn.execute(
            "UPDATE roadmap SET status = ? WHERE id = ?",
            (status, task_id)
        )
        conn.commit()

def delete_task(task_id):
    """Deletes a task from the roadmap."""
    with connect_db() as conn:
        conn.execute("DELETE FROM roadmap WHERE id = ?", (task_id,))
        conn.commit()

# --- Progress and Streak Management Functions ---

def get_progress_data(user_id):
    """Fetches streak and last login data."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM progress WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

def update_streak(user_id):
    """Checks and updates the user's login streak."""
    today = datetime.now().strftime("%Y-%m-%d")
    progress_data = get_progress_data(user_id)
    
    if not progress_data:
        # User somehow doesn't have a progress record, initialize one
        with connect_db() as conn:
            conn.execute(
                "INSERT INTO progress (user_id, last_login) VALUES (?, ?)",
                (user_id, today)
            )
            conn.commit()
            return 1

    last_login_str = progress_data['last_login']
    current_streak = progress_data['streak_days']
    
    # Convert string to datetime object for comparison
    last_login_date = datetime.strptime(last_login_str, "%Y-%m-%d").date()
    today_date = datetime.now().date()
    
    # Calculate time difference in days
    delta = today_date - last_login_date
    
    new_streak = current_streak
    
    if delta.days == 1:
        # User logged in yesterday: streak continues
        new_streak += 1
    elif delta.days > 1:
        # User missed a day: streak broken
        new_streak = 1
    elif delta.days == 0:
        # User already logged in today: streak remains the same
        pass
    else:
        # Covers first-time login or unusual cases
        new_streak = 1
        
    # Update DB with new streak and today's login
    with connect_db() as conn:
        conn.execute(
            "UPDATE progress SET streak_days = ?, last_login = ? WHERE user_id = ?",
            (new_streak, today, user_id)
        )
        conn.commit()
        return new_streak