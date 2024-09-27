#!/usr/bin/env python

import PySimpleGUI as sg

# THIS WILL BE GUI FOR CONFIGURING BEHAVIOUR OF rsync_to_VM.py
# EITHER ONE-TIME BY RUNNING IT WITH CLI ARGUMENTS
# OR PERMANENTLY (UNTIL NEXT CONFIG) BY CHANGING sync_conf.py

# configure layout
layout = [[sg.Text("Hello, this will be configuration window!")], [sg.Button("Set")]]

# Create window
window = sg.Window("Configure rsync_to_VM.py", layout)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user clicks on OK, or closes the window
    if event in ["Set", sg.WIN_CLOSED]:
        break

window.close()
