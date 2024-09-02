"""Main script to execute the application"""
#Importing modules
from packages.widget import CockpitWidget
from PyQt5.QtWidgets import QApplication
#Fixing imports
import sys

#Main function
def main():
    #Starting widget, which starts the server
    widget_app = QApplication(sys.argv)
    widget = CockpitWidget()
    widget.show()
    sys.exit(widget_app.exec_())

#Run app
if __name__ == "__main__":
    main()