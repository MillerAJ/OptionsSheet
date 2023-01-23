# OptionsSheet

This application is built with pySimpleGUI. The idea is to provide an environment where it is easy to intuitively explore/fiddle 
with options contracts, pricing models and plot basic options positions (i.e. long/short positions, strangles, butterflies, etc.)

Given a ticker, the program will webscrape available options contracts from yahooFinance. You'll be able to edit inputs like the risk free rate and the
number of days to consider when calculating historic volatility. 

Be careful with your inputs! I didn't add checks to make sure inputs were in the proper format so if you input a letter where a number is asked for it will likely crash the program! 

Other than that it's fairly simple and (I hope) easy to use, enjoy!
