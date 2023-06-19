import datetime
import time
import requests
import keyring
from twilio.rest import Client
import pytz


def request_api_data():
    url = "https://d4armory.io/api/events/recent"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        print("Request failed with status code:", response.status_code)

    boss_name = data["boss"]["expectedName"]
    boss_time = data["boss"]["expected"]

    return boss_name, boss_time


def check_time(boss_time: str):
    current_timestamp = int(time.time())

    time_difference = boss_time - current_timestamp

    threshold = 1800  # 30 minutes in seconds

    min_time = datetime.time(7, 30)  # 8:30 AM
    max_time = datetime.time(21, 30)  # 9:30 PM

    current_datetime = datetime.datetime.now()
    current_time = current_datetime.time()

    if current_time > min_time and current_time < max_time:
        if time_difference <= threshold:
            time_diff_formatted = datetime.datetime.utcfromtimestamp(
                time_difference
            ).strftime("%M:%S")

            return True, time_diff_formatted


def send_msg(boss_name: str, boss_time: str, spawn_time: str):
    """Send SMS message to phone numbers below if critiera is met."""

    # Set environment variables for your credentials
    account_sid = keyring.get_password("twilio", "sid")
    auth_token = keyring.get_password("twilio", "token")
    client = Client(account_sid, auth_token)

    # Sending SMS message
    message = client.messages.create(
        body=f"{boss_name} is spawning in {spawn_time}, at {boss_time} EST",
        from_="+15044144854",
        to="+15406295089",
    )

    print(message.sid)


def convert_to_12_hour_format(boss_time):
    datetime_obj = datetime.datetime.utcfromtimestamp(boss_time)
    local_timezone = pytz.timezone("America/New_York")

    local_datetime = datetime_obj.replace(tzinfo=pytz.utc).astimezone(local_timezone)

    new_boss_time = local_datetime.strftime("%H:%M")
    formatted_boss_time = datetime.datetime.strptime(new_boss_time, "%H:%M").strftime(
        "%I:%M %p"
    )

    return formatted_boss_time


if __name__ == "__main__":
    boss_name, boss_time = request_api_data()
    spawn_time = check_time(boss_time)
    if within_time_threshold:
        formatted_boss_time = convert_to_12_hour_format(boss_time)
        send_msg(boss_name, formatted_boss_time, spawn_time)
