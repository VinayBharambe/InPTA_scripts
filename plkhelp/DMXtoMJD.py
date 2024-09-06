# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 10:28:18 2024

@author: Vinay

@author: Vinay Bharambe

title           : plk_help.py
description     : This is a GUI addon for Tempo2. It inputs par file and tim file 
                    to make a user friendly GUI. User can select and deselect DMX
                    parameters to get MJD of the selected DMX.
date            : 01 June 2024
notes           : You need PyQT5 installed

"""

import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox,QGridLayout, QCheckBox, QPushButton, QVBoxLayout, QHBoxLayout, QInputDialog
from PyQt5.QtCore import Qt
import subprocess
import os

def print_help():
    print("Usage: DMXtoMJD.py -f <par_file_path> <tim_file_path>")
    print("Example: DMXtoMJD.py -f file1.par file2.tim")

def read_files(file1_path, file2_path):
    try:
        with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
            file1_content = f1.read()
            file2_content = f2.read()
        return file1_content, file2_content
    except FileNotFoundError:
        print("Error: One or both files not found.")
        print_help()
        sys.exit(1)


class CheckBoxApp(QWidget):
    def __init__(self, cols,value,fit,error_value,file1_path,file2_path,mjd):
        
        keywords = {
    "PSRJ", "ELONG", "ELAT", "BINARY", "TZRSITE", "START", "FINISH", "TZRMJD", 
    "TZRFRQ", "TRES", "EPHVER", "NE_SW", "CLK", "UNITS", "TIMEEPH", "DILATEFREQ", 
    "PLANET_SHAPIRO", "T2CMETHOD", "CORRECT_TROPOSPHERE", "EPHEM", "NITS", "NTOA", "MODE","CHI2R"}
        
        super().__init__()
        self.cols = cols
        self.fit = fit
        self.value = value
        self.error_value = error_value
        self.file1_path = file1_path
        self.file2_path = file2_path
        self.mjd = mjd

        # Set the layout
        # Set the layout
        self.layout = QVBoxLayout()
        self.setGeometry(100, 100, 800, 400) 
        
        
        # Create checkboxes based on names and values
        self.checkbox_layout = QGridLayout()
        self.checkboxes = []
        row = 0
        col = 0
        
                
        for i, (cols, fit) in enumerate(zip(cols, fit)):
            if cols.startswith("DMX_") :
                checkbox = QCheckBox(str(cols))
                checkbox.setChecked(bool(fit))
                checkbox.stateChanged.connect(lambda state, index=i: self.update_values(index, state))
                self.checkbox_layout.addWidget(checkbox, row, col)
                self.checkboxes.append(checkbox)
                col += 1
                if col >= 4:
                    col = 0
                    row += 1
        
        # Set the layout for the QWidget
        self.setLayout(self.layout)
        
        # Add the checkbox layout to the main layout
        self.layout.addLayout(self.checkbox_layout)
        
        # Create buttons
        self.buttons_layout = QHBoxLayout()


        self.all_button = QPushButton("Select All")
        self.all_button.clicked.connect(self.check_all_checkboxes)
        self.buttons_layout.addWidget(self.all_button)
        
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.deselect_all_checkboxes)
        self.buttons_layout.addWidget(self.deselect_all_button)

        self.quit_button = QPushButton("Reset")
        self.quit_button.clicked.connect(self.reset)
        self.buttons_layout.addWidget(self.quit_button)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)
        self.buttons_layout.addWidget(self.quit_button)
        

        
        # Add buttons layout to the main layout
        self.layout.addLayout(self.buttons_layout)
        
        # Set the layout for the QWidget
        self.setLayout(self.layout)
        self.setWindowTitle('InPTA DMX to MJD  --> '+self.file1_path)

        self.setStyleSheet("background-color: #ffffcc;")
    
    def check_all_checkboxes(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
            checkbox.setChecked(True)

    def deselect_all_checkboxes(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
            
        
    def reset(self):
        one = self.file1_path
        two = self.file2_path
        self.close()
        print("\n \n Restarted the interface \n \n")
        print("=====================================================================")
        os.system(f"python3 DMXtoMJD.py -f {one} {two}")
        
        

    def update_values(self,index, state):
        
        checkbox = self.sender()
        # Update the values list based on the checkbox state
        if state == Qt.Checked:
            self.fit[index] = 1
            checkbox.setText(self.cols[index]+" = "+str(self.mjd[index]))
            print(f"{self.cols[index]} is {self.mjd[index]}")
        else:
            self.fit[index] = 0
            checkbox.setText(self.cols[index])
            #print(f"{self.cols[index]} is unfitted")
        
    
    


def main():
    if len(sys.argv) != 4 or sys.argv[1] != "-f":
        print("Error: Incorrect arguments.")
        print_help()
        sys.exit(1)
    
    file1_path = sys.argv[2]
    file2_path = sys.argv[3]

    cols = []
    value = []
    fit = []
    error_value=[]
    mjd=[]

    with open(file1_path, 'r') as file:
        # Read each line in the file
        for line in file:
            # Split the line by both spaces and tabs
            parts = line.split()
            
            cols.append(parts[0])
            try:
                temp = float(parts[1])
                if parts[0]=="EPHVER":
                    temp = int(parts[1])
            except ValueError:
              temp = parts[1]

            value.append(temp)

            if len(parts)==2:
              fit.append(0)
              error_value.append(0)
            elif len(parts)==3:
              fit.append(0)
              error_value.append(float(parts[2]))
            elif len(parts)==4:
              fit.append(int(parts[2]))
              error_value.append(float(parts[3]))
            else:
              a=1   

    for each in cols:
        if each.startswith("DMX_"):
            number = each[4:8] 
            mjd.append((value[cols.index("DMXR1_"+number)]+value[cols.index("DMXR2_"+number)])/2)
        else:
            mjd.append(0)

    #print(mjd)

    
    # Create the application object
    app = QApplication([])
    
    # Create an instance of the application window
    window = CheckBoxApp(cols,value,fit,error_value,file1_path,file2_path,mjd)
    
    window.show()
    
    

    # Run the application's event loop
    app.exec_()
    

    

if __name__ == '__main__':
    main()

    


