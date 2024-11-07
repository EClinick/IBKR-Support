import threading
import time
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


class IBapi(EWrapper, EClient):
    """
    IBapi class inherits from EWrapper and EClient to handle IB API callbacks and requests.
    """
    def __init__(self):
        EClient.__init__(self, self)
        self.data_ready = False

    def contractDetails(self, reqId, contractDetails):
        """
        Callback for receiving contract details.
        """
        super().contractDetails(reqId, contractDetails)
        print(f"\nContract Details (Request ID: {reqId}):")
        print(f"  conId: {contractDetails.contract.conId}")
        print(f"  Symbol: {contractDetails.contract.symbol}")
        print(f"  SecType: {contractDetails.contract.secType}")
        print(f"  Expiry: {contractDetails.contract.lastTradeDateOrContractMonth}")
        print(f"  Exchange: {contractDetails.contract.exchange}")
        print(f"  Currency: {contractDetails.contract.currency}")
        print(f"  Local Symbol: {contractDetails.contract.localSymbol}")
        print(f"  Description: {contractDetails.longName}")
        print(f"  Multiplier: {contractDetails.contract.multiplier}")

        # Format and print trading hours in a more readable way
        print("\n  Trading Hours:")
        trading_periods = contractDetails.tradingHours.split(';')
        for trading_period in trading_periods:
            parts = trading_period.split(':', 1)
            date = parts[0]
            hours = parts[1] if len(parts) > 1 else 'CLOSED'
            print(f"    Date: {date}, Hours: {hours}")

        # Format and print liquid hours in a more readable way
        print("\n  Liquid Hours:")
        liquid_periods = contractDetails.liquidHours.split(';')
        for liquid_period in liquid_periods:
            parts = liquid_period.split(':', 1)
            date = parts[0]
            hours = parts[1] if len(parts) > 1 else 'CLOSED'
            print(f"    Date: {date}, Hours: {hours}")

    def contractDetailsEnd(self, reqId):
        """
        Callback indicating the end of contract details reception.
        """
        self.data_ready = True
        print(f"\nEnd of contract details for Request ID: {reqId}")


def run_loop(app):
    """
    Runs the IB API message loop.
    """
    app.run()


def main():
    """
    Main function to request contract details for MNQ futures.
    """
    # Initialize IB API client
    app = IBapi()
    app.connect('127.0.0.1', 7497, 123)  # Connect to TWS or IB Gateway

    # Start the IB API message loop in a separate thread
    api_thread = threading.Thread(target=run_loop, args=(app,), daemon=True)
    api_thread.start()

    time.sleep(1)  # Allow time for connection to establish

    # Define the contract for MNQ Futures
    contract = Contract()
    contract.symbol = "MNQ"  # Underlying symbol for Micro E-mini Nasdaq-100 Futures
    contract.secType = "FUT"  # Security type is FUT for futures
    contract.exchange = "CME"  # CME exchange for MNQ futures
    contract.currency = "USD"
    contract.lastTradeDateOrContractMonth = "202312"  # Use YYYYMM format to define contract month
    contract.includeExpired = True  # Include expired contracts if needed

    # Request contract details
    app.reqContractDetails(219, contract)

    # Wait for response and disconnect
    time.sleep(5)  # Adjust the sleep time if necessary to receive all results
    app.disconnect()


if __name__ == "__main__":
    main()
