import nextcord
from nextcord import Interaction
from nextcord.ext import commands, application_checks
import logging
import os
from translate import Translator

dataBase = {"user": ["from_lang","to_lang"]}

class ShowOriginal(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.value = None

    @nextcord.ui.button(label="Show original", style=nextcord.ButtonStyle.blurple)
    async def showOriginal(self, 
                           button: nextcord.ui.button, 
                           interaction: Interaction):
        self.value = True
        self.stop()

class Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        global dataBase
        originalMessage = message.content
        if message.author.id in list(dataBase.keys()):
            await message.delete()
            translator = Translator(from_lang=dataBase[message.author.id][0], 
                                    to_lang=dataBase[message.author.id][1])
            translatedMessage = translator.translate(message.content)
            print(f"{message.content} has been translated to '{translatedMessage}'")
            em = nextcord.Embed(description=translatedMessage)
            em.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
            em.set_footer(text="This message has been translated.") 
            view = ShowOriginal()
            newMsg = await message.channel.send(embed=em, view=view)
            await view.wait()

            if view.value is None:
                return
            elif view.value:
                em.set_footer(text=f"Original message: {message.content}")
                await newMsg.edit(embed=em)


    @nextcord.slash_command(
            name="toggle",
            description="Toggle translation for a user with selected languages."
            )
    async def toggle(self, interaction: Interaction, 
                     target_user: nextcord.Member, 
                     from_lang: str, to_lang: str):
        await interaction.response.defer()
        global dataBase
        if target_user.id in list(dataBase.keys()):
            del dataBase[target_user.id]
            em = nextcord.Embed(
                color=0x2ecc71,
                title=":white_check_mark: **Success!**",
                description=f"Successfully removed {target_user.mention} from the tracker.",
                )
            em.set_footer(icon_url = interaction.user.avatar.url,
                          text = f"Command ran by {interaction.user.global_name}"
            )
        else:
            dataBase[target_user.id] = [from_lang, to_lang]
            em = nextcord.Embed(
                color=0x2ecc71,
                title=":white_check_mark: **Success!**",
                description=f"{target_user.name} has been added to the tracker! (Languages: `{from_lang}` **->** `{to_lang}`)"
                )
            em.set_footer(icon_url = interaction.user.avatar.url,
                        text = f"Command ran by {interaction.user.global_name}"
                        )
        await interaction.followup.send(embed=em)

def setup(bot):
    bot.add_cog(Messages(bot))