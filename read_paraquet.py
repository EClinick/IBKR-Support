import pandas as pd

def read_parquet_file(filename='all_data.parquet'):
    """
    Reads a Parquet file and returns a DataFrame.

    Parameters:
    - filename: Path to the Parquet file.

    Returns:
    - Pandas DataFrame containing the data.
    """
    try:
        df = pd.read_parquet(filename, engine='pyarrow')
        print(f"Data loaded from {filename}")
        print(df.head())  # Display first few records
        #display last few records
        print(df.tail())
        return df
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
    except Exception as e:
        print(f"Error reading Parquet file: {e}")
        return None

if __name__ == "__main__":
    df = read_parquet_file()

    if df is not None and not df.empty:
        # Proceed with your ML pipeline using the DataFrame `df`
        # Example: Display basic statistics
        print("\nDataFrame Statistics:")
        print(df.describe())

        # Example: Check for missing values
        print("\nMissing Values:")
        print(df.isnull().sum())

        # Example: Save DataFrame to CSV (optional)
        # df.to_csv('all_data.csv', index=False)
    else:
        print("No data available for processing.")
