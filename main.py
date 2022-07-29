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

load_dotenv()
client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!usd'):
        currency_data = get_currency_data()

        if currency_data['status'] == "success":
            currency_message = currency_data['amount']
            currency_message += currency_data['base_currency_name']
            currency_message += " -> "
            currency_message += currency_data['rates']['USD']['rate']
            currency_message += currency_data['rates']['USD']['currency_name']
            await message.channel.send(currency_message)
        else:
            await message.channel.send("No currency data!")

client.run(os.getenv("TOKEN"))
