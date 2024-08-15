import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from deep_translator import GoogleTranslator  # Importing from deep_translator

# TODO: need to implement a real database for this in the future
dataBase = {}  # Format: {user_id: ["from_lang", "to_lang"]}

class ShowOriginal(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.value = None

    @nextcord.ui.button(label="Show original", style=nextcord.ButtonStyle.blurple)
    async def show_original(self, button: nextcord.ui.button, interaction: Interaction):
        self.value = True
        self.stop()

class Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages to prevent infinite loops
        if message.author.bot:
            return

        original_message = message.content
        user_id = message.author.id

        if user_id in dataBase:
            await message.delete()
            src_lang, dest_lang = dataBase[user_id]

            try:
                translated_message = GoogleTranslator(
                    source=src_lang, 
                    target=dest_lang
                ).translate(original_message)
            except Exception:
                translated_message = "Translation error occurred"

            embed = nextcord.Embed(description=translated_message)
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
            embed.set_footer(text="This message has been translated.")

            view = ShowOriginal()
            new_message = await message.channel.send(embed=embed, view=view)
            await view.wait()

            if view.value:
                embed.set_footer(text=f"Original message: {original_message}")
                await new_message.edit(embed=embed)

    @nextcord.slash_command(
        name="toggle",
        description="Toggle translation for a user with selected languages."
    )
    async def toggle(self, interaction: Interaction,
                     target_user: nextcord.Member,
                     from_lang: str, to_lang: str):
        await interaction.response.defer()
        user_id = target_user.id

        if target_user.bot:
            await interaction.followup.send(content="Do not track bot users!")
            return

        if user_id in dataBase:
            del dataBase[user_id]
            description = f"Successfully removed {target_user.mention} from the tracker."
        else:
            dataBase[user_id] = [from_lang, to_lang]
            description = f"{target_user.name} has been added to the tracker! (Languages: `{from_lang}` **->** `{to_lang}`)"

        embed = nextcord.Embed(
            color=0x2ecc71,
            title=":white_check_mark: **Success!**",
            description=description
        )
        embed.set_footer(icon_url=interaction.user.avatar.url,
                         text=f"Command ran by {interaction.user.display_name}")

        await interaction.followup.send(embed=embed)

    @nextcord.slash_command(
        name="history",
        description="Translate the last specific amount of messages in a channel."
    )
    async def history(self, interaction: Interaction,
                      from_lang: str, to_lang: str,
                      amount: int = SlashOption(min_value=5, max_value=50)):
        await interaction.response.defer(ephemeral=True)
        messages = await interaction.channel.history(limit=amount).flatten()

        messages = [msg for msg in messages if not msg.author.bot]
        messages.reverse()

        translations = []
        for message in messages:
            try:
                translated_text = GoogleTranslator(
                    source=from_lang, 
                    target=to_lang
                ).translate(message.content)
                translations.append(f"**{message.author}:**\n{translated_text}\n")
            except Exception:
                translations.append(f"**{message.author}:**\nTranslation error occurred\n")

        result_message = "".join(translations)
        embed = nextcord.Embed(
            color=0x2ecc71,
            title=":white_check_mark: **Success!**",
            description=result_message
        )
        embed.set_footer(icon_url=interaction.user.avatar.url,
                         text="This chat history is translated.")
        await interaction.followup.send(embed=embed)

def setup(bot):
    bot.add_cog(Messages(bot))
