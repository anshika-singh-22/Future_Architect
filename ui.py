import sys
import os 
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QProgressBar, QMessageBox, 
    QFileDialog, QInputDialog, QStyleFactory
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor
import database as db
import logic
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pypdf

# --- THEME DEFINITION (QStyleSheet - QSS) ---
STUDENT_THEME_QSS = """
    /* General Window Background */
    QMainWindow, QWidget {
        background-color: #F5F5F5; 
        color: #333333;
    }

    /* Main Title and Headers */
    QLabel#TitleLabel {
        font-size: 32px;
        font-weight: bold;
        color: #4CAF50; /* Green Primary */
        padding: 20px;
    }
    QLabel {
        font-size: 14px;
    }

    /* Input Fields */
    QLineEdit {
        background-color: white;
        border: 1px solid #CCCCCC;
        border-radius: 8px; 
        padding: 10px;
        font-size: 16px;
        min-height: 30px;
        selection-background-color: #2196F3;
    }
    QLineEdit:focus {
        border: 2px solid #2196F3; 
    }

    /* Primary Buttons (Login, Create, Add, Import) */
    QPushButton {
        background-color: #2196F3; 
        color: white;
        border: none;
        border-radius: 15px; 
        padding: 12px 25px;
        font-size: 16px;
        font-weight: 500;
        margin-top: 10px;
        min-height: 20px;
    }
    QPushButton:hover {
        background-color: #1976D2; 
    }
    QPushButton:pressed {
        background-color: #0D47A1;
    }

    /* Table Widget - Roadmap */
    QTableWidget {
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        gridline-color: #E0E0E0;
        padding: 5px;
        font-size: 13px;
    }
    QHeaderView::section {
        background-color: #F0F0F0;
        color: #555555;
        padding: 8px;
        border-bottom: 2px solid #4CAF50; 
        font-weight: bold;
    }

    /* Progress Bar */
    QProgressBar {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        text-align: center;
        background-color: #E0E0E0;
        color: #333333;
        font-weight: bold;
        min-height: 25px;
    }
    QProgressBar::chunk {
        background-color: #4CAF50; 
        border-radius: 8px;
        margin: 1px;
    }

    /* Status Labels and Indicators */
    QLabel#StreakLabel {
        color: #FF5722; 
        font-weight: bold;
    }
    QLabel#GoalLabel {
        color: #4CAF50;
        font-weight: bold;
    }
    QLabel#RewardLabel {
        background-color: #FFFDE7; 
        border: 1px solid #FFEB3B;
        border-radius: 5px;
        padding: 5px;
    }
    
    /* Small Buttons in Table (Toggle/Delete) */
    QWidget > QPushButton {
        background-color: #9E9E9E;
        color: white;
        border-radius: 5px;
        padding: 5px 8px;
        font-size: 12px;
        min-height: unset;
        margin: 0px;
    }
    QWidget > QPushButton:hover {
        background-color: #757575;
    }
"""

# --- Custom Widgets ---

class ProgressChart(QWidget):
    """Widget to display progress chart using Matplotlib."""
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.layout = QVBoxLayout(self)
        
        plt.style.use('default') 
        self.figure, self.ax = plt.subplots(figsize=(4, 4)) 
        self.figure.patch.set_facecolor('#F5F5F5')
        self.ax.set_facecolor('#FFFFFF')
        
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.update_chart()

    def update_chart(self):
        self.ax.clear()
        
        progress, done, total = logic.calculate_progress(self.user_id)
        
        if total == 0:
            self.ax.text(0.5, 0.5, "No tasks added yet!", ha='center', va='center', fontsize=12, color='#777777')
        else:
            labels = 'Completed', 'Pending'
            sizes = [done, total - done]
            colors = ['#4CAF50', '#FF9800']
            explode = (0.05, 0) 
            
            self.ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', 
                        startangle=90, colors=colors, textprops={'color': '#333333'})
            self.ax.axis('equal')  
            self.ax.set_title(f"Roadmap Progress ({done}/{total})", color='#333333', fontsize=14)

        self.figure.tight_layout()
        self.canvas.draw()

