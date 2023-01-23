
import PySimpleGUI as sg
import stockFunctions as sF
import optionFunctions as oF
import opstrat as op
import matplotlib.pyplot as plt
from multiprocessing import Process

def createWindow():
    sg.theme('Default1')  
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
    # main program that asks user for a ticker to start
    createWindow()


