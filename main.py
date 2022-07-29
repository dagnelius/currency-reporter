import os
import discord
import requests
import json
from dotenv import load_dotenv

def get_currency_data() -> object:
    parameters = {"api_key": os.getenv("API_KEY"), "format": "json", "to": "USD", "amount": "1"}
    url = "https://api.getgeoapi.com/v2/currency/convert"
    response = requests.get(url, parameters)
    data = json.loads(response.text)
    return data

def build_currency_message(data) -> str:
    message = data['amount']
    message += data['base_currency_name']
    message += " -> "
    message += data['rates']['USD']['rate']
    message += data['rates']['USD']['currency_name']
    return message

def main():
    load_dotenv()
    client = discord.Client()

    @client.event
    async def on_ready():
        print("Currency Reporter is Ready!\n")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith('$$$'):
            currency_data = get_currency_data()
            if currency_data['status'] == "success":
                await message.channel.send(build_currency_message(currency_data))
            else:
                await message.channel.send("No currency data!")

    client.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()

