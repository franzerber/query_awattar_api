# Python Data Analysis Tool using API

## Description query awattar api and make statistics

import requests
import asyncio 
import json
from time import ctime, time, mktime
from datetime import date, timedelta, datetime
from pprint import pprint
DEBUG = True

def ask_user():
    """ query User """
    todays_date = date.today()
    print(f"today: {todays_date}")
    print(type(todays_date))
    month = int(input('Enter a month: '))
    day = int(input('Enter a day: '))
    return(month, day)

def get_unix_timestamp(year: int, month: int, day: int) -> int:
    """Generate Unix timestamp from year, month, and day."""
    dt = datetime(year, month, day)
    unix_timestamp = int(mktime(dt.timetuple()))
    return unix_timestamp

def get_timestring(month: int, day: int) -> list[str]:
    """ generate list of start and endtimes """
    first_year = 2022
    second_year = 2023
    third_year = 2024
    now = datetime.now()
    timestamps= []
    timestamps.append([get_unix_timestamp(first_year, month, day)*1000, get_unix_timestamp(first_year, month, day+1)*1000])
    timestamps.append([get_unix_timestamp(second_year, month, day)*1000, get_unix_timestamp(second_year, month, day+1)*1000])
    one_day_ago = now - timedelta(days=1)
    print(f"one day ago: {one_day_ago.timestamp()}, third year: {get_unix_timestamp(third_year, month, day)}")
    if int(one_day_ago.timestamp()) > get_unix_timestamp(third_year, month, day):
        print("one day ago is bigger than third year")
        timestamps.append([get_unix_timestamp(third_year, month, day)*1000, get_unix_timestamp(third_year, month, day+1)*1000])
    pprint(timestamps)
    return timestamps

def get_data_from_api(start_timestamp: str, end_timestamp: str):
    """ Query API and return results """
    parameter = {
        'start': start_timestamp,
        'end': end_timestamp
    }
    apiurl='https://api.awattar.at/v1/marketdata'
    response = requests.get(apiurl, params=parameter, timeout=15)
    print(response)
    data_dict = json.loads(response.text)
    datalist = data_dict['data']
    return datalist

def is_timestamp_in_ms(unix_timestamp: int) -> bool:
    """Check if the Unix timestamp is in milliseconds format."""
    return len(str(unix_timestamp)) == 13

def convert_unix_to_readable(unix_timestamp: int) -> str:
    """Convert Unix timestamp to readable date and time format."""
    if is_timestamp_in_ms(unix_timestamp):
        # Convert milliseconds to seconds
        unix_timestamp = unix_timestamp / 1000 # type: ignore # no need to check if it is in ms
    return datetime.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')

def print_data(data_list: list[dict]):
    """ generate data
    "hourly,info_source=awattar_api cents_per_kwh=15.11 1692831600000000011\n
     hourly,info_source=awattar_api cents_per_kwh=15.22 1692831600000000022\n"
    """
    request_data=""
    for line in data_list:
        unix_timestamp = line['start_timestamp']
        startts=convert_unix_to_readable(line['start_timestamp'])
        endts=convert_unix_to_readable(line['end_timestamp'])
        price:float = line['marketprice']
        unit = line['unit']
        euro_pro_kwh=float(price)/1000
        cents=round((euro_pro_kwh *100), 2)
        if DEBUG is not False:
            print(f"full line: {line}")
            print(f"Zeitraum von: {startts} bis: {endts} -  Preis: {price} / {unit} = {cents} Cent/kwh")
        request_data=f"{request_data}\nhourly,info_source=awattar_api cents_per_kwh={cents} {unix_timestamp*1000000}"
    return request_data

def main():
    """ Main function """
    month, day = ask_user()
    timestamp_list = get_timestring(month, day)
    for timestamps in timestamp_list:
        response_data = get_data_from_api(start_timestamp = timestamps[0], end_timestamp = timestamps[1])
        print(len(response_data))


if __name__ =="__main__":
    main()