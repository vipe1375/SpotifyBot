import spotipy
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import button, View, Button
import os

from dotenv import load_dotenv

load_dotenv()

token = os.getenv('token')


my_guild=discord.Object(id=1052633446595440741)


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix = '*', intents=discord.Intents.all(), application_id=1052625943748943942)
        

    async def setup_hook(self) -> None:
        await self.load_extension('commands')
        #self.tree.copy_global_to(guild=my_guild)
        await self.tree.sync(guild=my_guild)
        await self.tree.sync()

    async def on_ready(self):
        print('Prêt !')





bot = Bot()

bot.run(token)

