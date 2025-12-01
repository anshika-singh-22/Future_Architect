import sys
import os
# FIX: Import QMessageBox to use it in error handling
from PyQt5.QtWidgets import QApplication, QMessageBox 
import database as db
from ui import MainApplication

def main():
    # 1. Project Setup (ensure folders and DB exist)
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # 2. Initialize Database
    db.setup_database()

    # 3. Launch GUI
    app = QApplication(sys.argv)
    
    try:
        # FIX: Pass the 'app' instance to the MainApplication constructor
        window = MainApplication(app) 
        window.show()
        
        # 4. Start Application Event Loop
        sys.exit(app.exec_())
    except Exception as e:
        # This error handler is useful if PyQt5 fails to load or another critical error occurs early
        QMessageBox.critical(None, "Fatal Error", f"Application failed to start.\nDetails: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()