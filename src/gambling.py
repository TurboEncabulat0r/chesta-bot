import discord
from discord.ext import commands
import asyncio
import builtins

guild = builtins.guild
client = builtins.client
# modal that asks the user for a bet ammount and a color
class rouletteModal(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Red", style=discord.ButtonStyle.red)
    async def red(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "red"
        self.stop()

    @discord.ui.button(label="Black", style=discord.ButtonStyle.blurple)
    async def black(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "black"
        self.stop()

    @discord.ui.button(label="Green", style=discord.ButtonStyle.green)
    async def green(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "green"
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == client.user:
            await interaction.response.send_message("You can't use this command.", ephemeral=True)
            return False
        return True

@client.slash_command(guild_ids=[guild])
async def roulette(ctx, bet: int):
    pass

@client.slash_command(guild_ids=[guild])
async def slots(ctx, bet: int):
    await ctx.respond("This command is not yet implemented.", ephemeral=True)