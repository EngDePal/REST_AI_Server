"""Main script to execute the application"""
#Importing modules
from packages.server import Server
from packages.user_interface import UserInterface
from PyQt5.QtWidgets import QApplication
import sys
#Importing threading
#GUI and Server need to be run in separate threads
#To achieve acceptable performance
import threading

#Main function
def main():
    #Creating and running thread for server
    server_thread  = threading.Thread(target=run_server)
    server_thread.start()

    #Running GUI in main thread
    run_gui()


#Define start-up functions

def run_gui():
    gui_app = QApplication(sys.argv)
    gui = UserInterface()
    gui.show()
    sys.exit(gui_app.exec_())

def run_server():
    server = Server()
    server.start_server()

#Script
main()