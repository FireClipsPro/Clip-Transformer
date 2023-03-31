import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv


class DiscordBotController:

    load_dotenv(os.path.abspath('../../.env.discord'))
    __TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    __GUILD = os.getenv('DISCORD_GUILD')
    __CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        self.client = discord.Client(intents=intents)

    def retrieve_midjourney_images(self, prompt):
        @self.client.event
        async def on_ready():
            guild = discord.utils.get(self.client.guilds, name=self.__GUILD)
            channel = self.client.get_channel(self.__CHANNEL_ID)
            print(f'{self.client.user} has connected to Discord!\n'
                  f'{guild.name}(id: {guild.id})\n'
                  f'Channel: {channel.name}\n')
            await channel.send(f'/imagine prompt: {prompt}')

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return
            print(message)

        self.client.run(self.__TOKEN)

bot = DiscordBotController()
bot.retrieve_midjourney_images('challenging yet achievable tasks')
