
# ___________________________________________________________________________________________________________________ #
"""
This script is designed for educational and entertainment purposes only. This script should not be used/taken as
financial advice. When investing it is always recommended to do your own outside research and/or to consult a
professional.

Data collected to make this model possible was collected from Financial Modeling Prep. They have lots of awesome FREE
datasets available. Link to their developer page -> https://financialmodelingprep.com/developer/docs/

This script is still a work in progress for me but I encourage any viewer to freely borrow/take from my project and
make it your own.
"""

# ______________________________________________ Imports ____________________________________________________________ #
import requests
import os
import pandas as pd
import csv
import numpy_financial as npf

# ____________________________________________ Preferences  _________________________________________________________ #
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# ______________________________________________ Variables __________________________________________________________ #
fin_model_api_key = os.environ.get("FMP_KEY")

# Ultimately these will be user inputs or web scrapes
treasury_rate = 3.5
company = "AAPL"
wacc = 8.0
tgr = 2.5
final_year_rev_growth = 7.0
final_year_ebit_percent = 27.5
final_year_tax_percent = 17.5

# Financial modeling prep api urls
IS_URL = f"https://financialmodelingprep.com/api/v3/income-statement/{company}?" \
      f"limit=120&" \
         f"apikey={fin_model_api_key}"

BS_URL = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{company}?" \
         f"limit=120&" \
         f"apikey={fin_model_api_key}"

CF_URL = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{company}?" \
         f"limit=120&" \
         f"apikey={fin_model_api_key}"

is_data = requests.get(IS_URL).json()
cf_data = requests.get(CF_URL).json()
bs_data = requests.get(BS_URL).json()

shares_outstanding = []
cash = []
debt = []

# Basis for data structure
dcf_model = {"Year": [],
             "Revenue": [],
             "%Growth": [11.6],
             "EBIT": [],
             "EBIT%Rev": [],
             "Taxes": [],
             "Taxes%EBIT": [],
             "D&A": [],
             "D&A%Rev": [],
             "CapEx": [],
             "CapEx%Rev": [],
             "Change in WC": [],
             "NWC%Rev": []}

# __________________________________________ Populating Model _______________________________________________________ #
for i in reversed(range(len(cf_data))):
    dcf_model["Year"].append(int(cf_data[i]["calendarYear"]))
    dcf_model["CapEx"].append(int(cf_data[i]["capitalExpenditure"]))
    dcf_model["Change in WC"].append(int(cf_data[i]["changeInWorkingCapital"]))
    dcf_model["D&A"].append(int(cf_data[i]["depreciationAndAmortization"]))

for i in reversed(range(len(is_data))):
    dcf_model["EBIT"].append(int(is_data[i]["incomeBeforeTax"]) + int(is_data[i]["interestExpense"]))
    dcf_model["Taxes"].append(int(is_data[i]["incomeTaxExpense"]))
    dcf_model["Revenue"].append(int(is_data[i]["revenue"]))
    shares_outstanding.append(int(is_data[i]["weightedAverageShsOutDil"]))

for i in reversed(range(len(bs_data))):
    cash.append(int(bs_data[i]["cashAndCashEquivalents"]))
    debt.append(int(bs_data[i]["shortTermDebt"]) + int(bs_data[i]["longTermDebt"]))

for i in range(0, len(dcf_model["EBIT"])):
    dcf_model["EBIT%Rev"].append(round((dcf_model["EBIT"][i] / dcf_model["Revenue"][i]) * 100, 2))
    dcf_model["Taxes%EBIT"].append(round((dcf_model["Taxes"][i] / dcf_model["EBIT"][i]) * 100, 2))
    dcf_model["D&A%Rev"].append(round((dcf_model["D&A"][i] / dcf_model["Revenue"][i]) * 100, 2))
    dcf_model["CapEx%Rev"].append(round((dcf_model["CapEx"][i] / dcf_model["Revenue"][i]) * 100, 2))
    dcf_model["NWC%Rev"].append(round((dcf_model["Change in WC"][i] / dcf_model["Revenue"][i]) * 100, 2))

for i in range(1, len(dcf_model["Revenue"])):
    dcf_model["%Growth"].append(round(((dcf_model["Revenue"][i] - dcf_model["Revenue"][i-1])/dcf_model["Revenue"][i])
                                      * 100, 2))

# Creating pandas DF
df = pd.DataFrame(dcf_model)

dna_avg = round(sum(dcf_model["D&A%Rev"][-3:]) / 3, 2)

nwc_percent_avg = sum(dcf_model["NWC%Rev"]) / len(dcf_model["NWC%Rev"])
capex_percent_avg = sum(dcf_model["CapEx%Rev"]) / len(dcf_model["CapEx%Rev"])

for _ in range(5):
    dcf_model["D&A%Rev"].append(round(dna_avg, 2))
    dcf_model["NWC%Rev"].append(round(nwc_percent_avg, 2))
    dcf_model["CapEx%Rev"].append(round(capex_percent_avg, 2))

