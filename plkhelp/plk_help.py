# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 10:28:18 2024

@author: Vinay Bharambe

title           : plk_help.py
description     : This is a GUI addon for Tempo2. It inputs par file and tim file 
                    to make a user friendly GUI. User can fit, unfit parameters and
                    call in tempo2 from the GUI. You can also call a sister GUI addon "DMXtoMJD.py"
date            : 01 June 2024
notes           : You need PyQT5 installed


"""

import sys
import pandas as pd
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QVBoxLayout, QCheckBox,QGridLayout, QCheckBox, QPushButton, QVBoxLayout, QHBoxLayout, QInputDialog
from PyQt5.QtCore import Qt
import subprocess
import os

def print_help():
    print("Usage: plk_help.py -f <par_file_path> <tim_file_path>")
    print("Example: plk_help.py -f file1.par file2.tim")

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

def write_par_file(cols,value,fit,error_value):
    
    keywords = {
    "PSRJ", "ELONG", "ELAT", "BINARY", "TZRSITE", "START", "FINISH", "TZRMJD", 
    "TZRFRQ", "TRES", "EPHVER", "NE_SW", "CLK", "UNITS", "TIMEEPH", "DILATEFREQ", 
    "PLANET_SHAPIRO", "T2CMETHOD", "CORRECT_TROPOSPHERE", "EPHEM", "NITS", "NTOA"}
    
    with open('temp_par.txt', 'w') as file:
        # Write each set of items from the lists to the file
        for item1, item2, item3, item4 in zip(cols,value,fit,error_value):
            if item1 in keywords:
                file.write(f"{item1}\t{item2}\n")
            elif item1 == "MODE":
                file.write(f"{item1} {1}\n")
            else:
                file.write(f"{item1}\t{item2}\t{item3}\t{item4}\n")
    #print("Data written to file successfully.")
    


class CheckBoxApp(QWidget):
    def __init__(self, cols,value,fit,error_value,file1_path,file2_path):
        
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

        # Set the layout
        # Set the layout
        self.layout = QVBoxLayout()
        self.setGeometry(100, 100, 800, 600) 
        
        
        # Create checkboxes based on names and values
        self.checkbox_layout = QGridLayout()
        self.checkboxes = []
        row = 0
        col = 0
        
                
        for i, (cols, fit) in enumerate(zip(cols, fit)):
            if cols not in keywords and not (cols.startswith("DMXEP") or cols.startswith("DMXR") or cols.startswith("DMXF")):
                checkbox = QCheckBox(cols)
                checkbox.setChecked(bool(fit))
                checkbox.stateChanged.connect(lambda state, index=i: self.update_values(index, state))
                self.checkbox_layout.addWidget(checkbox, row, col)
                self.checkboxes.append(checkbox)
                col += 1
                if col >= 5:
                    col = 0
                    row += 1
        
        # Set the layout for the QWidget
        self.setLayout(self.layout)
        
        # Add the checkbox layout to the main layout
        self.layout.addLayout(self.checkbox_layout)
        
        # Create buttons
        self.buttons_layout = QHBoxLayout()
        
        self.fit_button = QPushButton("Fit with Tempo2")
        self.fit_button.clicked.connect(self.fit_with_tempo2)
        self.buttons_layout.addWidget(self.fit_button)

        self.custom_button = QPushButton("Custom Tempo2 Command")
        self.custom_button.clicked.connect(self.custom_tempo2)
        self.buttons_layout.addWidget(self.custom_button)

        self.save_button = QPushButton("Save Par File")
        self.save_button.clicked.connect(self.save_par_file)
        self.buttons_layout.addWidget(self.save_button)

        self.open_button = QPushButton("Open DMX to MJD")
        self.open_button.clicked.connect(self.open_dmx_to_mjd)
        self.buttons_layout.addWidget(self.open_button)

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
        self.setWindowTitle(f"InPTA plk interface --> python3  plk_help.py  -f  {self.file1_path}  {self.file2_path}")


    def fit_with_tempo2(self):
        # Run the command "python one.py"
        #subprocess.run(["tempo2 -us -gr plk -f J0740+6620.DMX.par J0740+6620_allToAs.200.tim"])
        os.system(f"tempo2 -us -gr plk -f temp_par.txt {self.file2_path}")

    def custom_tempo2(self):
        # Prompt the user to enter a custom tempo2 command and run it
        text, run = QInputDialog.getText(self, 'Enter Command', 'Enter valid Tempo2 command:')
        if run:
            print(f"{text}")
            os.system(f"{text}")
        

    def save_par_file(self):
        # Prompt the user to enter a text input and print it
        text, ok = QInputDialog.getText(self, 'Save Par File', 'Enter text:')
        if ok:
            os.system(f"cp -pr temp_par.txt {text}")
            print(f"{text} saved succesfully.")
    
    def open_dmx_to_mjd(self):
        # Run the command "python two.py"
        os.system(f"python3 DMXtoMJD.py -f {self.file1_path} {self.file2_path}")
        
    def reset(self):
        one = self.file1_path
        two = self.file2_path
        self.close()
        print("\n \n Restarted the interface \n \n")
        print("================================================================================================")
        os.system(f"python3 plk_help.py -f {one} {two}")
        
        

    def update_values(self,index, state):
        # Update the values list based on the checkbox state
        if state == Qt.Checked:
            self.fit[index] = 1
            print(f"{self.cols[index]} is fitted")
            write_par_file(self.cols,self.value,self.fit,self.error_value)
        else:
            self.fit[index] = 0
            print(f"{self.cols[index]} is unfitted")
            write_par_file(self.cols,self.value,self.fit,self.error_value)
        
    
    


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

    #print(value)
    write_par_file(cols,value,fit,error_value)
    
    # Create the application object
    app = QApplication([])
    
    # Create an instance of the application window
    window = CheckBoxApp(cols,value,fit,error_value,file1_path,file2_path)
    
    window.show()
    
    

    # Run the application's event loop
    app.exec_()
    
    os.system("rm -rf temp_par.txt")

    

if __name__ == '__main__':
    main()

    