# --- Main Screens ---

class LoginScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Title
        title_label = QLabel("Student Roadmap Tracker")
        title_label.setObjectName("TitleLabel")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Input Fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("🧑‍🎓 Enter your Name")
        self.name_input.setMaximumWidth(400)
        layout.addWidget(self.name_input, alignment=Qt.AlignCenter)

        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("🚀 What's your Career Goal?")
        self.goal_input.setMaximumWidth(400)
        layout.addWidget(self.goal_input, alignment=Qt.AlignCenter)
        
        # Buttons
        self.login_btn = QPushButton("🔑 Login")
        self.login_btn.clicked.connect(self.handle_login)
        self.login_btn.setMaximumWidth(400)
        layout.addWidget(self.login_btn, alignment=Qt.AlignCenter)

        self.create_btn = QPushButton("📝 Create Profile")
        self.create_btn.clicked.connect(self.handle_create_profile)
        self.create_btn.setMaximumWidth(400)
        layout.addWidget(self.create_btn, alignment=Qt.AlignCenter)
        
        # Spacer
        layout.addSpacing(50)
        info_label = QLabel("Use a unique name to track your progress.")
        info_label.setStyleSheet("color: #777777; font-style: italic;")
        layout.addWidget(info_label, alignment=Qt.AlignCenter)
        
    def handle_login(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter your name.")
            return

        user_data = db.get_user_by_name(name)
        if user_data:
            self.main_window.current_user_id = user_data['id']
            self.main_window.current_user_name = user_data['name']
            self.main_window.current_user_goal = user_data['goal']
            self.main_window.switch_to_dashboard()
        else:
            QMessageBox.warning(self, "Error", "User not found. Please create a profile.")

    def handle_create_profile(self):
        name = self.name_input.text().strip()
        goal = self.goal_input.text().strip()
        
        if not name or not goal:
            QMessageBox.warning(self, "Error", "Name and Goal are required to create a profile.")
            return

        user_id = db.create_user(name, goal)
        if user_id:
            QMessageBox.information(self, "Success", f"Profile for {name} created successfully!")
            self.main_window.current_user_id = user_id
            self.main_window.current_user_name = name
            self.main_window.current_user_goal = goal
            self.main_window.switch_to_dashboard()
        else:
            QMessageBox.warning(self, "Error", "Profile creation failed. Name might already be taken.")


class DashboardScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Top Info Bar (Goal, Streak, Logout)
        top_layout = QHBoxLayout()
        
        self.goal_label = QLabel("Goal: ")
        self.goal_label.setObjectName("GoalLabel")
        top_layout.addWidget(self.goal_label)

        top_layout.addSpacing(20)

        self.streak_label = QLabel("🔥 Streak: 0 days")
        self.streak_label.setObjectName("StreakLabel")
        top_layout.addWidget(self.streak_label)
        
        top_layout.addStretch(1) 

        self.logout_btn = QPushButton("🚪 Logout")
        self.logout_btn.clicked.connect(self.main_window.switch_to_login)
        self.logout_btn.setStyleSheet("QPushButton { background-color: #E0E0E0; color: #333333; border: 1px solid #777777; padding: 5px 15px; border-radius: 10px; } QPushButton:hover { background-color: #CCCCCC; }")
        top_layout.addWidget(self.logout_btn)
        
        main_layout.addLayout(top_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        # Content Area (Table + Chart/Actions)
        content_layout = QHBoxLayout()
        
        # Left Side: Roadmap Table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels(["ID", "Skill/Task", "Deadline", "Status", "Actions"])
        self.task_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.task_table.setColumnHidden(0, True) 
        self.task_table.verticalHeader().setVisible(False)
        content_layout.addWidget(self.task_table, 2) 

        # Right Side: Chart and Add/Import Task Buttons
        right_layout = QVBoxLayout()
        
        # Chart placeholder
        self.chart_widget = ProgressChart(self.main_window.current_user_id or 0)
        right_layout.addWidget(self.chart_widget)

        # Action Buttons
        button_layout = QVBoxLayout()
        
        self.add_task_btn = QPushButton("➕ Add Single Task")
        self.add_task_btn.clicked.connect(self.show_add_task_popup)
        button_layout.addWidget(self.add_task_btn)

        self.import_btn = QPushButton("📄 Import & Plan Roadmap")
        self.import_btn.clicked.connect(self.handle_import_roadmap)
        button_layout.addWidget(self.import_btn)

        right_layout.addLayout(button_layout)
        
        self.reward_label = QLabel("")
        self.reward_label.setObjectName("RewardLabel")
        right_layout.addWidget(self.reward_label)

        right_layout.addStretch(1)
        content_layout.addLayout(right_layout, 1)
        
        main_layout.addLayout(content_layout)

    def update_dashboard(self):
        """Called on login and after every task update."""
        user_id = self.main_window.current_user_id
        
        self.goal_label.setText(f"Goal: {self.main_window.current_user_goal}")
        
        # Streak logic: Check streak, get motivational quote
        login_message, quote, streak = logic.on_login_check_streak(user_id)
        self.streak_label.setText(f"🔥 Streak: {streak} days")
        
        if self.main_window.central_widget.currentWidget() != self:
             self.show_motivational_popup(login_message, quote)

        # 2. Update Progress Bar and Chart
        progress, done, total = logic.calculate_progress(user_id)
        self.progress_bar.setMaximum(total if total > 0 else 1)
        self.progress_bar.setValue(done)
        self.progress_bar.setFormat(f"Progress: %p% ({done}/{total} tasks)")

        self.chart_widget.user_id = user_id
        self.chart_widget.update_chart()
        
        # 3. Update Rewards (Passive Display)
        rewards = logic.check_for_rewards(user_id, streak, progress)
        self.reward_label.setText("🎖️ Active Rewards:\n" + "\n".join(rewards) if rewards else "")

        # 4. Populate Task Table
        self.populate_task_table(user_id)

        # 5. Start Reminders (using a fixed time for now)
        logic.start_reminder_service(user_id, self.main_window.current_user_name, "10:00")


    def populate_task_table(self, user_id):
        tasks = db.fetch_tasks(user_id)
        self.task_table.setRowCount(len(tasks))
        
        for row_index, task in enumerate(tasks):
            # Determine the alternating background color for the row
            row_color = QColor(255, 255, 255) # White (Even rows)
            if row_index % 2 != 0:
                row_color = QColor(248, 248, 248) # Light Gray (Odd rows)

            # 1. ID (Hidden)
            id_item = QTableWidgetItem(str(task['id']))
            id_item.setBackground(row_color)
            self.task_table.setItem(row_index, 0, id_item)
            
            # 2. Skill/Task
            skill_item = QTableWidgetItem(task['skill'])
            skill_item.setBackground(row_color)
            self.task_table.setItem(row_index, 1, skill_item)

            # 3. Deadline (Check for overdue tasks)
            deadline_str = task['deadline'] if task['deadline'] else "-"
            deadline_item = QTableWidgetItem(deadline_str)
            deadline_item.setBackground(row_color)
            
            if deadline_str != "-":
                from datetime import date
                try:
                    task_date = date.fromisoformat(deadline_str)
                    if task_date < date.today() and task['status'] == 0:
                        # Override color for overdue tasks only (Foreground/Font)
                        deadline_item.setForeground(Qt.red)
                        deadline_item.setFont(QFont('Arial', 10, QFont.Bold))
                except ValueError:
                    pass 
                    
            self.task_table.setItem(row_index, 2, deadline_item)
            
            # 4. Status
            status_text = "✅ Done" if task['status'] == 1 else "⏳ Pending"
            status_item = QTableWidgetItem(status_text)
            status_item.setBackground(row_color) # Apply row color
            self.task_table.setItem(row_index, 3, status_item)

            # Apply visual style for done tasks
            if task['status'] == 1:
                 skill_item.setForeground(Qt.darkGray)
                 skill_item.setFont(QFont('Arial', 10, QFont.StyleItalic))
                 
            # 5. Actions (Button) - Note: setCellWidget handles styling for the action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            toggle_btn = QPushButton("Mark Done" if task['status'] == 0 else "Mark Pending")
            toggle_btn.setFixedSize(100, 25)
            toggle_btn.clicked.connect(lambda checked, t_id=task['id'], current_status=task['status']: self.toggle_task_status(t_id, current_status))
            
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setFixedSize(80, 25)
            delete_btn.setStyleSheet("QPushButton { background-color: #FF5722; } QPushButton:hover { background-color: #E64A19; }")
            delete_btn.clicked.connect(lambda checked, t_id=task['id'], t_skill=task['skill']: self.delete_task_item(t_id, t_skill))

            action_layout.addWidget(toggle_btn)
            action_layout.addWidget(delete_btn)
            self.task_table.setCellWidget(row_index, 4, action_widget)


    def toggle_task_status(self, task_id, current_status):
        new_status = 1 if current_status == 0 else 0
        db.update_task_status(task_id, new_status)
        
        if new_status == 1:
            progress, done, total = logic.calculate_progress(self.main_window.current_user_id)
            streak_data = db.get_progress_data(self.main_window.current_user_id)
            current_streak = streak_data['streak_days'] if streak_data else 0

            rewards = logic.check_for_rewards(self.main_window.current_user_id, current_streak, progress)
            
            if rewards:
                QMessageBox.information(self, "✨ Reward Unlocked! ✨", 
                                        "\n".join(rewards) + "\n\nCongratulations on your achievement!")
            
        self.update_dashboard()
        
    def delete_task_item(self, task_id, task_skill):
        reply = QMessageBox.question(self, 'Delete Task', 
                                     f"Are you sure you want to delete '{task_skill}'?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            db.delete_task(task_id)
            self.update_dashboard()

    def show_add_task_popup(self):
        popup = AddTaskPopup(self.main_window.current_user_id, self.update_dashboard)
        popup.exec_()
        
    def handle_import_roadmap(self):
        # 1. Get overall deadline from user
        overall_deadline, ok = QInputDialog.getText(self, 'Set Roadmap Deadline', 
                                                    'Enter the overall deadline (YYYY-MM-DD):', 
                                                    QLineEdit.Normal)
        if not ok or not overall_deadline:
            return

        # 2. Open file dialog for selection
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Roadmap File", "", 
                                                  "Text Files (*.txt);;PDF Files (*.pdf)")
        if not filePath:
            return

        content = ""
        try:
            if filePath.lower().endswith('.txt'):
                with open(filePath, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif filePath.lower().endswith('.pdf'):
                with open(filePath, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    full_text = []
                    for page in reader.pages:
                        full_text.append(page.extract_text())
                    content = "\n".join(full_text)
            
            # 3. Process and schedule
            num_tasks = logic.process_imported_roadmap(self.main_window.current_user_id, content, overall_deadline)
            QMessageBox.information(self, "Success", f"{num_tasks} tasks imported and scheduled day-wise until {overall_deadline}!")
            self.update_dashboard() 
            
        except ValueError as ve:
            QMessageBox.critical(self, "Scheduling Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Failed to read or process file: {e}")

    def show_motivational_popup(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(title)
        msg.setInformativeText(f"**Quote of the Day**\n'{message}'")
        msg.setWindowTitle("Login Status & Motivation")
        msg.setStyleSheet("QMessageBox { background-color: #FFFFFF; }")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_reminder_popup(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(title)
        msg.setInformativeText(message)
        msg.setWindowTitle("Roadmap Reminder")
        msg.setStyleSheet("QMessageBox { background-color: #FFF3E0; }")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


class AddTaskPopup(QMessageBox):
    """Simple modal popup to add a new task."""
    def __init__(self, user_id, refresh_callback):
        super().__init__()
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.setWindowTitle("Add New Roadmap Task")
        self.setStyleSheet(STUDENT_THEME_QSS) 
        
        # Setup input widgets
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Skill/Task Name (e.g., Complete Python Module 3)")
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (Optional)")
        
        self.deadline_input = QLineEdit()
        self.deadline_input.setPlaceholderText("Deadline (YYYY-MM-DD) (Optional)")
        
        # Create a custom widget to hold the inputs
        input_widget = QWidget()
        vbox = QVBoxLayout(input_widget)
        vbox.addWidget(QLabel("Task Name:"))
        vbox.addWidget(self.task_input)
        vbox.addWidget(QLabel("Description:"))
        vbox.addWidget(self.desc_input)
        vbox.addWidget(QLabel("Deadline:"))
        vbox.addWidget(self.deadline_input)
        
        # Replace default content of QMessageBox with custom widget
        layout = self.layout()
        for i in reversed(range(layout.count())): 
            widget = layout.itemAt(i).widget()
            if widget is not None: 
                widget.setParent(None)

        # Add the custom widget
        layout.addWidget(input_widget)
        
        save_button = QPushButton("💾 Save Task")
        save_button.clicked.connect(lambda: self.done(QMessageBox.Save))
        
        cancel_button = QPushButton("❌ Cancel")
        cancel_button.clicked.connect(lambda: self.done(QMessageBox.Cancel))
        
        # Manually add the buttons to the layout
        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(save_button)
        h_layout.addWidget(cancel_button)
        layout.addLayout(h_layout)
        
        self.setStandardButtons(QMessageBox.NoButton)

    def exec_(self):
        result = super().exec_()
        if result == QMessageBox.Save:
            task_name = self.task_input.text().strip()
            task_desc = self.desc_input.text().strip()
            task_deadline = self.deadline_input.text().strip()
            
            if task_name:
                db.add_task(self.user_id, task_name, task_desc, task_deadline if task_deadline else None)
                self.refresh_callback() 
                QMessageBox.information(self, "Success", f"Task '{task_name}' added!")
            else:
                QMessageBox.warning(self, "Error", "Task name cannot be empty.")
        
        return result

# --- Main Application Window ---

class MainApplication(QMainWindow):
    def __init__(self, application_instance): 
        super().__init__()
        
        self.app = application_instance 
        
        self.setWindowTitle("Student Roadmap Tracker")
        self.setGeometry(100, 100, 1000, 700)
        
        self.app.setStyleSheet(STUDENT_THEME_QSS) 
        
        if os.path.exists("assets/icon.png"):
             self.setWindowIcon(QIcon("assets/icon.png")) 
        
        self.current_user_id = None
        self.current_user_name = None
        self.current_user_goal = None

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.login_screen = LoginScreen(self)
        self.dashboard_screen = DashboardScreen(self)
        
        self.central_widget.addWidget(self.login_screen)
        self.central_widget.addWidget(self.dashboard_screen)
        
        logic.set_reminder_display_callback(self.dashboard_screen.show_reminder_popup)

        self.switch_to_login()
        
    def switch_to_login(self):
        self.central_widget.setCurrentWidget(self.login_screen)
        
    def switch_to_dashboard(self):
        if self.current_user_id is not None:
            self.dashboard_screen.update_dashboard()
            self.central_widget.setCurrentWidget(self.dashboard_screen)
        else:
            self.switch_to_login()