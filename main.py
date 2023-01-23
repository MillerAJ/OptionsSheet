
import PySimpleGUI as sg
import stockFunctions as sF
import optionFunctions as oF
import opstrat as op
import matplotlib.pyplot as plt
from multiprocessing import Process

# INCOMPLETE -- This was to create the GUI for the optionSheet, I don't think this actually does anything...
def createWindow():
    sg.theme('Default1')  # Add a little color to your windows
    # All the stuff inside your window.
    layout = [[sg.Text('Ticker:'), sg.InputText()],
              [sg.Button("Search", bind_return_key=True), sg.Button("Close")]]
    # Create the Window
    window = sg.Window('Option Sheet', layout, default_element_size=(30, 10),
                       resizable=True, finalize=True)
    window.bind('<Configure>', "Event")
    openOptionSheet = False
    # Event Loop to process "events"
    while True:
        event, values = window.read()
        #print(values)
        if event in (sg.WIN_CLOSED, 'Close'):
            break
        if event == 'Search':
            if values[0] != None:
                ticker = values[0].upper()
                openOptionSheet = True
                break
    window.close()
    while openOptionSheet == True:
        openOptionSheet, ticker = sF.createOptionSheet(ticker)


if __name__ == '__main__':
    ticker = 'TSLA'

    #============================================================================
    #       Left off: 
    # having an issue reading tet from a text field...may need to just make it an inut field? (maybe I can make it uneditable?)
    # -HISTORICVOL- is the problem child...
    # ========================================================================

    # expirationDates, callList, putList = sF.getOptions(ticker)
    sF.createOptionSheet(ticker)


    # main program tht asks user for a ticker to start
    #createWindow()




    #how opstrat takes list of options below...

    # op1={'op_type': 'c', 'strike': 215, 'tr_type': 's', 'op_pr': 7.63}
    # op2={'op_type': 'c', 'strike': 220, 'tr_type': 'b', 'op_pr': 5.35}
    # op3={'op_type': 'p', 'strike': 210, 'tr_type': 's', 'op_pr': 7.20}
    # op4={'op_type': 'p', 'strike': 205, 'tr_type': 'b', 'op_pr': 5.52}
    #
    # op_list=[op1, op2, op3, op4]
    # op.multi_plotter(spot=212.26,spot_range=10, op_list=op_list)


