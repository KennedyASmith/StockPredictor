from yahooquery import Ticker
import random
import os
from datetime import datetime, timedelta


### USES TOP 1000 NET CHANGE, USA BASED, NON-ZERO MARKET CAP SYMBOLS ON NASDAQ

## ESG: More weight on the ESG
## 

## Total tested:  39
## Beta accuracy: 30.77%
## Market cap accuracy: 30.77%
## Growth vs value accuracy: 0.00%
## ESG accuracy: 15.38%
## Earnings surprise accuracy: 35.90%
## Sector accuracy: 7.69%

## Total tested:  42
## Beta accuracy: 42.86%
## Market cap accuracy: 28.57%
## Growth vs value accuracy: 0.00%
## ESG accuracy: 19.05%
## Earnings surprise accuracy: 54.76%
## Sector accuracy: 7.14%

# Determine whether to buy, sell, or hold based on the beta
def shouldBuyBeta(stock_info, t):
    try:
        beta = stock_info[t].get('beta')
    except Exception as e:
        return "n"
    if type(beta) != float:
        return "n"
    elif beta > 1:
        return "s" #High beta. It is considered more volatile than the market. Might want to sell. 
    elif beta < 1:
        return "b" #Low beta. It is considered less volatile than the market. Might want to buy.
    else:
        return "h" #The stock has a beta of 1, which is the same as the market. Might want to hold. 

# Determine whether to buy, sell, or hold based on the market cap
def shouldBuyMc(stock_info, t):
    try:
        market_cap = stock_info.get(t)['marketCap']
    except Exception as e:
        return "n" 
    if type(market_cap) != int:
        return "n"
    if market_cap < 5000000000:
        return "b" # Buy if market cap is less than $5 billion
    elif market_cap > 15000000000:
        return "s" # Sell if market cap is greater than $15 billion
    else:
        return "h" # Hold if market cap is between $5 billion and $15 billion

# Determine whether to buy, sell, or hold based on the ESG score
def shouldBuyESG(ticker, t):
    try:
        data = ticker.esg_scores.get(t)
        esg_score = data['totalEsg']
    except Exception as e:
        return "n"
    if type(esg_score) != float:
        print("ESG Type ", type(esg_score))
        return "n"
    elif esg_score >= 70:
        return "b" # Buy if ESG score is 70 or higher
    elif esg_score < 50:
        return "s" # Sell if ESG score is less than 50
    else:
        return "h" # Hold if neither buying nor selling conditions are met

# Determine whether to buy, sell, or hold based on the earnings surprise
def shouldBuyEarningsSurprise(ticker, symbol):
    hist = ticker.earning_history

    try:
        earnings_surprise = hist['surprisePercent'].mean();
    except Exception as e:
        return "n"
    if earnings_surprise is None:
        return "n"
    elif earnings_surprise > 0:
        return "b" # Buy if earnings surprise is positive
    elif earnings_surprise < 0:
        return "s" # Sell if earnings surprise is negative
    else:
        return "h" # Hold if earnings surprise is zero

# Determine whether to buy, sell, or hold based on the GICS sector
def shouldBuySector(ticker, t):
    asset = ticker.asset_profile;
    try:
        sector = asset[t]["sector"];
    except Exception as e:
        return "n" 
    if type(sector) != str:
        print("Sector Type ", type(sector))
        return "n"
    elif sector == "Technology":
        return "b" # Buy if the stock is in the Technology sector
    elif sector == "Utilities" or sector == "Consumer Staples":
        return "s" # Sell if the stock is in the Utilities or Consumer Staples sectors
    else:
        return "h" # Hold if neither buying nor selling conditions are met

