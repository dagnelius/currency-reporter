import discord
import json
import os
import threading
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

# Set Environment Variables
load_dotenv()

# Set Default Values
data = {}
date = ""
prefix = "-"

# Set Global Variable Date
def set_date():
    global date
    date = datetime.now()

# Get Data From GetGeoApi Api
def get_currency_data() -> object:
    set_date()
    parameters = {"api_key": os.getenv("API_KEY"), "format": "json", "amount": "1"}
    url = "https://api.getgeoapi.com/v2/currency/convert"
    response = requests.get(url, parameters)
    if response.status_code != 200:
        return
    json_response = json.loads(response.text)
    return json_response

# Get Data Every 30 Minutes
def get_data():
    start_time = time.time()
    while True:
        global data
        safe_data = get_currency_data()
        if safe_data:
            data = safe_data
            time.sleep(1800.0 - ((time.time() - start_time) % 1800.0))
        else:
            data = data
            time.sleep(1800.0 - ((time.time() - start_time) % 1800.0))

# Build Response Message
def build_message(json_data, currency) -> str:
    message = "```diff\n"
    message += f"-------------[EUR: {currency}---]\n"
    if float(json_data['amount']) > float(json_data['rates'][currency]['rate']):
        message += "-            [EUR: "
    else:
        message += "+            [EUR: "
    message += json_data['amount'] + "]\n"
    if float(json_data['amount']) > float(json_data['rates'][currency]['rate']):
        message += f"+            [{currency}: "
    else:
        message += f"-            [{currency}: "
    message += json_data['rates'][currency]['rate'] + "]\n"
    message += "--------------------------\n"
    refresh_time = "--Last Refresh: " + date.strftime("%H:%M:%S") + '--'
    message += refresh_time
    message += "\n--------------------------"
    message += "```"
    return message

def main():
    global data
    client = discord.Client()

    # Get data every 30 minutes
    t = threading.Thread(target=get_data)
    t.start()

    @client.event
    async def on_ready():
        print("Currency Reporter is Ready!\n")

    @client.event
    async def on_message(message):
        global data
        if message.author == client.user:
            return

        if message.content.startswith(f'{prefix}help'):
            return_content = f'''
```diff
---------------------[HELP]
-Syntax:         [{prefix}BASE-TO]
-Example:        [{prefix}EUR-USD]
---------------------------
+Available Base Currencies:
+                     [EUR]
+  Available To Currencies:
+           [EUR, GBP, PLN]
---------------------------
```
'''
            await message.channel.send(return_content)

        if message.content.startswith(f'{prefix}EUR-'):
            currency_data = data
            if currency_data['status'] == "success":
                if not message.content[5:8] in currency_data['rates']:
                    await message.channel.send(f"Currency {message.content[5:8]} not found!")
                else:
                    await message.channel.send(build_message(currency_data, message.content[5:8]))
            else:
                await message.channel.send("No currency data!")

    client.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()


# TODO: OOP, RESERVED SPACE
