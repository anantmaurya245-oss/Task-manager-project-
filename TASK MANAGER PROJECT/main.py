import customtkinter as ctk
from gui.main_window import MainWindow  # FIXED: gui not gul
import os


def main():
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    # Initialize and run the application
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()