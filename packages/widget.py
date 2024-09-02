"""GUI for the REST AI Server"""
#NOT FUNCTIONAL
#Importing the PyQt5 GUI framework and other modules
from PyQt5.QtWidgets import QWidget, QLabel, QTableWidget
from PyQt5.QtGui import QFont
#Running server backend
from packages.server import Server


class CockpitWidget(QWidget):

    #Starting 
    def __init__(self):

        #Setting up GUI
        super().__init__()
        self.design_interface()

        #Setting up server
        self.server = Server()
        #Running server in secondary thread
        self.server.start()

        #Connect server signals
        self.server.counter_signal.connect(self.update_counter)

        #Status variable
        #Status 1 is online, 0 offline
        self.server_status = 1

    #Methods handling logic and user inputs

    #Updates the amount of active clients
    def update_counter(self, count: int):
        self.client_counter.setText(f"{count}")

    def update_table(self):
        pass

    def close_app(self):
        pass

    #Defines all interface elements
    def design_interface(self):
        #Application window setup
            self.setWindowTitle("RemoteMind Telepath Cockpit")
            self.setStyleSheet("background-color: white")
            self.setGeometry(100, 100, 800, 650)

            #Stylish App Name
            prefix_font = QFont()
            prefix_font.setPointSize(40)
            prefix_font.setBold(True)

            self.prefix_label = QLabel("Telepath", self)
            self.prefix_label.setStyleSheet("color : purple; font : Lucida" )
            self.prefix_label.setFont(prefix_font)
            self.prefix_label.move(550,50)

            suffix_font = QFont()
            suffix_font.setPointSize(22)
            suffix_font.setItalic(True)
            suffix_font.setBold(True)
            suffix_font.setFamily("Arial")

            self.suffix_label = QLabel("RemoteMind", self)
            self.suffix_label.setStyleSheet("color : dark grey;")
            self.suffix_label.setFont(suffix_font)
            self.suffix_label.move(600,30)

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

            #Setting font for the section header
            self.section_font = QFont()
            self.section_font.setBold(True)
            self.section_font.setFamily("Arial")
            self.section_font.setPointSize(22)

            #Cockpit section: Check clients
            self.cockpit_label = QLabel("Cockpit", self)
            self.cockpit_label.setGeometry(50, 50, 150, 50)
            self.cockpit_label.setFont(self.section_font)

            #Number of active clients
            self.counter_font = QFont()
            self.counter_font.setPointSize(16)
            self.counter_font.setFamily("Arial")

            self.counter_label = QLabel("Active Clients: ", self)
            self.counter_label.setGeometry(50, 100, 300, 50)
            self.counter_label.setFont(self.counter_font)

            self.counter_value = 0
            self.client_counter = QLabel(f"{self.counter_value}", self)
            self.client_counter.setGeometry(175, 100, 300, 50)
            self.client_counter.setFont(self.counter_font)

            #Table of registered clients
            #Client is represented by the token
            #Additionaly shows the plugin and the last command type plus its confirmations status
            self.client_table = QTableWidget(self)
            self.column_headers = ["Token", "Plugin", "Last Command", "Target Coordinates"]
            self.client_table.setColumnCount(len(self.column_headers))
            self.client_table.setHorizontalHeaderLabels(self.column_headers)
            self.client_table.setGeometry(50, 200, 700, 400)

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
                                font-size: 14px
                            }
                        """)
            
            #Instructions
            self.instructions_font = QFont()
            self.instructions_font.setPointSize(16)
            self.instructions_font.setFamily("Arial")
            self.instructions_font.setBold(True)

            instructions = "Controll the app using the terminal - Observe your robots through the widget"
            self.instructions_label = QLabel(instructions, self)
            self.instructions_label.move(50,150)
            self.instructions_label.setStyleSheet("color : black")
            self.instructions_label.setFont(self.instructions_font)

            #Version and License
            self.info_font = QFont()
            self.info_font.setPointSize(8)
            self.info_font.setFamily("Arial")

            info = "@2024. Pre-release version"
            self.info_label = QLabel(info, self)
            self.info_label.move(0,0)
            self.info_label.setStyleSheet("color : grey")
            self.info_label.setFont(self.info_font)