def get_ticker_symbols():
    ticker_symbols = []
    folder_path = os.path.dirname(os.path.abspath(__file__))

    # construct the path to the symbols file
    symbols_file_path = os.path.join(folder_path, 'ticker_symbols.txt')

    with open(symbols_file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            ticker_symbols.append(line.strip())

    return ticker_symbols

def build_string(items):
    return ", ".join(items)

def buildAccuracyTable(iterations, years):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years) # Get data for past year
    
    # Define a large list of tickers to analyze
    all_tickers = get_ticker_symbols()
    random_tickers = random.sample(all_tickers, iterations)

    # Initialize counters for accuracy of each method
    beta_correct = 0
    mc_correct = 0
    esg_correct = 0
    earnings_surprise_correct = 0
    sector_correct = 0
    total = 0
    
    unavailable_data = [];

    # Iterate over the tickers and calculate the accuracy of each method
    for t in random_tickers:


        # Build a ticker object from the symbol string t
        ticker = Ticker(t)

        price_data = ticker.history(start=start_date, end=end_date)

        # Calculate the price change over the past 10 years
        try:
            start_price = price_data.iloc[0]['close']
            end_price = price_data.iloc[-1]['close']
            price_change = end_price - start_price
        except IndexError:
            unavailable_data.append(t)
            continue

        ## Get info for this stock
        stock_data = ticker.summary_detail
        
        # Use each method to predict whether to buy, sell, or hold the stock
        beta_prediction = shouldBuyBeta(stock_data, t)
        mc_prediction = shouldBuyMc(stock_data, t)
        esg_prediction = shouldBuyESG(ticker, t)
        earnings_surprise_prediction = shouldBuyEarningsSurprise(ticker, t)
        sector_prediction = shouldBuySector(ticker, t)

        # Print the prediction associated with tested symbol
        #print("\n------------------------------")
        #print("Testing Symbol: ", t)
        #print("Price change: ", price_change)
        #print("Beta: ", beta_prediction)
        #print("MC: ", mc_prediction)
        #print("ESG: ", esg_prediction)
        #print("ESP: ", earnings_surprise_prediction)
        #print("Sector: ", sector_prediction)

        # Compare each prediction to the actual change in stock price and update counters
        if beta_prediction == "b" and price_change > 0:
            beta_correct += 1
        elif beta_prediction == "s" and price_change < 0:
            beta_correct += 1
        
        if mc_prediction == "b" and price_change > 0:
            mc_correct += 1
        elif mc_prediction == "s" and price_change < 0:
            mc_correct += 1
        
        if esg_prediction == "b" and price_change > 0:
            esg_correct += 1
        elif esg_prediction == "s" and price_change < 0:
            esg_correct += 1
        
        if earnings_surprise_prediction == "b" and price_change > 0:
            earnings_surprise_correct += 1
        elif earnings_surprise_prediction == "s" and price_change < 0:
            earnings_surprise_correct += 1

        if sector_prediction == "b" and price_change > 0:
            sector_correct += 1
        elif sector_prediction == "s" and price_change < 0:
            sector_correct += 1

        total += 1

    # Calculate and print the accuracy of each method
    print("------------------------------")
    print("Total tested symbols: ", total, " of ", len(random_tickers));
    if len(unavailable_data) > 0:
        print("Data was unavailable for symbols: \n[", build_string(unavailable_data), "]\n")
    print(f"Beta accuracy: {beta_correct / total:.2%}")
    print(f"Market cap accuracy: {mc_correct / total:.2%}")
    print(f"ESG accuracy: {esg_correct / total:.2%}")
    print(f"Earnings surprise accuracy: {earnings_surprise_correct / total:.2%}")
    print(f"Sector accuracy: {sector_correct / total:.2%}")
    print("------------------------------")

    accuracies = {
            "Beta": (beta_correct/total),
            "Market Cap": (mc_correct / total),
            "ESG": (esg_correct / total),
            "Earnings Surprise": (earnings_surprise_correct / total),
            "Sector": (sector_correct / total)
    }

    return accuracies

def join_with_commas(list_of_strings):
    if len(list_of_strings) == 0:
        return ""  # return empty string for empty list
    elif len(list_of_strings) == 1:
        return list_of_strings[0]  # return single string as is
    elif len(list_of_strings) == 2:
        return f"{list_of_strings[0]} and {list_of_strings[1]}"  # join two strings with "and"
    else:
        # join all but last string with commas, then add "and" before last string
        return f"{', '.join(list_of_strings[:-1])}, and {list_of_strings[-1]}"

