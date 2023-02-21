import spotipy
import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import button, View, Button
import os, datetime

from dotenv import load_dotenv

load_dotenv()

token = os.getenv('token')


my_guild=discord.Object(id=1052633446595440741)


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix = '*', intents=discord.Intents.all(), application_id=1052625943748943942)
        self.weekly_pepites = {}
        

    async def setup_hook(self) -> None:
        await self.load_extension('commands')
        
        #self.tree.copy_global_to(guild=my_guild)
        await self.tree.sync(guild=my_guild)
        await self.tree.sync()


    async def on_ready(self):
        #await self.get_pepites.start()
        print('Prêt !')


    def sort_pepites(self):
        l = []
        
        while len(l) < 5:
            maxi = ["str", 0]
            for i in self.weekly_pepites:
                if i[1] > maxi[1]:
                    maxi = i
            l.append(maxi)
            self.weekly_pepites.remove(maxi)

        return l
        






bot = Bot()

@bot.command()
async def caca(ctx):
    channel = bot.get_channel(1060556948052914257)
    await channel.send("caca")

bot.run(token)

