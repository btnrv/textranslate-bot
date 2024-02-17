import nextcord
from nextcord import Interaction, SlashOption
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
                                    to_lang=dataBase[message.author.id][1], provider="deepl")
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
        if target_user.bot:
            await interaction.followup.send(content="Do not track bot users!")
            return
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

    @nextcord.slash_command(
        name="history",
        description="Translate the last specific amount of messages in a channel."
    )
    async def history(self, interaction: Interaction, 
                     from_lang: str, to_lang: str,
                     amount: int = SlashOption(min_value=5, max_value=50)
                     ):
        resultMessage = ""
        await interaction.response.defer(ephemeral=True)
        translator = Translator(from_lang=from_lang, to_lang=to_lang)
        messagesList = await interaction.channel.history(limit=amount+1).flatten()
        for message in messagesList:
            if message.author.bot:
                messagesList.remove(message)
        messagesList.reverse()
        for message in messagesList:
            resultMessage += f"**{message.author}:**\n {translator.translate(message.content)}\n"
        em = nextcord.Embed(
                color=0x2ecc71,
                title=":white_check_mark: **Success!**",
                description=resultMessage[:-2]
                )
        em.set_footer(icon_url = interaction.user.avatar.url,
                    text = "This chat history is translated."
                    )
        await interaction.followup.send(embed=em)

def setup(bot):
    bot.add_cog(Messages(bot))