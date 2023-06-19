# D4Boss-Timer
Simple python program that uses Selenium to go to https://d4armory.io/events/ and pull down the countdown for the next boss, as well as the bosses, name to add into an SMS message if the timer is below 30 minutes and the current time is between 8:30 AM and 9:30 PM.

The other version uses the https://d4armory.io/api/events/recent API endpoint to get the data.

# to build & run the docker containers:

rename ```example.env``` to ```.env``` and fill in the values, then
```docker compose build && docker compose up -d && docker container logs -f D4Boss-alerts```