### Error getting 5s bars for MNQ from its earliest data point


# SETUP

I'm using IBKR TWS API, so the ports are set to 7497 for the client and 7496 for the gateway. You can change these in the code if you're using a different port.

# GOAL

The goal is to get the earliest available data point for MNQ and then get 5s bars from that point to the current time, and store it in a compressed file type called parquet.

Paraquet is a columnar storage file format that is optimized for reading and writing data in a columnar manner. It is a good choice for storing time series data.

The current functionality requests 5s bars in increments of 1 hour, to reduce the load, and to detect the bug easier.


## Run earliest_available_datapoint.py

```python earliest_available_datapoint.py```

This will get you the earliest data point available for MNQ.

Example output:

```bash
ERROR -1 2104 Market data farm connection is OK:hfarm
ERROR -1 2104 Market data farm connection is OK:usfarm.nj
ERROR -1 2104 Market data farm connection is OK:jfarm    
ERROR -1 2104 Market data farm connection is OK:usfuture 
ERROR -1 2104 Market data farm connection is OK:cashfarm 
ERROR -1 2104 Market data farm connection is OK:eufarmnj 
ERROR -1 2104 Market data farm connection is OK:usfarm   
ERROR -1 2106 HMDS data farm connection is OK:euhmds     
ERROR -1 2106 HMDS data farm connection is OK:cashhmds   
ERROR -1 2106 HMDS data farm connection is OK:fundfarm   
ERROR -1 2106 HMDS data farm connection is OK:ushmds     
ERROR -1 2158 Sec-def data farm connection is OK:secdefil
HeadTimestamp. ReqId: 1, HeadTimeStamp: 20230921  22:00:00
Earliest available data point: 20230921  22:00:00
Earliest available data point (datetime): 2023-09-21 22:00:00
Disconnected from IB API
```

This shows that the earliest available data point for MNQ is 2023-09-21 22:00:00.

## Running looping_data_req.py

```python looping_data_req.py```

This will get you 5s bars for MNQ from the earliest available data point to the current time.
It requests an hour of data at a time, but following IBKR requirements of having the hour be converted into seconds, so 3600 seconds.
It will try 3 times to request that hour of data, and if IBKR doesn't provide it, it will close the connection.

Currently the start and endtime is set to this, because there is a bug that won't provide time after the end time.


``` python
    # Define the date range for historical data
    start_date = datetime.strptime('2023-09-23', '%Y-%m-%d')
    end_date = datetime.strptime('2023-09-25', '%Y-%m-%d')
```

# Example crash

As you will find out it will run, but after a certain time period it will stop providing data to the client, with the following error message:

ERROR 101 162 Historical Market Data Service error message:HMDS query returned no data: MNQZ4@CME Trades

```bash
Time: 1695416325 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416330 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416335 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416340 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416345 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416350 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416355 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416360 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416365 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416370 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416375 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416380 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416385 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416390 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Time: 1695416395 Open: 15650.0 High: 15650.0 Low: 15650.0 Close: 15650.0 Volume: 0
Historical data received from 20230924  21:00:00 to 20230924  22:00:00
Data appended to Parquet file: all_data.parquet
ERROR 101 162 Historical Market Data Service error message:HMDS query returned no data: MNQZ4@CME Trades
```

# Run read_parquet.py

```python read_parquet.py```

This will read the parquet file and print the data collected from the IBKR API.

# Example output

```bash
        
        Data loaded from all_data.parquet
                    timestamp     open     high      low    close  volume  
        0 2023-09-22 20:00:00  15650.0  15650.0  15650.0  15650.0       0  
        1 2023-09-22 20:00:05  15650.0  15650.0  15650.0  15650.0       0  
        2 2023-09-22 20:00:10  15650.0  15650.0  15650.0  15650.0       0  
        3 2023-09-22 20:00:15  15650.0  15650.0  15650.0  15650.0       0  
        4 2023-09-22 20:00:20  15650.0  15650.0  15650.0  15650.0       0  
                    timestamp     open     high      low    close  volume
        715 2023-09-22 20:59:35  15650.0  15650.0  15650.0  15650.0       0
        716 2023-09-22 20:59:40  15650.0  15650.0  15650.0  15650.0       0
        717 2023-09-22 20:59:45  15650.0  15650.0  15650.0  15650.0       0
        718 2023-09-22 20:59:50  15650.0  15650.0  15650.0  15650.0       0
        719 2023-09-22 20:59:55  15650.0  15650.0  15650.0  15650.0       0

        DataFrame Statistics:
                                timestamp     open     high      low    close  volume
        count                            720    720.0    720.0    720.0    720.0   720.0
        mean      2023-09-22 20:29:57.500000  15650.0  15650.0  15650.0  15650.0     0.0
        min              2023-09-22 20:00:00  15650.0  15650.0  15650.0  15650.0     0.0
        25%    2023-09-22 20:14:58.750000128  15650.0  15650.0  15650.0  15650.0     0.0
        50%       2023-09-22 20:29:57.500000  15650.0  15650.0  15650.0  15650.0     0.0
        75%    2023-09-22 20:44:56.249999872  15650.0  15650.0  15650.0  15650.0     0.0
        max              2023-09-22 20:59:55  15650.0  15650.0  15650.0  15650.0     0.0
        std                              NaN      0.0      0.0      0.0      0.0     0.0

        Missing Values:
        timestamp    0
        open         0
        high         0
        low          0
        close        0
        volume       0
        dtype: int64
```

As you can see the last time stamp is 2023-09-22 20:59:55, which is the last data point that was collected before the error message was thrown.


# Conclusion

The bug is that the IBKR API will stop providing data after a certain time period, and will throw an error message.
I'm not sure if this is my fault, but it seems like it's a bug in the API because the earliest available data point is 2023-09-21 22:00:00, and the data is requested from 2023-09-22 20:00:00 to 2023-09-25 22:00:00, which is within the available data range.