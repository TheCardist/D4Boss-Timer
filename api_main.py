import os
import datetime
import time
import requests
from twilio.rest import Client
import pytz


def request_api_data():
    """ Request boss name and time data """
    
    url = "https://d4armory.io/api/events/recent"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        print("Request failed with status code:", response.status_code)

    boss_name = data["boss"]["expectedName"]
    boss_time = data["boss"]["expected"]

    return boss_name, boss_time


def check_time(boss_time: str) -> bool | str:
    """ Check if it's an appropriate time of day to send sms and if the boss time is <= 30 minutes. """
    
    current_timestamp = int(time.time())

    time_difference = boss_time - current_timestamp

    threshold = 1800  # 30 minutes in seconds

    # Assuming environment variables are set as "HH:MM"
    min_time_str = os.environ.get('MIN_TIME', '07:30')  # default to '07:30' if not set
    max_time_str = os.environ.get('MAX_TIME', '21:30')  # default to '21:30' if not set

    # Split the strings and convert to integers
    min_hour, min_minute = map(int, min_time_str.split(':'))
    max_hour, max_minute = map(int, max_time_str.split(':'))

    # Create datetime.time objects
    min_time = datetime.time(min_hour, min_minute)
    max_time = datetime.time(max_hour, max_minute)

    current_datetime = datetime.datetime.now()
    current_time = current_datetime.time()
    time_diff_formatted = str(datetime.timedelta(seconds=time_difference))

    if current_time > min_time and current_time < max_time:
        if time_difference <= threshold:
            return True, time_diff_formatted
    return False, time_diff_formatted


def send_msg(boss_name: str, boss_time: str, spawn_time: str):
    """ Send SMS message to phone numbers below if criteria are met. """

    # Set environment variables for your credentials
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
    recipient_phone_number= os.environ.get('RECIPIENT_PHONE_NUMBER')
    auth_token = os.environ.get('TWILIO_TOKEN')
    client = Client(account_sid, auth_token)

    # Sending SMS message
    message = client.messages.create(
        body=f"{boss_name} is spawning in {spawn_time}, at {boss_time}",
        from_=f"{twilio_phone_number}",
        to=f"{recipient_phone_number}",
    )

    print(message)


def convert_to_12_hour_format(boss_time: str) -> str:
    datetime_obj = datetime.datetime.utcfromtimestamp(boss_time)
    local_timezone_str = os.environ.get('TZ', 'America/New_York')  # default to 'America/New_York' if not set
    local_timezone = pytz.timezone(local_timezone_str)

    local_datetime = datetime_obj.replace(tzinfo=pytz.utc).astimezone(local_timezone)

    new_boss_time = local_datetime.strftime("%H:%M")
    formatted_boss_time = datetime.datetime.strptime(new_boss_time, "%H:%M").strftime(
        "%I:%M %p"
    )

    return formatted_boss_time


if __name__ == "__main__":
    boss_name, boss_time = request_api_data()
    formatted_boss_time = convert_to_12_hour_format(boss_time)
    within_time_threshold, spawn_time = check_time(boss_time)
    if within_time_threshold:
        print("next spawn is at " + formatted_boss_time)
        print("sending SMS")
        send_msg(boss_name, formatted_boss_time, spawn_time)
    else:
        print("next spawn is at " + formatted_boss_time)