def get_predictions(symbol):
        # Build a ticker object from the symbol string t
        ticker = Ticker(symbol)

        ## Get info for this stock
        stock_data = ticker.summary_detail

        return {
            "Beta": shouldBuyBeta(stock_data, symbol),
            "Market Cap": shouldBuyMc(stock_data, symbol),
            "ESG": shouldBuyESG(ticker, symbol),
            "Earnings Surprise": shouldBuyEarningsSurprise(ticker, symbol),
            "Sector": shouldBuySector(ticker, symbol)
        }

def get_weighted_results(predictions, accuracies):
    beta_prediction = predictions["Beta"]
    mc_prediction = predictions["Market Cap"]
    esg_prediction = predictions["ESG"]
    earnings_surprise_prediction = predictions["Earnings Surprise"]
    sector_prediction = predictions["Sector"]
    return {
            "Beta": accuracies["Beta"] * 
                (1 if beta_prediction == "b" else (-1 if beta_prediction  == "s" else 0)),
            "Market Cap": accuracies["Market Cap"] * 
                (1 if mc_prediction == "b" else (-1 if mc_prediction == "s" else 0)),
            "ESG": accuracies["ESG"] * 
                (1 if esg_prediction == "b" else (-1 if esg_prediction == "s" else 0)),
            "Earnings Surprise": accuracies["Earnings Surprise"] * 
                (1 if earnings_surprise_prediction == "b" else (-1 if earnings_surprise_prediction == "s" else 0)),
            "Sector": accuracies["Sector"] * 
                (1 if sector_prediction == "b" else (-1 if sector_prediction == "s" else 0))
        }

# Calculate weighted average using percentage weights
def get_weighted_certainty(weighted_results):
    return (
                        (weighted_results["Beta"] +
                        weighted_results["Market Cap"] +
                        weighted_results["ESG"] +
                        weighted_results["Earnings Surprise"] +
                        weighted_results["Sector"])/5
                        );

# Finds the average of the numerical values in an array
def average(numbers):
    if len(numbers) == 0:
        return None  # return None for empty array
    else:
        return sum(numbers) / len(numbers)

