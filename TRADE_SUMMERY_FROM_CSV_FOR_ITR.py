import pandas as pd

# Function to process the ledger and calculate P&L using FIFO
def calculate_pnl(ledger):
    # Sort the ledger by Date (important for FIFO calculation)
    ledger['Date'] = pd.to_datetime(ledger['Date'])
    ledger = ledger.sort_values(by='Date')

    # Initialize empty lists for storing results
    summary = []
    positions = {}

    # Loop through each row (trade)
    for _, row in ledger.iterrows():
        symbol = row['Symbol']
        qty = row['Qty']
        price = row['Price']
        transaction_type = row['Buy/Sell']

        # If it's a buy, add to positions
        if transaction_type.lower() == 'buy':
            if symbol in positions:
                positions[symbol].append({'qty': qty, 'price': price})
            else:
                positions[symbol] = [{'qty': qty, 'price': price}]

        # If it's a sell, calculate P&L
        elif transaction_type.lower() == 'sell':
            total_pnl = 0
            remaining_qty = qty

            while remaining_qty > 0:
                # Fetch the oldest buy position
                buy_position = positions[symbol][0]
                buy_qty = buy_position['qty']
                buy_price = buy_position['price']

                # If the sell quantity is more than the buy quantity, use up the entire buy position
                if remaining_qty >= buy_qty:
                    pnl = (price - buy_price) * buy_qty
                    total_pnl += pnl
                    remaining_qty -= buy_qty
                    # Remove the consumed buy position
                    positions[symbol].pop(0)
                else:
                    # Partial sell from the current position
                    pnl = (price - buy_price) * remaining_qty
                    total_pnl += pnl
                    positions[symbol][0]['qty'] -= remaining_qty
                    remaining_qty = 0

            # Add the summarized trade to the summary list
            summary.append({
                'Date': row['Date'],
                'Symbol': symbol,
                'Buy/Sell': 'Sell-Buy',
                'Quantity': qty,
                'Rate': price,
                'P&L': total_pnl
            })

    # Convert the summary to a DataFrame
    summary_df = pd.DataFrame(summary)
    return summary_df

# Load broker ledger data (CSV)
def load_ledger(file_path):
    return pd.read_csv(file_path)

# Main function to process the ledger and generate summary
def generate_trade_summary(file_path):
    # Load the broker ledger
    ledger = load_ledger(file_path)

    # Ensure the ledger has necessary columns
    required_columns = ['Date', 'Symbol', 'Buy/Sell', 'Qty', 'Price']
    if not all(col in ledger.columns for col in required_columns):
        raise ValueError(f"Ledger must contain the following columns: {', '.join(required_columns)}")

    # Calculate P&L and summarize trades
    trade_summary = calculate_pnl(ledger)

    # Output the trade summary to a new Excel file
    summary_file_path = "Trade_Summary.xlsx"
    with pd.ExcelWriter(summary_file_path, engine="xlsxwriter") as writer:
        trade_summary.to_excel(writer, sheet_name="Trade Summary", index=False)

    print(f"Trade summary saved to {summary_file_path}")

# Example usage
file_path = "path_to_your_upstox_ledger.csv"  # Replace this with the actual file path
generate_trade_summary(file_path)
