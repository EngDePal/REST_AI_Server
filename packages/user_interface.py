#Importing the PyQt5 GUI framework and other modules
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QTableWidget
from PyQt5.QtGui import QFont
import sys

class UserInterface(QWidget):

    #Creates the base layout
    def __init__(self):
        super().__init__()

        #Application window setup
        self.setWindowTitle("Telepath RemoteMind")
        self.setGeometry(100, 100, 1000, 700)

        #Stylish App Name
        prefix_font = QFont()
        prefix_font.setPointSize(40)
        prefix_font.setBold(True)

        self.prefix_label = QLabel("Telepath", self)
        self.prefix_label.setStyleSheet("color : purple; font : Lucida Console" )
        self.prefix_label.setFont(prefix_font)
        self.prefix_label.move(750,50)

        suffix_font = QFont()
        suffix_font.setPointSize(22)
        suffix_font.setItalic(True)
        suffix_font.setBold(True)
        suffix_font.setFamily("Calibri")

        self.suffix_label = QLabel("RemoteMind", self)
        self.suffix_label.setStyleSheet("color : dark grey;")
        self.suffix_label.setFont(suffix_font)
        self.suffix_label.move(800,30)


        #Operations section: Control server, load plugins
        self.operations_label = QLabel("Operations", self)
        self.operations_label.setGeometry(100, 50, 150, 50)

        #Start server button
        self.start_button = QPushButton("Start server", self)
        self.start_button.clicked.connect(self.click_on_start)
        self.start_button.setFixedSize(150,50)
        self.start_button.move(100, 100)

        #Stop server button
        self.shutdown_button = QPushButton("Shutdown server", self)
        self.shutdown_button.clicked.connect(self.click_on_shutdown)
        self.shutdown_button.setFixedSize(150,50)
        self.shutdown_button.move(300, 100)

        #Login control box
        self.login_box = QTextEdit(self)
        self.login_box.setReadOnly(True)
        self.login_box.setGeometry(100, 160, 350, 200)

        #Plugin DropDown list, label and button
        self.plugin_label = QLabel("Available Plug-Ins", self)
        self.plugin_label.setGeometry(100, 360, 150, 50)

        self.plugin_list = QComboBox(self)
        self.plugin_list.setGeometry(250, 360, 200, 50)

        self.load_button = QPushButton("Load", self)
        self.load_button.clicked.connect(self.click_on_load)
        self.load_button.setGeometry(250, 400, 200, 50)

        #Cockpit section: Check clients
        self.cockpit_label = QLabel("Cockpit", self)
        self.cockpit_label.setGeometry(500, 50, 150, 50)

        #Table of registered clients
        self.table_label = QLabel("Active Clients", self)
        self.table_label.setGeometry(500, 100, 300, 50)

        #Client is represented by the token
        #Additionaly shows the plugin and the last command type plus its confirmations status
        self.client_table = QTableWidget(self)
        self.column_headers = ["No.", "Client", "Plugin", "Status"]
        self.client_table.setColumnCount(len(self.column_headers))
        self.client_table.setHorizontalHeaderLabels(self.column_headers)
        self.client_table.setGeometry(500, 150, 400, 300)

        #Access section: MongoDB queries
        self.access_label = QLabel("Access", self)
        self.access_label.setGeometry(100, 470, 150, 50)

        #User input for the query
        self.query_input = QLineEdit("Please provide input in JSON format!", self)
        self.query_input.setGeometry(100, 520, 300, 100)

        self.query_output = QLineEdit(self)
        self.query_output.setGeometry(600, 520, 300, 100)

        #Start button for query
        self.query_button =QPushButton("MongoDB query", self)
        self.query_button.clicked.connect(self.click__on_query)
        self.query_button.setGeometry(425, 550, 150, 50)


    #Handling of logic and user inputs


    def click_on_start(self):
        pass

    def click_on_shutdown(self):
        pass

    def update_login_control(self):
        pass

    def update_dropdown(self):
        pass

    def click_on_load(self):
        pass

    def update_table(self):
        pass

    def click__on_query(self):
        pass

    def query_result(self):
        pass

def main():
    app = QApplication(sys.argv)
    gui = UserInterface()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()