import threading
import time
import json
from datetime import datetime, timedelta
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os


class IBapi(EWrapper, EClient):
    """
    IBapi class inherits from EWrapper and EClient to handle IB API callbacks and requests.
    """

    def __init__(self, filename):
        EClient.__init__(self, self)
        self.data = []  # Initialize list to store historical data
        self.data_ready = False
        self.filename = filename
        self.error_occurred = False  # New flag to track errors
        self.error_message = ""      # Store error message

    def historicalData(self, reqId, bar):
        """
        Callback for historical data. Appends each bar to self.data.
        """
        # Print received data (optional)
        print(f'Time: {bar.date} Open: {bar.open} High: {bar.high} '
              f'Low: {bar.low} Close: {bar.close} Volume: {bar.volume}')

        # Create data record as a dictionary
        record = {
            "date": bar.date,  # Unix timestamp as string
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume
        }

        # Append record to data list
        self.data.append(record)

    def historicalDataEnd(self, reqId, start, end):
        """
        Callback indicating the end of historical data reception.
        """
        self.data_ready = True
        print(f'Historical data received from {start} to {end}')

    def write_data_to_parquet(self):
        """
        Writes accumulated data to a Parquet file with Snappy compression.
        """
        if not self.data:
            print("No data to write to Parquet.")
            return

        # Create a DataFrame from the accumulated data
        df = pd.DataFrame(self.data)

        # Convert 'date' to datetime
        try:
            df['timestamp'] = pd.to_datetime(df['date'].astype(int), unit='s')  # Convert Unix timestamp to datetime
            df.drop('date', axis=1, inplace=True)
        except Exception as e:
            print(f"Error converting 'date' to datetime: {e}")
            df['timestamp'] = pd.NaT  # Assign Not-a-Time if conversion fails

        # Reorder columns for better readability
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

        # Write to Parquet with Snappy compression
        table = pa.Table.from_pandas(df)

        if os.path.exists(self.filename):
            # If the file exists, append to it
            with pq.ParquetWriter(self.filename, table.schema, compression='snappy', use_dictionary=True) as writer:
                writer.write_table(table)
        else:
            # If the file does not exist, create it
            pq.write_table(table, self.filename, compression='snappy')

        print(f"Data appended to Parquet file: {self.filename}")

    def error(self, reqId: int, errorCode: int, errorString: str, advancedOrderRejectJson = ""):
        """Handle API errors"""
        print(f"Error. Id: {reqId} Code: {errorCode} Msg: {errorString}")
        
        # Check for HMDS query error or other specific errors
        if errorCode == 162 and "HMDS query returned no data" in errorString:
            self.error_occurred = True
            self.error_message = errorString
            self.data_ready = True  # Set to True to break the waiting loop
        
        # Add other specific error codes if needed
        elif errorCode in [162, 200, 354, 2106]:  # Common historical data error codes
            self.error_occurred = True
            self.error_message = errorString
            self.data_ready = True


def run_loop(app):
    """
    Runs the IB API message loop.
    """
    app.run()


def request_historical_data(app, contract, endDateTime, duration='1 D', bar_size='1 min', what_to_show='TRADES'):
    """
    Requests historical data from IB API.

    Parameters:
    - app: Instance of IBapi.
    - contract: IB Contract object.
    - endDateTime: End datetime for the data request.
    - duration: Duration string (e.g., '1 D' for one day).
    - bar_size: Size of each bar (e.g., '1 min').
    - what_to_show: Data type to show (e.g., 'BID').
    """
    app.data = []
    app.data_ready = False
    app.error_occurred = False  # Reset error flag
    app.error_message = ""      # Reset error message

    # Send historical data request
    app.reqHistoricalData(
        reqId=101,
        contract=contract,
        endDateTime=endDateTime,
        durationStr=duration,
        barSizeSetting=bar_size,
        whatToShow=what_to_show,
        useRTH=0,
        formatDate=2,
        keepUpToDate=False,
        chartOptions=[]
    )
    
    # Wait until data is ready or timeout after 60 seconds
    start_wait_time = time.time()
    while not app.data_ready and time.time() - start_wait_time < 60:
        time.sleep(1)

    if app.error_occurred:
        print(f"Skipping interval due to error: {app.error_message}")
        return False

    if not app.data_ready:
        print(f"Error: Data not received for {endDateTime}")
        return False

    return True


def main():
    """
    Main function to collect historical data and save it to a Parquet file.
    """
    filename = 'all_data.parquet'  # Parquet file

    # Initialize IB API client
    app = IBapi(filename)
    #app.connect("10.0.0.237", 4002, 123)  # Replace with your IB Gateway/TWS IP and port
    app.connect('127.0.0.1', 7497, 123) # THIS IS FOR IBKR TWS, THIS IS FOR TESTING PURPOSES ONLY
    #app = IBapi(filename)
    # app.connect("192.168.1.19", 4002, 123)  # Replace with your IB Gateway/TWS IP and port
    #app.connect('127.0.0.1', 7497, 123)  # THIS IS FOR IBKR TWS, THIS IS FOR TESTING PURPOSES ONLY

    # Start the IB API message loop in a separate thread
    api_thread = threading.Thread(target=run_loop, args=(app,), daemon=True)
    api_thread.start()

    time.sleep(1)  # Allow time for connection to establish

    # Define the contract (e.g., Tesla stock)
    contract = Contract()
    contract.symbol = "MNQ"
    contract.secType = "FUT"
    contract.exchange = "CME"
    contract.currency = "USD"
    contract.lastTradeDateOrContractMonth = "20241220"
    contract.includeExpired = True

    # Define the date range for historical data
    start_date = datetime.strptime('2023-09-23', '%Y-%m-%d')
    end_date = datetime.strptime('2023-10-23', '%Y-%m-%d')

    current_date = start_date
    while current_date < end_date:
        # Define the end datetime for the current request
        current_end = current_date + timedelta(hours=1)
        endDateTime = current_end.strftime('%Y%m%d-%H:%M:%S')  # Format: YYYYMMDD-HH:MM:SS

        print(f"Requesting data for interval: {current_date} to {current_end}")

        # Request data for the current hour
        success = request_historical_data(
            app,
            contract,
            endDateTime,
            duration='3600 S',  # Duration string
            bar_size='5 secs',  # Bar size
            what_to_show='TRADES'  # Data type
        )

        if success:
            # Write data to Parquet file after each hour of data is received
            app.write_data_to_parquet()
        
        # Always advance to next hour, regardless of success or failure
        current_date += timedelta(hours=1)
        
        # Add a small delay between requests to avoid overwhelming the API
        time.sleep(1)

    # Disconnect from IB API
    app.disconnect()
    print("Disconnected from IB API")


if __name__ == "__main__":
    main()
