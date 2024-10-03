"""GUI for the REST AI Server"""
#Importing the PyQt5 GUI framework and other modules
from PyQt5.QtWidgets import QWidget, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QTextEdit, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
#Running server backend
from packages.server import Server
#For server shutdown
import requests
#For correct GUI layout
import platform

class CockpitWidget(QWidget):

    #Constructor:
    def __init__(self):

        #Setting up GUI
        super().__init__()

        #Switch between layouts depending on OS
        if platform.system() == "Darwin" or platform.system() == "Linux": 
            self.design_mac_interface()
        elif platform.system() == "Windows":
            self.design_windows_interface()
        else:
             raise Exception("Unknown operating system. No Widget template available.")
        
        #Server state: On -> True or Off -> False
        self.server_state = False

    #Methods handling logic and user inputs

    #Updates the amount of active clients
    def update_counter(self, count: int):
        self.client_counter.setText(f"{count}")

    #Updates the table with client infos
    def update_table(self, data: dict, remove: bool, update: bool):

        #False -> Add data
        if remove == False:

            #Check, whether new data is added or just updated

            #False -> Create a new line
            if update == False:
            
                self.add_table_data(data)

            #True -> Update a line
            if update == True:
                 
                 self.update_table_data(data)

        #True -> Remove data
        if remove == True:
            
            self.remove_table_data(data)

    #Updates the status line
    def update_status(self, token: str, mode: str):
         
        text = ""
         
        if mode == "LOGIN":
              text = f"New Client succesfully logged in.\nGenerated ID: {token}."

        elif mode == "LOGOUT":
              text = f"A client has logged out.\nClient ID: {token}"
        
        self.status_line.setText(text)

    #Instructs the user to check the terminal
    def notify_login(self):
         
        text = "A new client attemps to login.\nPlease check the terminal for further instructions."
        self.status_line.setText(text)

    #Info about server start
    def notify_start(self):
        text = "The server has been started."
        self.status_line.setText(text)
         
    #Starts the server
    def click_on_start(self):

        if self.server_state == False:

            #Setting up server
            self.server = Server()

            #Connect signals
            self.connect_signals()

            #Start server in separate thread and get the url
            self.server.start()

            #Change state to on
            self.server_state = True
    
    #Stops the server
    def click_on_shutdown(self):

        if self.server_state == True:

            #Notifying user
            decision = self.show_confirmation_dialog()

            self.server_state == False

            if decision == True:
                #Calling shutdown method
                shutdown_url = self.base_url + "shutdown"
                response = requests.post(shutdown_url)

    #Updating the URL with info from the server
    def set_url(self, url: str):
         
         self.base_url = url

    #Confirmation dialog for server shutdown
    def show_confirmation_dialog(self):

        #Show the message box and capture the user response
        reply = self.msg_box.exec_()

        #Return True if 'Yes' is clicked, otherwise False
        return reply == QMessageBox.Yes

    def connect_signals(self):
         
        #Connect server signals
        self.server.counter_signal.connect(self.update_counter)
        self.server.table_signal.connect(self.update_table)
        self.server.user_info_signal.connect(self.update_status)
        self.server.login_signal.connect(self.notify_login)
        self.server.start_signal.connect(self.notify_start)
        self.server.url_signal.connect(self.set_url)
    
    #Adds the input data to the client table
    def add_table_data(self, data: dict):

        #Dict of column index to data
            row_data = dict()
            target_row = None

            #Preparing data
            #Token and plugin name are added during login
            if "token" in data.keys():
                    value = data["token"]
                    target_row = self.determine_row(value)
                    row_data[0] = str(value)
            if "plugin_name" in data.keys():
                    value = data["plugin_name"]
                    row_data[1] = str(value)
                
            #Filling up with empty strings to avoid Key Errors
            row_data[2] = ""
            row_data[3] = ""

            #Adding data
            for column in range(self.table_column_count):
                item = QTableWidgetItem(row_data[column])
                #Make data read only
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.client_table.setItem(target_row, column, item)

    #Updates the command and parameters columns of a row
    def update_table_data(self, data: dict):
         
        #Get the row of the existing token
        if "token" in data.keys():
            target_row = self.search_client(data["token"])
        else:
             raise Exception("Error in data transmission to widget: No token included.")

        #Update the fields if the row exists
        if target_row is not None:   
            if "command" in data.keys():
                    value = str(data["command"])
                    item = QTableWidgetItem(value)
                    self.client_table.setItem(target_row, 2, item)
                    #Resize column depending on content
                    if value in ["LIN", "PTP", "INFO", "LOG", "EXIT"]:
                        self.client_table.setRowHeight(target_row, 50)
                    elif value == "CIRC":
                        self.client_table.setRowHeight(target_row, 100)
            if "parameters" in data.keys():
                    parameters = data["parameters"]
                    parameters.pop("type")
                    item = QTableWidgetItem(str(parameters))
                    self.client_table.setItem(target_row, 3, item)


    #Removes table rows
    def remove_table_data(self, data: dict):
         
        #Search for the token in the table
        if "token" in data.keys():
            target_row = self.search_client(data["token"])
        else:
            raise Exception("Error in data transmission to widget: No token included.")
            
        if target_row is not None:
                 self.client_table.removeRow(target_row)

        #Update row count to avoid empty rows
        self.table_row_count -= 1


    #Searches for a client in the table by token
    #Returns the corresponding row
    def determine_row(self, token: str):

        target_row = self.search_client(token)

        if target_row == None:
            #If there are no rows yet, one will be created
            if self.table_row_count == 0:
                target_row = 0
                self.table_row_count = 1
                self.client_table.setRowCount(self.table_row_count)
            #Else a new row is added for the new data
            else:
                target_row = self.table_row_count
                self.table_row_count += 1
                self.client_table.setRowCount(self.table_row_count)

        #Check in case of errors
        if target_row is None:
            raise Exception("An issues with table data assignment has occurred.")
           
        return target_row
    
    #Searches for an existing client in the table
    #Returns None, if there is no match
    def search_client(self, token: str):
         
        target_row = None

        #Checking all rows
        for row in range(self.table_row_count):
            #Token is always in the first column
            item = self.client_table.item(row, 0)
            if item is not None:
                if item.text() == token:
                    target_row = row

        return target_row
         

    #Defines all interface elements for MacOS
    def design_mac_interface(self):
        #Application window setup
            self.setWindowTitle("RemoteMind Telepath Cockpit")
            self.setStyleSheet("background-color: white")
            self.setGeometry(100, 100, 800, 700)

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
            self.cockpit_label.setGeometry(50, 50, 100, 50)
            self.cockpit_label.setFont(self.section_font)

            #Server control

            #Start server button
            self.start_button = QPushButton("Start Server", self)
            self.start_button.clicked.connect(self.click_on_start)
            self.start_button.setFixedSize(200,50)
            self.start_button.move(50, 150)
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
            self.shutdown_button.setFixedSize(200,50)
            self.shutdown_button.move(50, 215)
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

            #Status line

            self.status_font = QFont()
            self.status_font.setPointSize(16)
            self.status_font.setFamily("Arial")

            self.status_label = QLabel("Status", self)
            self.status_label.setGeometry(300, 100, 50, 50)
            self.status_label.setFont(self.status_font)

            self.status_line = QTextEdit(self)
            self.status_line.setGeometry(300, 150, 450, 115)
            self.status_line.setStyleSheet("""
                        QTextEdit {
                            background-color: white;
                            border: 3px solid black;
                            border-radius: 7px;
                            font-family: 'Courier New';
                            font-size: 14px;
                            color: black;
                        }
                    """
                    )
            self.status_line.setReadOnly(True)
            

            #Number of active clients
            self.counter_font = QFont()
            self.counter_font.setPointSize(16)
            self.counter_font.setFamily("Arial")

            self.counter_label = QLabel("Active Clients: ", self)
            self.counter_label.setGeometry(50, 100, 100, 50)
            self.counter_label.setFont(self.counter_font)

            self.counter_value = 0
            self.client_counter = QLabel(f"{self.counter_value}", self)
            self.client_counter.setGeometry(175, 100, 50, 50)
            self.client_counter.setFont(self.counter_font)

            #Table of registered clients
            #Client is represented by the token
            #Additionaly shows the plugin and the last command type plus its confirmation status
            self.client_table = QTableWidget(self)
            self.column_headers = ["Token", "Plugin", "Recent Command", "Recent Parameters"]
            self.client_table.setColumnCount(len(self.column_headers))
            self.client_table.setRowCount(0)
            self.client_table.setHorizontalHeaderLabels(self.column_headers)
            self.client_table.setGeometry(50, 280, 700, 400)

            self.table_row_count = 0
            self.table_column_count = len(self.column_headers)

            #Setting column width
            row_widths = [80, 100, 125, 375]
            for i in range(self.table_column_count):
                self.client_table.setColumnWidth(i, row_widths[i])

            self.client_table.setStyleSheet("""
                            QTableWidget {
                                border: 3px solid grey;
                                border-radius: 7px;
                                font-family: "Courier New";
                                font-size: 14px;
                            }
                            QTableWidget::item {
                                border-bottom: 1px solid grey
                            }
                            QTableWidget::item:selected {
                                background-color: grey;
                            }
                            QHeaderView::section {
                                background-color: white;
                                color: black;
                                font-family: "Arial";
                                font-size: 14px
                                border-bottom: 1px solid grey
                            }
                            QTableWidget::horizontalHeader {
                                border-bottom: 1px solid grey
                                color: black
                                font-family: "Arial";
                                font-size: 14px;      
                            }
                            QTableWidget::verticalHeader {
                                border-bottom: 1px solid grey
                                color: black
                                font-family: "Arial";
                                font-size: 14px;      
                            }
                        """)
            
            #Confirmation dialog

            self.msg_box = QMessageBox()

            #Dialog text
            self.msg_box.setWindowTitle('Server Shutdown')
            self.msg_box.setText('Do you really want to shut down the server? This will close the entire application.')

            #Dialog Functionality
            self.msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            self.msg_box.setDefaultButton(QMessageBox.Cancel)

            #Dialog Styling
            self.msg_box.setIcon(QMessageBox.Warning)

            self.msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: black;
                    font-size: 14px;
                    font-family: "Arial"
                }
                QPushButton {
                    background-color: white;
                    color: black;
                    font-family: "Arial"
                    border-radius: 7px;
                    font-size: 14px;
                    border: 3px solid black
                                       
                }
                QPushButton:hover {
                    font-weight: bold
                }
            """)

            #Version and License
            self.info_font = QFont()
            self.info_font.setPointSize(8)
            self.info_font.setFamily("Arial")

            info = "@2024. Version 1.0: Initial release."
            self.info_label = QLabel(info, self)
            self.info_label.move(0,0)
            self.info_label.setStyleSheet("color : grey")
            self.info_label.setFont(self.info_font)

    #Defines all interface elements for Microsoft Windows
    def design_windows_interface(self):
         #Application window setup
            self.setWindowTitle("RemoteMind Telepath Cockpit")
            self.setStyleSheet("background-color: white")
            self.setGeometry(100, 100, 800, 700)

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

            #Server control

            #Start server button
            self.start_button = QPushButton("Start Server", self)
            self.start_button.clicked.connect(self.click_on_start)
            self.start_button.setFixedSize(200,50)
            self.start_button.move(50, 150)
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
            self.shutdown_button.setFixedSize(200,50)
            self.shutdown_button.move(50, 215)
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

            #Status line

            self.status_font = QFont()
            self.status_font.setPointSize(16)
            self.status_font.setFamily("Arial")

            self.status_label = QLabel("Status", self)
            self.status_label.setGeometry(300, 100, 100, 50)
            self.status_label.setFont(self.status_font)

            self.status_line = QTextEdit(self)
            self.status_line.setGeometry(300, 150, 450, 115)
            self.status_line.setStyleSheet("""
                        QTextEdit {
                            background-color: white;
                            border: 3px solid black;
                            border-radius: 7px;
                            font-family: 'Courier New';
                            font-size: 14px;
                            color: black;
                        }
                    """
                    )
            self.status_line.setReadOnly(True)
            

            #Number of active clients
            self.counter_font = QFont()
            self.counter_font.setPointSize(16)
            self.counter_font.setFamily("Arial")

            self.counter_label = QLabel("Active Clients: ", self)
            self.counter_label.setGeometry(50, 100, 150, 50)
            self.counter_label.setFont(self.counter_font)

            self.counter_value = 0
            self.client_counter = QLabel(f"{self.counter_value}", self)
            self.client_counter.setGeometry(200, 100, 50, 50)
            self.client_counter.setFont(self.counter_font)

            #Table of registered clients
            #Client is represented by the token
            #Additionaly shows the plugin and the last command type plus its confirmation status
            self.client_table = QTableWidget(self)
            self.column_headers = ["Token", "Plugin", "Recent Command", "Recent Parameters"]
            self.client_table.setColumnCount(len(self.column_headers))
            self.client_table.setRowCount(0)
            self.client_table.setHorizontalHeaderLabels(self.column_headers)
            self.client_table.setGeometry(50, 280, 700, 400)

            self.table_row_count = 0
            self.table_column_count = len(self.column_headers)

            #Setting column width
            row_widths = [80, 100, 125, 375]
            for i in range(self.table_column_count):
                self.client_table.setColumnWidth(i, row_widths[i])

            self.client_table.setStyleSheet("""
                            QTableWidget {
                                border: 3px solid grey;
                                border-radius: 7px;
                                font-family: "Courier New";
                                font-size: 14px;
                            }
                            QTableWidget::item {
                                border-bottom: 1px solid grey
                            }
                            QTableWidget::item:selected {
                                background-color: grey;
                            }
                            QHeaderView::section {
                                background-color: white;
                                color: black;
                                font-family: "Arial";
                                font-size: 14px
                                border-bottom: 1px solid grey
                            }
                            QTableWidget::horizontalHeader {
                                border-bottom: 1px solid grey
                                color: black
                                font-family: "Arial";
                                font-size: 14px;      
                            }
                            QTableWidget::verticalHeader {
                                border-bottom: 1px solid grey
                                color: black
                                font-family: "Arial";
                                font-size: 14px;      
                            }
                        """)
            
            #Confirmation dialog

            self.msg_box = QMessageBox()

            #Dialog text
            self.msg_box.setWindowTitle('Server Shutdown')
            self.msg_box.setText('Do you really want to shut down the server? This will close the entire application.')

            #Dialog Functionality
            self.msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            self.msg_box.setDefaultButton(QMessageBox.Cancel)

            #Dialog Styling
            self.msg_box.setIcon(QMessageBox.Warning)

            self.msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: black;
                    font-size: 14px;
                    font-family: "Arial"
                }
                QPushButton {
                    background-color: white;
                    color: black;
                    font-family: "Arial"
                    border-radius: 7px;
                    font-size: 14px;
                    border: 3px solid black
                                       
                }
                QPushButton:hover {
                    font-weight: bold
                }
            """)

            #Version and License
            self.info_font = QFont()
            self.info_font.setPointSize(8)
            self.info_font.setFamily("Arial")

            info = "@2024. Version 1.0: Initial release."
            self.info_label = QLabel(info, self)
            self.info_label.move(0,0)
            self.info_label.setStyleSheet("color : grey")
            self.info_label.setFont(self.info_font)