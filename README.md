Student Roadmap Tracker
The Student Roadmap Tracker is a cross-platform desktop application designed to help students and self-learners bridge the gap between their career goals and daily learning tasks.

Built in Python using the PyQt5 framework for a clean GUI and SQLite3 for robust local data storage, this tool provides a structured environment for personalized skill development.

✨ Key Features
Goal Setting: Users define a specific career aspiration (e.g., "Data Scientist," "Full-Stack Developer").

Custom Roadmaps: Create or import detailed roadmaps listing required skills, courses, and projects with deadlines.

Progress Tracking: Mark tasks as complete and visualize overall progress with embedded Matplotlib charts.

Streak & Motivation System: Encourages consistency with daily login streaks, motivational reminders, and badge rewards (e.g., "5-Day Streak").

Local Persistence: All roadmaps and progress are securely stored in a local SQLite database, ensuring privacy and offline access.

🛠️ Technology Stack
Component,Tool / Library,Purpose
Frontend/GUI,PyQt5 (or Tkinter),"Interactive desktop interface for Windows, macOS, and Linux."
Database,SQLite3,"Lightweight, file-based persistence for user data and roadmaps."
Visualization,Matplotlib,Generates clear pie/bar charts to show completion percentage.
Logic/Scheduling,schedule / datetime,Handles reminders and streak calculation logic.
Deployment,PyInstaller,Optional packaging into a standalone executable.
