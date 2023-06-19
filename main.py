import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from twilio.rest import Client
import datetime


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
        body=f"{boss_type} is spawning in {boss_countdown}, at {next_boss_time}",
        from_=f"{twilio_phone_number}",
        to=f"{recipient_phone_number}",
    )

    print(message)


def get_boss_info() -> str:
    """ Extract the boss name and current countdown timer information from the website. """

    # Using selenium without opening the browser on the computer
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    driver.get("https://d4armory.io/events/")

    boss_timer_element = driver.find_element(By.XPATH, '//*[@id="tableBossNext"]')
    boss_countdown = boss_timer_element.text

    boss_type_element = driver.find_element(By.XPATH, '//*[@id="bossName"]')
    boss_type = boss_type_element.text

    driver.quit()

    return boss_countdown, boss_type


def get_clean_countdown(boss_countdown: str) -> str:
    """ Remove the h, m, s values from the string to determine later if the timer is lower than 1800 seconds """

    chars = ["h", "m", "s"]
    for c in chars:
        boss_countdown = boss_countdown.replace(c, "")
    return boss_countdown


def convert_to_seconds(boss_countdown: str) -> int:
    """ Convert the extracted countdown information into seconds to validate if it is <= 1800 seconds (30 minutes) before sending the SMS. """

    countdown = boss_countdown.split(" ")

    seconds = 0

    if (
        len(countdown) == 3
    ):  # if there is an hour, minute, and second element in the countdown.
        seconds += int(countdown[0]) * 3600  # hours to seconds
        seconds += int(countdown[1]) * 60  # minutes to seconds
        seconds += int(countdown[2])  # seconds
    elif len(countdown) == 2:  # only minute and seconds
        seconds += int(countdown[0]) * 60  # minutes to seconds
        seconds += int(countdown[1])  # seconds
    else:  # only seconds
        seconds += int(countdown[0])  # seconds

    return seconds


def set_12hr_format(boss_in_seconds: int) -> str:
    """ Convert the seconds into a 12 hour format to display in the SMS message, could also scrap off the d4 website instead. """

    # Get the current datetime object
    current_datetime = datetime.datetime.now()

    # Number of seconds to add
    seconds_to_add = boss_in_seconds

    # Create a timedelta object with the desired number of seconds
    delta = datetime.timedelta(seconds=seconds_to_add)

    # Add the timedelta to the current datetime to get the new datetime
    new_datetime = current_datetime + delta

    # Extract the time component from the new datetime
    new_time = new_datetime.time()

    next_boss_time = (
        new_time.strftime("%I:%M %p")
        .lstrip("0")
        .lower()
        .replace("am", "a.m.")
        .replace("pm", "p.m.")
    )

    return next_boss_time


def check_time(seconds: int) -> bool:
    """ Putting restrictions in place so sms messages are not sent too early or too late in the day and are not sent at all if the boss has more than 30 minutes until spawn time. """

    current_time = datetime.datetime.now().time()

    # Assuming environment variables are set as "HH:MM"
    min_time_str = os.environ.get('MIN_TIME', '07:30')  # default to '07:30' if not set
    max_time_str = os.environ.get('MAX_TIME', '21:30')  # default to '21:30' if not set

    # Split the strings and convert to integers
    min_hour, min_minute = map(int, min_time_str.split(':'))
    max_hour, max_minute = map(int, max_time_str.split(':'))

    # Create datetime.time objects
    min_time = datetime.time(min_hour, min_minute)
    max_time = datetime.time(max_hour, max_minute)

    if current_time > min_time and current_time < max_time:
        if seconds <= 1800:  # <= 30 minutes until spawn time
            return True


if __name__ == "__main__":
    boss_countdown, boss_type = get_boss_info()
    clean_countdown = get_clean_countdown(boss_countdown)

    seconds = convert_to_seconds(clean_countdown)
    next_boss_time = set_12hr_format(seconds)
    
    if check_time(seconds):
        print("next spawn is at " + next_boss_time + ".")
        print("sending SMS")
        send_msg(boss_countdown, boss_type, next_boss_time)
    else:
        print("next spawn is at " + next_boss_time + ".")