dcf_model['%Growth'].append(df["%Growth"].mean())
dcf_model["Revenue"].append((1 + (dcf_model["%Growth"][-1] / 100)) * dcf_model["Revenue"][-1])
dcf_model["Year"].append(int(dcf_model["Year"][-1] + 1))

for i in range(4):
    dcf_model["%Growth"].append(round(dcf_model["%Growth"][-1] - (dcf_model["%Growth"][-1] - final_year_rev_growth)
                                      / 5, 2))
    dcf_model["Revenue"].append(round((1 + (dcf_model["%Growth"][-1]/100)) * dcf_model["Revenue"][-1], 2))
    dcf_model["Year"].append(round((dcf_model["Year"][-1] + 1), 0))

for i in range(5):
    dcf_model["EBIT%Rev"].append(dcf_model["EBIT%Rev"][-1] - (dcf_model["EBIT%Rev"][-1] - final_year_ebit_percent) / 5)
    dcf_model["EBIT"].append(round((dcf_model["EBIT%Rev"][-1]/100) * dcf_model["Revenue"][5 + i], 2))

    dcf_model["Taxes%EBIT"].append(dcf_model["Taxes%EBIT"][-1] - (dcf_model["Taxes%EBIT"][-1] - final_year_tax_percent)
                                   / 5)
    dcf_model["Taxes"].append(round((dcf_model["Taxes%EBIT"][-1] / 100) * dcf_model["EBIT"][5 + i], 2))

    dcf_model["D&A"].append(round((dcf_model["D&A%Rev"][-1] / 100) * dcf_model["Revenue"][5 + i], 2))

    dcf_model["CapEx"].append(round((dcf_model["CapEx%Rev"][-1] / 100) * dcf_model["Revenue"][5 + i], 2))

    dcf_model["Change in WC"].append(round((dcf_model["NWC%Rev"][-1] / 100) * dcf_model["Revenue"][5 + i], 2))

df = pd.DataFrame(dcf_model).T

# Dataframe output to csv file
df.to_csv('output.csv', header=False)

# ______________________________________________ Analysis ___________________________________________________________ #
fcf = []
for i in range(1, 6):
    fcf.append(round((dcf_model["EBIT"][-i]-dcf_model["Taxes"][-i]) + dcf_model["D&A"][-i] + dcf_model["CapEx"][-i] +
               dcf_model["Change in WC"][-i], 2))

fcf = list(reversed(fcf))

discount_fcf = []
for i in range(len(fcf)):
    discount_fcf.append(round(-1 * (npf.pv((treasury_rate / 100), nper=i+1, pmt=0, fv=fcf[i], when='end')), 2))

terminal_value = round(fcf[-1] * (1 + (tgr / 100)) / ((wacc / 100) - (tgr / 100)), 2)

pv_terminal_value = round(-1 * (npf.pv((treasury_rate / 100), nper=5, pmt=0, fv=terminal_value, when='end')), 2)

enterprise_value = sum(discount_fcf) + pv_terminal_value

equity_value = enterprise_value + cash[-1] - debt[-1]

implied_share_price = round(equity_value / shares_outstanding[-1], 2)

# Terminal output for quick analysis
print(f"Discounting FCF for the next 5 years derives an implied share price of: ${implied_share_price} for {company}.")

# __________________________________________ Building the Output ____________________________________________________ #
fcf_row = ["FCF", "___", "___", "___", "___", "___", fcf[0], fcf[1], fcf[2], fcf[3], fcf[4]]

dfcf_row = ["Discount FCF", "___", "___", "___", "___", "___", discount_fcf[0], discount_fcf[1], discount_fcf[2],
            discount_fcf[3], discount_fcf[4]]

buffer_row = ["___", "___", "___", "___", "___", "___", "___", "___", "___", "___", "___"]

terminal_row = ["___", "___", "___", "___", "___", "___", "___", "___", "___", "Terminal Value: ", terminal_value]

pv_terminal_row = ["___", "___", "___", "___", "___", "___", "___", "___", "___", "PV Terminal Value: ",
                   pv_terminal_value]

enterprise_value_row = ["___", "___", "___", "___", "___", "___", "___", "___", "___", "Enterprise Value: ",
                        enterprise_value]

cash_row = ["___", "___", "___", "___", "___", "___", "___", "___", "___", "(+) Cash: ", cash[-1]]

debt_row = ["___", "___", "___", "___", "___", "___", "___", "___", "___", "(-) Debt: ", debt[-1]]

equity_value_row = ["___", "___", "___", "___", "___", "___", "___", "___", "___", "Equity Value: ", equity_value]

shares_outstanding_row = ["___", "___", "___", "___", "___", "___", "___", "___", "___", "Outstanding Shares: ",
                          shares_outstanding[-1]]

implied_share_price_row = ["___", "___", "___", "___", "___", "___", "___", "___", "___", "Implied Share Price",
                           implied_share_price]

# Final output to 'output.csv' file
with open("output.csv", "a") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows([fcf_row, dfcf_row, buffer_row, terminal_row, pv_terminal_row, enterprise_value_row, cash_row,
                      debt_row, equity_value_row, shares_outstanding_row, implied_share_price_row])
