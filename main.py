"""Main script to execute the application"""
#Importing modules
from packages.user_interface import UserInterface
from PyQt5.QtWidgets import QApplication
#Fixing imports
import sys
import os


#Main function
def main():
    #Running GUI in main thread
    run_gui()


#Define start-up functions

def run_gui():
    gui_app = QApplication(sys.argv)
    gui = UserInterface()
    gui.show()
    sys.exit(gui_app.exec_())

#Run app
if __name__ == "__main__":
    main()