def determine_stock_decision(portfolio, symbol, accuracies):
    
        predictions = get_predictions(symbol)
        weighted_results = get_weighted_results(predictions, accuracies)
        weighted_certainty  = get_weighted_certainty(weighted_results)

        # Find the average certainty for this simulation
        print("Gathering average simulation certainty for 50 symbols...")
        all_tickers = get_ticker_symbols()
        random_tickers = random.sample(all_tickers, 50)
        certainties = []
        for t in random_tickers:
            pred = get_predictions(t)
            res = get_weighted_results(pred, accuracies)
            certainty = get_weighted_certainty(res)
            certainties.append(certainty)
        average_certainty = average(certainties)

        buys = []; sells = []; holds = []
        for factor, weight in weighted_results.items():
            if weight > 0:
                buys.append(factor)
            if weight < 0:
                sells.append(factor)
            else:
                holds.append(factor)

        certainty_difference = (abs(weighted_certainty)/abs(average_certainty)) - 1

        print("Weighted Certainty: ", abs(certainty_difference))

        if(portfolio == "growth"):
            risk = 0.2
        else:
            risk = 0.5

        if weighted_certainty > 0 and abs(certainty_difference) > risk:
            decision = "buy"
        elif weighted_certainty < 0 and abs(certainty_difference) > risk:
            decision = "sell"
        else:
            decision = "hold"

        print("\n")
        print(symbol, " factor evaluation: ")
        print("Beta: ", predictions["Beta"])
        print("MC: ", predictions["Market Cap"])
        print("ESG: ", predictions["ESG"])
        print("ESP: ", predictions["Earnings Surprise"])
        print("Sector: ", predictions["Sector"], "\n")

        print("Factor Weights: ")
        print("Beta:", weighted_results["Beta"])
        print("Market Cap:", weighted_results["Market Cap"])
        print("ESG:", weighted_results["ESG"])
        print("Earnings Surprise:", weighted_results["Earnings Surprise"])
        print("Sector:", weighted_results["Sector"])
        print("\nCertainties: ")
        print(f"Decision Certainty: {abs(weighted_certainty):.2%}")
        print(f"Average Certainty: {abs(average_certainty):.2%}")
        print(f"Difference: {certainty_difference:.2%}")

        print("\nFinal Decision: ", decision)

        print("\n------ Explanation ------")
        print(f"According to this program's methodology, the best option for a {portfolio} portfolio would be to {decision} {symbol}.")
        print("Here are reasons that contribute to that decision:\n")
        if portfolio == "esg":
            print("- Since this evaluation is for an ESG portfolio, the values of all other factors are decreased by 75% to lean in favor of ESG decisions")
            print("  The simulation utilizes 10 years of data, and requires a decision certainty of 50% to reduce risk.")
        elif portfolio == "income":
            print("- Since this evaluation is for an income portfolio, the simulation utilizes the average of 10 years of data")
            if (decision == "sell") or (decision == "buy"):
                print(f"  and recommends to {decision} only because the decision certainty was 50% more certain than the average certainty found in simulation.")
            else:
                print("  and recommends to hold because the decision certainty was not at least 50% more certain than the average certainty found in simulation.")
            print("  These values are altered to minimize risk.")
        else:
            print("- Since this evaluation is for an growth portfolio, the simulation utilizes only 1 year of data to shorten the intended span of investment, increasing risk.")
            if (decision == "sell") or (decision == "buy"):
                print(f"  and recommends to {decision} because the decision certainty was at least 20% more certain than the average certainty found in simulation.")
            else:
                print("  and recommends to hold because the decision certainty was not at least 20% more certain than the average certainty found in simulation.")
            print("  These values are altered to maximize growth.")
        if decision == "sell":
            print("- The recommendation from",
            join_with_commas(sells), "suggests that the best option is to sell")
            if(len(buys) > 0):
                print("  Although the recommendation from", join_with_commas(buys), "suggests that the best option is to buy,")
                print("  the indication of", join_with_commas(sells), " weighs in favor of the decision to sell.")
        elif decision == "buy":
            print("- The recommendation from",
            {join_with_commas(buys)}, "suggests that the best option is to buy")
            if(len(sells) > 0):
                print("  Although the recommendation from", join_with_commas(sells), "suggests that the best option is to sell.")
                print("  the indication of", join_with_commas(sells), " weighs in favor of the decision to buy.")
        else:
            if len(sells) > 0 and len(buys) > 0:
                print("- Despite the decision to hold, the recommendations of", join_with_commas(sells), "indicated the best option was to sell")
                print("  and ", join_with_commas(buys), " indicated the best option was to buy. These recommendations were all determined too risky for the portfolio.")
            elif len(sells) > 0:
                print("- Despite the decision to hold, the recommendation of", join_with_commas(sells), "indicated the best option was to sell.")
                print("  However, this option was determined too risky for the portfolio.")
            elif len(buys) > 0:
                print("- Despite the decision to hold, the recommendation of", join_with_commas(buys), "indicated the best option was to buy.")
                print("  However, this option was determined too risky for the portfolio.")
        print("\n")
        
        return decision


def invest(ticker, client=False):
    iterations = 150
    years = 0

    explanation = "\n\n\n-------------------------------\n"
    explanation += "Evaluating " + ticker + " for";
    if client == "esg":
        explanation += " an ESG"
        years = 10
    elif client == "income":
        explanation += " an Income"
        years = 10
    else:
        client = "growth"
        explanation += " a Growth"
        years = 1
    explanation += " portfolio. \n\nRunning simulation to gather accuracy of factors..."
    print(explanation)

    print(f"Simulation size: {iterations} symbols")

    accuracies = buildAccuracyTable(iterations, years)

    for factor, accuracy in accuracies.items():
        if factor == "esg":
            continue  # skip this factor
        elif abs(accuracy) > 0:
            accuracies[factor] = accuracy - (0.75 * accuracy)  # decrease weight by 75%

    decision = determine_stock_decision(client, ticker, accuracies)
    return decision 

invest("FDR.MC", "esg")