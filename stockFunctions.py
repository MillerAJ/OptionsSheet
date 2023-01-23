import numpy as np
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas_datareader import data as pdr
import PySimpleGUI as sg
from matplotlib import style
import yfinance as yf
import pyautogui
import opstrat as op
import optionFunctions as oF

# returns the company name for a given ticker
def getCompanyName(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    try:
        return soup.find(class_="D(ib) Fz(18px)").get_text()
    except:
        print("error: failed to retrieve company name")


# returns current stock price given a ticker
def getStockPrice(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    try:
        return float(soup.find(class_="Fw(b) Fz(36px) Mb(-4px) D(ib)").get_text())
    except:
        print("error: failed to retrieve stock price")


# creates a histogram of past daily returns
def plotPercentChange(ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5000)  # get 5000 days of data
    yf.pdr_override()  # needed as a workaround, a bug in pandas data reader recently came about
    df = pdr.get_data_yahoo(ticker, start_date, end_date)
    style.use('ggplot')
    pd.options.plotting.backend = 'plotly'
    histo = df['Adj Close'].pct_change().plot(kind='hist', bins=100)
    histo.show()


# plots the price action of a stock
def plotPriceAction(ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5000)  # get 5000 days of data
    yf.pdr_override()  # needed as a workaround, a bug in pandas data reader recently came about
    df = pdr.get_data_yahoo(ticker, start_date, end_date)
    # df = pdr.DataReader(ticker, 'yahoo', start_date, end_date)
    style.use('ggplot')
    pd.options.plotting.backend = 'plotly'
    priceAction = df['Adj Close'].plot()
    # fig = plt.gcf()
    # fig.canvas.manager.set_window_title(ticker + " stock price")
    priceAction.show()


# returns historic volatility given a ticker and number of days to observe (ending at the present date)
# still need to double check that this calculates accurately!!
def getHistoricVol(ticker, time_period):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=time_period)
    yf.pdr_override()  # needed as a workaround as a bug in pandas data reader recently came about
    df = pdr.get_data_yahoo(ticker, start_date, end_date)
    #df = pdr.DataReader(ticker, 'yahoo', start_date, end_date)
    df['PCT_Change'] = df['Adj Close'].pct_change()
    pct_info = df['PCT_Change'].dropna()
    return pct_info.std() * np.sqrt(252)


# returns a dictionary with date:key pairs for contract expiration dates
# this will enable users to select a date and get the related url key to add to the url to see contracts for tht date
def getOptions(ticker, expDate='n'):
    # open yahooFinance
    try:
        if expDate == 'n':
            url = f"https://finance.yahoo.com/quote/{ticker}/options?p={ticker}/"
        else:
            url = f"https://finance.yahoo.com/quote/{ticker}/options?date={expDate}&p={ticker}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
    except:
        print("Error - failed to connect to yahooFinance")
        return 0, 0, 0

    try:
        # get expiration dates
        dropDown = soup.find('div', class_="Fl(start) Pend(18px)")
        items = dropDown.select('option[value]')
        dates = [item.getText() for item in items]
        values = [item.get('value') for item in items]
        expirationDates = {}

    except:
        print("Error - no option contracts found for", ticker.upper())
        return 0, 0, 0
    for i in range(0, len(dates)):
        expirationDates[dates[i]] = values[i]

    # get calls
    callTableHTML = soup.find('table', class_="calls W(100%) Pos(r) Bd(0) Pt(0) list-options")
    callHeaders = []
    for i in callTableHTML.find_all('th'):  # get column headers
        title = i.text.strip()
        callHeaders.append(title)
    callTable = pd.DataFrame(
        columns=callHeaders)  # get each row, expect the first because we already got the headers (hence the "[1:]")
    for row in callTableHTML.find_all('tr')[1:]:
        data = row.find_all('td')
        row_data = [td.text.strip() for td in data]
        length = len(callTable)
        callTable.loc[length] = row_data

    # get puts
    putTableHTML = soup.find('table', class_="puts W(100%) Pos(r) list-options")
    putHeaders = []
    for i in putTableHTML.find_all('th'):  # get column headers
        title = i.text.strip()
        putHeaders.append(title)
    putTable = pd.DataFrame(
        columns=putHeaders)  # get each row, expect the first becuse we already got the headers (hence the "[1:]")
    for row in putTableHTML.find_all('tr')[1:]:
        data = row.find_all('td')
        row_data = [td.text.strip() for td in data]
        length = len(putTable)
        putTable.loc[length] = row_data

    # modify call and put tables
    # For both callList and putList the colum "Contract Name" is not included to create more space, could be added back in if needed
    callList = callTable.loc[:, ["Last Trade Date", "Open Interest", "Volume", "Implied Volatility",
                                 "Change", "% Change", "Ask", "Bid", "Last Price", "Strike"]]
    putList = putTable[putTable.columns[::-1]]
    putList = putList.loc[:, ["Strike", "Last Price", "Bid", "Ask", "% Change", "Change", "Implied Volatility",
                              "Volume", "Open Interest", "Last Trade Date"]]
    putList.style.set_properties(**{'text-align': 'left'})

    return expirationDates, callList, putList


def updateExpDate(ticker, urlExpirationCode):
    expirationDates, callList, putList = getOptions(ticker, urlExpirationCode)
    if expirationDates == 0:
        return False, ''
    callTableEntries = []
    for val in callList.values.tolist():
        callTableEntries.append(val)
    putTableEntries = []
    for val in putList.values.tolist():
        putTableEntries.append(val)
    return callTableEntries, putTableEntries


def createOptionSheet(ticker):
    sg.theme('LightBrown1')  # Add a little color to your windows
    expirationDates, callList, putList = getOptions(ticker)
    if expirationDates == 0:
        return False, ''

    callTableEntries = []
    for val in callList.values.tolist():
        callTableEntries.append(val)
    callTableHeaders = []
    for val in callList.columns.values.tolist():
        callTableHeaders.append(val)

    putTableEntries = []
    for val in putList.values.tolist():
        putTableEntries.append(val)
    putTableHeaders = []
    for val in putList.columns.values.tolist():
        putTableHeaders.append(val)

    # ===============================================================================================================
    #                       Define Main Window Layout and GUI Elements
    # ================================================================================================================
    stockInfo = [[sg.Text(key="-COMPANYNAME-", font=("Helvetica", 40)), sg.Text(" | Last Price: ", font=("Helvetica", 40)),
                     sg.Text(key="-STOCKPRICE-", font=("Helvetica", 40))]]
    callTable = [[sg.Table(values=callTableEntries, headings=callTableHeaders, justification='r',
                           auto_size_columns=False, num_rows=30, max_col_width=40,
                           row_height=30, key="-CALLTABLE-", enable_events=True)]]
    putTable = [[sg.Table(values=putTableEntries, headings=putTableHeaders, justification='l',
                          auto_size_columns=False, num_rows=30, max_col_width=40,
                          row_height=30, key="-PUTTABLE-", enable_events=True)]]
    expirationDropDown = [
        [sg.Combo(list(expirationDates.keys()), default_value=list(expirationDates.keys())[0], key="expirationDates")]]

    searchBar = [[sg.Text('Ticker:'), sg.InputText(key="-INPUT-")],
                 [sg.Button("Search", bind_return_key=True), sg.Button("Close")]]

    introFrame = [[sg.Frame("Search New Company", searchBar)],
                  [sg.Frame("Stock Info", stockInfo)]]
    positionTableEntries = []
    positionTable = [
        [sg.Table(values=[], headings=["Buy / Sell", "Contract Type", "Strike", "Premium"], justification='c',
                  auto_size_columns=False, def_col_width=15, num_rows=8, alternating_row_color='white',
                  row_height=20, key="-POSITIONTABLE-", enable_events=True)]]

    positionOptions = [
                       [sg.Text("Underlying Price Range to Plot: +/-"), sg.InputText("15", size=(5, 15), justification='r', key="-UNDERLYINGVOL-", pad=0), sg.Text("%")],
                       [sg.Button("Remove Selected Transaction", key="-DELETEPOSITION-")],
                       [sg.Button("Remove All", key="-DELETEALL-")],
                       [sg.Button("Plot Position Payoff", key="-PLOTPAYOFF-")]
                      ]

    optionInfo = [[sg.Frame(" Expiration Date: ", expirationDropDown), sg.Button("Update Exp. Date"), sg.Text("Select an option contract for pricing info or to buy/sell", pad=(200,0), font=("Helvetica", 16))],
                  [sg.Frame(" CALLS: ", callTable), sg.Frame(" PUTS: ", putTable)]]
    historicVolInput = [[sg.Text("Include last"), sg.InputText("365", size=(10,30), key="-HISTORICVOLINPUT-"), sg.Text("days in calculation.")],
                        [sg.Button("Recalculate",key="-CALCHISVOL-"),sg.Text("Historic Volatility ="),
                         sg.InputText('      ',key="-HISVOLOUTPUT-", readonly=True, size=(10,10))]]

    riskFreeRateInput = [[sg.Text("Rate as a decimal: "), sg.InputText(".02", size=(8, 10), key="-RISKFREERATE-")]]
    new_layout = [
        [sg.Column(introFrame), sg.VSeperator(), sg.Frame("Open Position", positionTable), sg.Frame('', positionOptions)],
        [sg.Frame(" Historic Volatility: ",historicVolInput), sg.Frame(" Risk Free Rate: ",riskFreeRateInput), sg.Text("",background_color='#e0f3f6', pad=(250,0)),
            sg.Button("Plot Stock Price", pad=5), sg.Button("Plot Daily Returns", pad=5)],
        [sg.Frame("", optionInfo)]
    ]

    current_price = getStockPrice(ticker)
    companyName = getCompanyName(ticker)
    historicVol = round(getHistoricVol(ticker, 365), 6)

    new_window = sg.Window('Option Sheet',
                           new_layout,
                           default_element_size=(30, 10),
                           resizable=True, finalize=True, background_color='#e0f3f6')

    new_window.bind('<Configure>', "Event")
    new_window.maximize()

    new_window["-HISVOLOUTPUT-"].update(historicVol)
    new_window['-STOCKPRICE-'].update(current_price)
    new_window['-COMPANYNAME-'].update(companyName)

    call_scroll = 0     # determine row with strike price closest to current_price for calls
    for num in callList['Strike']:
        call_scroll += 1
        if float(num) > float(current_price):
            break

    put_scroll = 0      # determine row with strike price closest to current_price for puts
    for num in putList['Strike']:
        put_scroll += 1
        if float(num) > float(current_price):
            break

    new_window["-CALLTABLE-"].Widget.see(call_scroll-11)    #scroll to have current stock price near middle of table
    new_window["-PUTTABLE-"].Widget.see(put_scroll-11)



    # -------------------------------------------------------------------------------------------------------
    # - - - - - - - - - - - - - - - - - - - - - - EVENT LOOP - - - - - - - - - - - - - - - - - - - - - - - -
    # -------------------------------------------------------------------------------------------------------
    while True:
        # event, values = new_window.read()    <- original event check, only supports a single window
        window, event, values = sg.read_all_windows()

        row_colors = []                                 # highlight ITM calls
        for row, row_data in enumerate(callTableEntries):
            if float(row_data[9]) < current_price:
                row_colors.append((row, 'white smoke'))
            else:
                row_colors.append((row, sg.theme_background_color()))
        new_window["-CALLTABLE-"].update(row_colors=row_colors)

        row_colors = []                                  # highlight ITM puts
        for row, row_data in enumerate(putTableEntries):
            if float(row_data[0]) > current_price:
                row_colors.append((row, 'white smoke'))
            else:
                row_colors.append((row, sg.theme_background_color()))
        new_window["-PUTTABLE-"].update(row_colors=row_colors)

        if event == "Update Exp. Date":
            expDate = values["expirationDates"]
            urlExpirationCode = expirationDates.get(expDate)
            callTableEntries, putTableEntries = updateExpDate(ticker, urlExpirationCode)
            new_window["-CALLTABLE-"].update(callTableEntries)
            new_window["-PUTTABLE-"].update(putTableEntries)
            try:
                put_window.close()
            except:
                pass
            try:
                call_window.close()
            except:
                pass
            new_window.refresh()

        if event == "-CALLTABLE-":
            try:
                call_window.close()
            except:
                pass
            callRow = callTableEntries[values['-CALLTABLE-'][0]]
            greeks_layout = [
                [sg.Text('Delta:'), sg.Text('', key="DELTA")],
                [sg.Text('Gamma:'), sg.Text('', key="GAMMA")],
                [sg.Text('Vega:'), sg.Text('', key="VEGA")],
                [sg.Text('Theta:'), sg.Text('', key="THETA")],
                [sg.Text('Rho:'), sg.Text('', key="RHO")]
            ]
            transaction_buttons = [[sg.Button("Buy", key="buy_call", size=(5, 10)), sg.Button("Sell", key="sell_call", size=(5, 10))]]
            blackScholesText = [[sg.Text('', key="-BLACKSCHOLES-")]]
            bachelierText = [[sg.Text('', key="-BACHELIER-")]]
            callRightCol = [[sg.Frame(" Black-Scholes Price: ", blackScholesText)],
                            [sg.Frame("  Bachelier Price:  ", bachelierText)],
                            [sg.Frame(" Open Position: ", transaction_buttons)]]


            call_layout = [[sg.Frame(" Option Greeks: ", greeks_layout),sg.Column(callRightCol)]]
            x, y = pyautogui.position()
            call_window = sg.Window('Call Info',
                                    call_layout,
                                    size=(320, 180), keep_on_top=True, location=(x, y + 10),
                                    resizable=True, finalize=True, background_color='#e0f3f6')
            call_window.bind('<Configure>', "Event")
            expDate = values[
                          "expirationDates"] + " 16:00"  # expiration timing can vary, assuming 3pm CST on expiration date
            # https://www.schwab.com/learn/story/options-expiration-definitions-checklist-more
            expDate = datetime.strptime(expDate, "%B %d, %Y %H:%M")
            S = float(current_price)
            K = float(callRow[9])
            r = float(values["-RISKFREERATE-"])
            T = expDate - datetime.now()
            T = round(((T.days * 86400 + T.seconds)/3600)/(365*24),6 ) # calculate hours to expiration as a percent of year
            sigma = float(values["-HISVOLOUTPUT-"])
            d1, d2, bsPrice = oF.blackScholes(r, S, K, T, sigma, 'c')
            baPrice = oF.bachelier(r, S, K, T, sigma * S, 'c')
            call_window["-BLACKSCHOLES-"].update(round(bsPrice, 12))
            call_window["DELTA"].update(round(oF.option_delta(d1, 'c'),4))
            call_window["GAMMA"].update(round(oF.option_gamma(d1, S, T, sigma),4))
            call_window["VEGA"].update(round(oF.option_vega(d1, S, T),4))
            call_window["THETA"].update(round(oF.option_theta(d1, d2, S, K, T, r, sigma, 'c'),4))
            call_window["RHO"].update(round(oF.option_rho(d2, K, T, r, 'c'),4))
            call_window["-BACHELIER-"].update(round(baPrice, 12))

        if event == "-PUTTABLE-":
            try:
                put_window.close()
            except:
                pass
            putRow = putTableEntries[values['-PUTTABLE-'][0]]
            greeks_layout = [
                [sg.Text('Delta:'), sg.Text('', key="DELTA")],
                [sg.Text('Gamma:'), sg.Text('', key="GAMMA")],
                [sg.Text('Vega:'), sg.Text('', key="VEGA")],
                [sg.Text('Theta:'), sg.Text('', key="THETA")],
                [sg.Text('Rho:'), sg.Text('', key="RHO")],
            ]
            transaction_buttons = [[sg.Button("Buy", key="buy_put", size=(5, 10)), sg.Button("Sell", key="sell_put", size=(5, 10))]]
            blackScholesText = [[sg.Text('', key="-BLACKSCHOLES-")]]
            bachelierText = [[sg.Text('', key="-BACHELIER-")]]
            putRightCol = [[sg.Frame(" Black-Scholes Price: ", blackScholesText)],
                            [sg.Frame("  Bachelier Price:  ", bachelierText)],
                            [sg.Frame(" Open Position: ", transaction_buttons)]]
            put_layout = [[sg.Frame(" Option Greeks: ", greeks_layout), sg.Column(putRightCol)]]
            x, y = pyautogui.position()
            put_window = sg.Window('Put Info',
                                   put_layout,
                                   size=(320, 180), keep_on_top=True, location=(x, y + 10),
                                   resizable=True, finalize=True, background_color='#e0f3f6')
            put_window.bind('<Configure>', "Event")
            expDate = values[
                          "expirationDates"] + " 16:00"  # expiration timing can vary, assuming 3pm CST on expiration date
                                        # https://www.schwab.com/learn/story/options-expiration-definitions-checklist-more
            expDate = datetime.strptime(expDate, "%B %d, %Y %H:%M")
            S = float(current_price)
            K = float(putRow[0])
            r = float(values["-RISKFREERATE-"])
            T = expDate - datetime.now()
            T = round(((T.days * 86400 + T.seconds)/3600)/(365*24),6)  # calculate hours to expiration as a percent of year
            sigma = float(values["-HISVOLOUTPUT-"])
            d1, d2, bsPrice = oF.blackScholes(r, S, K, T, sigma, 'p')
            baPrice = oF.bachelier(r, S, K, T, sigma*S, 'p')
            put_window["-BLACKSCHOLES-"].update(round(bsPrice,12))
            put_window["DELTA"].update(round(oF.option_delta(d1, 'p'), 4))
            put_window["GAMMA"].update(round(oF.option_gamma(d1, S, T, sigma), 4))
            put_window["VEGA"].update(round(oF.option_vega(d1, S, T), 4))
            put_window["THETA"].update(round(oF.option_theta(d1, d2, S, K, T, r, sigma, 'p'), 4))
            put_window["RHO"].update(round(oF.option_rho(d2, K, T, r, 'p'), 4))
            put_window["-BACHELIER-"].update(round(baPrice, 12))

        if event == "Plot Stock Price":
            plotPriceAction(ticker)

        if event == "Plot Daily Returns":
            plotPercentChange(ticker)

        if event == 'Search':
            newTicker = values['-INPUT-']
            if newTicker is not None and newTicker != "":
                try:
                    put_window.close()
                except:
                    pass
                try:
                    call_window.close()
                except:
                    pass
                openOptionSheet = True
                new_window.close()
                break

        if event in (sg.WIN_CLOSED, 'Close'):
            try:
                if window == call_window:
                    call_window.close()
            except:
                pass
            try:
                if window == put_window:
                    put_window.close()
            except:
                pass

            if window == new_window:
                try:
                    put_window.close()
                except:
                    pass
                try:
                    call_window.close()
                except:
                    pass
                openOptionSheet = False
                newTicker = ''
                new_window.close()
                break

        if event == "sell_call":
            if float(callRow[7]) != 0:
                premium = callRow[7]
            else:
                premium = callRow[8]
            transaction = ['SELL', 'CALL', callRow[9], premium]
            positionTableEntries.append(transaction)
            new_window['-POSITIONTABLE-'].Update(values=positionTableEntries)

        if event == "buy_call":
            if float(callRow[6]) != 0:
                premium = callRow[6]
            else:
                premium = callRow[8]
            transaction = ['BUY', 'CALL', callRow[9], premium]
            positionTableEntries.append(transaction)
            new_window['-POSITIONTABLE-'].Update(values=positionTableEntries)

        if event == "buy_put":
            if float(putRow[3]) != 0:
                premium = putRow[3]
            else:
                premium = putRow[1]
            transaction = ['BUY', 'PUT', putRow[0], premium]
            positionTableEntries.append(transaction)
            new_window['-POSITIONTABLE-'].Update(values=positionTableEntries)

        if event == "sell_put":
            if float(putRow[2]) != 0:
                premium = putRow[2]
            else:
                premium = putRow[1]
            transaction = ['SELL', 'PUT', putRow[0], premium]
            positionTableEntries.append(transaction)
            new_window['-POSITIONTABLE-'].Update(values=positionTableEntries)

        if event == "-PLOTPAYOFF-":
            try:
                if window == call_window:
                    call_window.close()
            except:
                pass
            try:
                if window == put_window:
                    put_window.close()
            except:
                pass
            positionList = []
            for position in positionTableEntries:
                transactionType = position[0][0:1].lower()
                contractType = position[1][0:1].lower()
                strike = float(position[2])
                premium = float(position[3])
                positionTraits = {'op_type': contractType, 'strike': strike, 'tr_type': transactionType, 'op_pr': premium}
                positionList.append(positionTraits)
            op.multi_plotter(spot=current_price, spot_range=float(values['-UNDERLYINGVOL-']), op_list=positionList)

        if event == "-DELETEPOSITION-":
            rowToDelete = positionTableEntries[values["-POSITIONTABLE-"][0]]
            if values["-POSITIONTABLE-"]:
                del positionTableEntries[values["-POSITIONTABLE-"][0]]
                new_window['-POSITIONTABLE-'].Update(values=positionTableEntries)

        if event == "-DELETEALL-":
            positionTableEntries = []
            new_window['-POSITIONTABLE-'].Update(values=positionTableEntries)

        if event == "-CALCHISVOL-":
            dayCount = values["-HISTORICVOLINPUT-"]
            historicVol = round(getHistoricVol(ticker, float(dayCount)), 6)
            new_window["-HISVOLOUTPUT-"].update(historicVol)

    return openOptionSheet, newTicker.upper()
