import nextcord
from nextcord import Interaction
from nextcord.ext import commands, application_checks
import os
from dotenv import load_dotenv

bot = commands.Bot(intents=nextcord.Intents.all())

@bot.event
async def on_ready():
    print("Bot hazır")
    print("-----------------")
    await bot.change_presence(activity=nextcord.Game(name='In development.'))

for fn in os.listdir("./cogs"):
    if fn.endswith(".py"):
        bot.load_extension(f"cogs.{fn[:-3]}")
    else:
        pass

@bot.slash_command(
    name="cog"
)
@application_checks.is_owner()
async def cog(interaction: Interaction):
    pass
@cog.subcommand()
@application_checks.is_owner()
async def load(interaction: Interaction, extension: str):
    bot.load_extension(f"cogs.{extension}")
    await interaction.send("cog yüklendi!")
@cog.subcommand()
@application_checks.is_owner()
async def unload(interaction: Interaction, extension: str):
    bot.unload_extension(f"cogs.{extension}")
    await interaction.send("cog durduruldu!")
@cog.subcommand()
@application_checks.is_owner()
async def reload(interaction: Interaction, extension: str):
    bot.reload_extension(f"cogs.{extension}")
    await interaction.send("cog yeniden yüklendi!")

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)