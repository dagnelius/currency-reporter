import os
import discord
import requests
import json
import time
import multiprocessing
from dotenv import load_dotenv

def get_currency_data() -> object:
    parameters = {"api_key": os.getenv("API_KEY"), "format": "json", "to": "USD", "amount": "1"}
    url = "https://api.getgeoapi.com/v2/currency/convert"
    response = requests.get(url, parameters)
    data = json.loads(response.text)
    return data

def get_data():
    start_time = time.time()
    while True:
        global data
        data = get_currency_data()
        time.sleep(3600.0 - ((time.time() - start_time) % 3600.0))

def build_currency_message(data) -> str:
    message = "```diff\n"
    if float(data['amount']) > float(data['rates']['USD']['rate']):
        message += "- [EUR: "
    else:
        message += "+ [EUR: "
    message += data['amount']
    message += "]\n"
    if float(data['amount']) > float(data['rates']['USD']['rate']):
        message += "+ [USD: "
    else:
        message += "- [USD: "
    message += data['rates']['USD']['rate']
    message += "]```"
    return message

data = {}
def main():
    load_dotenv()
    global data
    data = get_currency_data()
    client = discord.Client()
    multiprocessing.Process(target=get_data)

    @client.event
    async def on_ready():
        print("Currency Reporter is Ready!\n")

    @client.event
    async def on_message(message):
        global data
        if message.author == client.user:
            return

        if message.content.startswith('$$$'):
            currency_data = data
            if currency_data['status'] == "success":
                await message.channel.send(build_currency_message(currency_data))
            else:
                await message.channel.send("No currency data!")

    client.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
