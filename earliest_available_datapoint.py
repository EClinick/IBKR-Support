import threading
import time
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from datetime import datetime

class IBapi(EWrapper, EClient):
    """
    IBapi class inherits from EWrapper and EClient to handle IB API callbacks and requests.
    """

    def __init__(self):
        EClient.__init__(self, self)
        self.earliest_data_point = None  # Initialize variable to store earliest data point

    def headTimestamp(self, reqId: int, headTimestamp: str):
        """
        Callback for the earliest available data point.
        """
        self.earliest_data_point = headTimestamp
        print(f"HeadTimestamp. ReqId: {reqId}, HeadTimeStamp: {headTimestamp}")

def run_loop(app):
    """
    Runs the IB API message loop.
    """
    app.run()

def request_earliest_data_point(app, contract, what_to_show='TRADES'):
    """
    Requests the earliest available data point from IB API.

    Parameters:
    - app: Instance of IBapi.
    - contract: IB Contract object.
    - what_to_show: Data type to show (e.g., 'TRADES').

    Returns:
    - The earliest available data point as a string.
    """
    app.earliest_data_point = None  # Reset the earliest data point

    # Send request for the earliest data point
    app.reqHeadTimeStamp(1, contract, what_to_show, 0, 1)

    # Wait until the earliest data point is received or timeout after 60 seconds
    start_wait_time = time.time()
    while app.earliest_data_point is None and time.time() - start_wait_time < 60:
        time.sleep(1)

    if app.earliest_data_point is None:
        print("Error: Earliest data point not received")
        return None

    return app.earliest_data_point

def main():
    """
    Main function to request the earliest available data point.
    """
    # Initialize IB API client
    app = IBapi()
    #app.connect('10.0.0.237', 4002, 123)  # THIS IS FOR IBKR TWS, THIS IS FOR TESTING PURPOSES ONLY
    app.connect('127.0.0.1', 7497, 123)
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
    contract.localSymbol="MNQZ4"
    #contract.lastTradeDateOrContractMonth = "20241220"
    #contract.includeExpired = True

    # Request the earliest available data point
    earliest_data_point = request_earliest_data_point(app, contract, what_to_show='TRADES')
    if earliest_data_point:
        print(f"Earliest available data point: {earliest_data_point}")
        #convert to datetime
        earliest_data_point = datetime.strptime(earliest_data_point, "%Y%m%d %H:%M:%S")
        print(f"Earliest available data point (datetime): {earliest_data_point}")

    # Disconnect from IB API
    app.disconnect()
    print("Disconnected from IB API")

if __name__ == "__main__":
    main()
