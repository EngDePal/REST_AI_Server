"""GUI for the REST AI Server"""
#NOT FUNCTIONAL
#Importing the PyQt5 GUI framework and other modules
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QComboBox, QTableWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
import sys

class UserInterface(QWidget):

    #Starting 
    def __init__(self):

        #Setting up GUI
        super().__init__()
        self.design_interface()


    #Methods handling logic and user inputs

    #Sets an update timer for all relevant UI elements
    def update_GUI(self):

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_counter)
        self.timer.start(5000)

    #Starting the server with the green start button
    def click_on_start(self):

        #Creating server instance
        self.server = Server()
        
        #Start server
        self.server.start_server()

        #Starting GUI updates
        self.update_GUI()
    
    #Not working ATM
    #Shutdown the server with the red shutdown button
    def click_on_shutdown(self):
        pass

    def update_login_control(self):
        pass
    
    def click_on_load(self):
        pass
    
    #Updates the amount of active clients
    def update_counter(self):
        counter = self.server.get_client_count()
        self.counter_label.setText(counter)

    def update_table(self):
        pass

    def click__on_query(self):
        pass

    def query_result(self):
        pass

    #Defines all interface elements
    def design_interface(self):
        #Application window setup
            self.setWindowTitle("RemoteMind Telepath")
            self.setStyleSheet("background-color: white")
            self.setGeometry(100, 100, 1000, 700)

            #Stylish App Name
            prefix_font = QFont()
            prefix_font.setPointSize(40)
            prefix_font.setBold(True)

            self.prefix_label = QLabel("Telepath", self)
            self.prefix_label.setStyleSheet("color : purple; font : Lucida" )
            self.prefix_label.setFont(prefix_font)
            self.prefix_label.move(750,50)

            suffix_font = QFont()
            suffix_font.setPointSize(22)
            suffix_font.setItalic(True)
            suffix_font.setBold(True)
            suffix_font.setFamily("Arial")

            self.suffix_label = QLabel("RemoteMind", self)
            self.suffix_label.setStyleSheet("color : dark grey;")
            self.suffix_label.setFont(suffix_font)
            self.suffix_label.move(800,30)

            #Defining some general fonts
            self.button_font = QFont()
            self.button_font.setFamily("Arial")
            self.button_font.setPointSize(14)

            #Defining some general style sheets
            generic_button_style = """QPushButton {
                    border: 3px solid black;
                    color: solid black;
                    background-color: white;
                    font-weight: normal;
                    border-radius: 7px
                }
                QPushButton:hover {
                    font-weight: bold;
                }
            """

            generic_textbox_style = """
                QTextEdit {
                    border: 2px solid grey;
                    border-radius: 7px;         
                    font-family: Courier New;          
                    font-size: 12px;   
                }
            """

            #The UI consists of three sections
            #Setting one font for all section titles
            self.section_font = QFont()
            self.section_font.setBold(True)
            self.section_font.setFamily("Arial")
            self.section_font.setPointSize(20)

            #Operations section: Control server, load plugins
            self.operations_label = QLabel("Operations", self)
            self.operations_label.setGeometry(100, 50, 150, 50)
            self.operations_label.setFont(self.section_font)

            #Start server button
            self.start_button = QPushButton("Start Server", self)
            self.start_button.clicked.connect(self.click_on_start)
            self.start_button.setFixedSize(150,50)
            self.start_button.move(100, 100)
            self.start_button.setFont(self.button_font)
            self.start_button.setStyleSheet("""
                QPushButton {
                    border: 3px solid green;
                    color: black;
                    background-color: white;
                    border-radius : 7px;
                }
                QPushButton:hover {
                    border: 3px solid green;
                    color: green;
                }
            """)

            #Stop server button
            self.shutdown_button = QPushButton("Shutdown Server", self)
            self.shutdown_button.clicked.connect(self.click_on_shutdown)
            self.shutdown_button.setFixedSize(150,50)
            self.shutdown_button.move(300, 100)
            self.shutdown_button.setFont(self.button_font)
            self.shutdown_button.setStyleSheet("""
                QPushButton {
                    border: 3px solid darkred;
                    color: black;
                    background-color: white;
                    border-radius : 7px;
                }
                QPushButton:hover {
                    border: 3px solid darkred;
                    color: darkred;
                }
            """)

            #Login control box
            self.login_box = QTextEdit("Awaiting new client login...", self)
            self.login_box.setReadOnly(True)
            self.login_box.setGeometry(100, 160, 350, 200)
            self.login_box.setStyleSheet(generic_textbox_style)
            self.login_box.setReadOnly(True)

            #Plugin DropDown list, label and button
            self.plugin_font = QFont()
            self.plugin_font.setPointSize(14)
            self.plugin_font.setFamily("Arial")

            self.plugin_label = QLabel("Available Plug-Ins", self)
            self.plugin_label.setGeometry(100, 370, 150, 50)
            self.plugin_label.setFont(self.plugin_font)

            self.plugin_list = QComboBox(self)
            self.plugin_list.setGeometry(250, 370, 200, 50)
            self.plugin_list.addItems(["select"])
            self.plugin_list.setCurrentIndex(0)
            self.plugin_list.setStyleSheet("""
                QComboBox {
                    border: 3px solid black;  
                    border-radius: 7px;          
                    font-family: Arial;      
                    font-size: 14px;
                    background-color: lightblue    
                }
                QComboBox::drop-down {
                    width: 20px;
                    height: 20px;
                    subcontrol-position: center right;                                                
                }
            """)

            self.load_button = QPushButton("Load", self)
            self.load_button.clicked.connect(self.click_on_load)
            self.load_button.setGeometry(250, 430, 200, 50)
            self.load_button.setFont(self.button_font)
            self.load_button.setStyleSheet(generic_button_style)

            #Cockpit section: Check clients
            self.cockpit_label = QLabel("Cockpit", self)
            self.cockpit_label.setGeometry(500, 50, 150, 50)
            self.cockpit_label.setFont(self.section_font)

            #Number of active clients
            self.counter_font = QFont()
            self.counter_font.setPointSize(14)
            self.counter_font.setFamily("Arial")

            self.counter_label = QLabel("Active Clients: ", self)
            self.counter_label.setGeometry(500, 100, 300, 50)
            self.counter_label.setFont(self.counter_font)

            self.counter_value = 0
            self.client_counter = QLabel(f"{self.counter_value}", self)
            self.client_counter.setGeometry(600, 100, 300, 50)
            self.client_counter.setFont(self.counter_font)

            #Table of registered clients
            #Client is represented by the token
            #Additionaly shows the plugin and the last command type plus its confirmations status
            self.client_table = QTableWidget(self)
            self.column_headers = ["No.", "Plugin", "Status"]
            self.client_table.setColumnCount(len(self.column_headers))
            self.client_table.setHorizontalHeaderLabels(self.column_headers)
            self.client_table.setGeometry(500, 150, 400, 330)

            self.client_table.setStyleSheet("""
                            QTableWidget {
                                border: 3px solid grey;
                                border-radius: 7px;
                                font-family: "Courier New";
                                font-size: 12px;
                            }
                            QTableWidget::item {
                                border-bottom: 1px solid black;
                            }
                            QTableWidget::item:selected {
                                background-color: lightblue;
                            }
                            QHeaderView::section {
                                background-color: grey;
                                color: black;
                                font-weight: bold;
                                font-family: "Arial";
                            }
                        """)

            #Access section: MongoDB queries
            self.access_label = QLabel("Access", self)
            self.access_label.setGeometry(100, 490, 150, 50)
            self.access_label.setFont(self.section_font)

            #User input for the query
            self.query_input = QTextEdit("Please provide input in JSON format!", self)
            self.query_input.setGeometry(100, 540, 300, 100)
            self.query_input.setStyleSheet("""
                QTextEdit {
                    border: 3px solid black;
                    border-radius: 7px;         
                    font-family: Courier New;          
                    font-size: 12px;   
                }
            """)
            
            self.query_output = QTextEdit("Awaiting query...", self)
            self.query_output.setGeometry(600, 540, 300, 100)
            self.query_output.setStyleSheet(generic_textbox_style)
            self.query_output.setReadOnly(True)

            #Start button for query
            self.query_button =QPushButton("Query", self)
            self.query_button.clicked.connect(self.click__on_query)
            self.query_button.setGeometry(425, 570, 150, 50)
            self.query_button.setFont(self.button_font)
            self.query_button.setStyleSheet(generic_button_style)

            #Version and License
            self.info_font = QFont()
            self.info_font.setPointSize(8)
            self.info_font.setFamily("Arial")

            info = "@2024. Pre-release version"
            self.info_label = QLabel(info, self)
            self.info_label.move(0,0)
            self.info_label.setStyleSheet("color : grey")
            self.info_label.setFont(self.info_font)

#We will put this inside main.py
def run_gui():
    gui_app = QApplication(sys.argv)
    gui = UserInterface()
    gui.show()
    sys.exit(gui_app.exec_())

run_gui()

