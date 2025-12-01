import database as db
from datetime import datetime, timedelta
import random
import time
import schedule
import threading
from dateutil import parser

# --- Core Logic Functions ---

def calculate_progress(user_id):
    """Calculates the percentage of completed tasks."""
    tasks = db.fetch_tasks(user_id)
    if not tasks:
        return 0.0, 0, 0
    
    total = len(tasks)
    done = sum(1 for task in tasks if task['status'] == 1)
    
    progress_percent = (done / total) * 100
    return progress_percent, done, total

def get_motivational_quote():
    """Returns a random motivational quote."""
    quotes = [
        "The best way to predict the future is to create it.",
        "Your goal is a magnet. Your efforts are the iron filings.",
        "Every step you take is a step towards your goal.",
        "Discipline is the bridge between goals and accomplishment.",
        "A little progress each day adds up to big results.",
        "Consistency is the magic bullet."
    ]
    return random.choice(quotes)

# --- Streak Handling ---

def on_login_check_streak(user_id):
    """Updates the streak and returns the new value."""
    new_streak = db.update_streak(user_id)
    quote = get_motivational_quote()
    
    message = f"Welcome back, tracker! Your current streak is **{new_streak} days**."
    if new_streak > 1:
        message += "\nKeep going, you're building a great habit!"
    
    return message, quote, new_streak

# --- Advanced Scheduling and Reminders (THREADED) ---

# Global variable to hold the reminder callback function from UI
reminder_display_callback = None 

def set_reminder_display_callback(callback):
    """Sets the UI function to call when a reminder is due."""
    global reminder_display_callback
    reminder_display_callback = callback

def reminder_job(user_id):
    """Function to be called by the scheduler."""
    user = db.get_user_by_name(db.get_progress_data(user_id)['user_id'])
    
    if user:
        quote = get_motivational_quote()
        title = f"Daily Roadmap Reminder for {user['name']}"
        message = f"Goal: {user['goal']}\nMotivation: '{quote}'\n\nDon't forget to track your progress today!"
        
        # Use the stored UI callback to show the reminder notification
        if reminder_display_callback:
            reminder_display_callback(title, message)
        
        print(f"Reminder sent for {user['name']} via background thread.")
        
def run_scheduler_thread():
    """Runs the scheduler in a separate thread."""
    while True:
        schedule.run_pending()
        time.sleep(1) # Check every second

def start_reminder_service(user_id, user_name, time_str="10:00"):
    """Initializes the reminder job and starts the background thread."""
    
    # Clear old job for this user/id if it exists
    schedule.clear(str(user_id)) 
    
    # Setup the job (time_str should be configurable in the UI)
    schedule.every().day.at(time_str).do(reminder_job, user_id).tag(str(user_id))
    print(f"Daily reminder set for {user_name} at {time_str}.")

    # Start the thread only if it's not running
    thread_name = 'SchedulerThread'
    if not any(t.name == thread_name for t in threading.enumerate()):
        t = threading.Thread(target=run_scheduler_thread, name=thread_name, daemon=True)
        t.start()
        print("Reminder scheduler thread started.")


# --- Roadmap Import and Day-Wise Planning ---

def process_imported_roadmap(user_id, content, overall_deadline_str):
    """
    Parses imported text content and distributes tasks up to a given deadline.
    """
    
    # 1. Determine the overall deadline
    try:
        deadline_date = parser.parse(overall_deadline_str).date()
    except Exception:
        raise ValueError("Invalid deadline format. Please use YYYY-MM-DD.")

    # 2. Simple Task Extraction (assuming one task per line or section)
    task_list = [line.strip() for line in content.split('\n') if line.strip()]
    
    if not task_list:
        return 0
        
    num_tasks = len(task_list)
    today = datetime.now().date()
    
    # Calculate total working days in the period
    days_left = (deadline_date - today).days
    
    if days_left <= 0:
        raise ValueError("Deadline must be in the future.")

    # Calculate how many days to space out between tasks
    task_spacing = days_left / num_tasks 

    for i, task_name in enumerate(task_list):
        # Assign a deadline for this specific task
        task_deadline = today + timedelta(days=int((i + 1) * task_spacing))
        
        # Ensure task deadline doesn't exceed the overall deadline
        if task_deadline > deadline_date:
             task_deadline = deadline_date
        
        db.add_task(user_id, task_name, "Scheduled from imported roadmap.", task_deadline.strftime("%Y-%m-%d"))

    return num_tasks

# --- Badges/Rewards (Logic) ---

def check_for_rewards(user_id, streak_days, progress_percent):
    """Checks for badge milestones."""
    rewards = []
    
    # Milestone Rewards
    if progress_percent >= 100.0:
        rewards.append("🎉 Roadmap Completed! Congratulations!")
        
    if 50.0 <= progress_percent < 51.0:
        rewards.append("🏆 Halfway There! (50% Milestone)")
        
    if 25.0 <= progress_percent < 26.0:
        rewards.append("🌟 Quarter Goal Achieved! (25% Milestone)")
        
    # Streak Rewards
    if streak_days >= 7 and streak_days % 7 == 0:
        rewards.append(f"🔥 {streak_days}-Day Streak Master!")
    
    return rewards