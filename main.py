import discord
import json
import os
import threading
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

def set_date():
    global date
    date = datetime.now()

def get_currency_data() -> object:
    set_date()
    parameters = {"api_key": os.getenv("API_KEY"), "format": "json", "amount": "1"}
    url = "https://api.getgeoapi.com/v2/currency/convert"
    response = requests.get(url, parameters)
    if response.status_code != 200:
        return
    json_response = json.loads(response.text)
    return json_response

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

def build_message(json_data, currency) -> str:
    message = "```diff\n"
    if float(json_data['amount']) > float(json_data['rates'][currency]['rate']):
        message += "-        [EUR: "
    else:
        message += "+        [EUR: "
    message += json_data['amount'] + "]\n"
    if float(json_data['amount']) > float(json_data['rates'][currency]['rate']):
        message += f"+        [{currency}: "
    else:
        message += f"-        [{currency}: "
    message += json_data['rates'][currency]['rate'] + "]\n"
    refresh_time = "Last Refresh: " + date.strftime("%H:%M:%S")
    message += refresh_time
    message += "```"
    return message

data = {}
date = ""

def main():
    load_dotenv()
    global data
    client = discord.Client()
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

        if message.content.startswith('$EUR-USD'):
            currency_data = data
            if currency_data['status'] == "success":
                await message.channel.send(build_message(currency_data, 'USD'))
            else:
                await message.channel.send("No currency data!")

        if message.content.startswith('$EUR-GBP'):
            currency_data = data
            if currency_data['status'] == "success":
                await message.channel.send(build_message(currency_data, 'GBP'))
            else:
                await message.channel.send("No currency data!")

        if message.content.startswith('$EUR-PLN'):
            currency_data = data
            if currency_data['status'] == "success":
                await message.channel.send(build_message(currency_data, 'PLN'))
            else:
                await message.channel.send("No currency data!")

    client.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
