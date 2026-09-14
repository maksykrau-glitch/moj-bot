import os
import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot online: {bot.user}")

@bot.tree.command(name="mute", description="Wycisza użytkownika")
@app_commands.describe(
    user="Osoba do wyciszenia",
    minutes="Czas w minutach",
    reason="Powód wyciszenia"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(
    interaction: discord.Interaction,
    user: discord.Member,
    minutes: int,
    reason: str = "Brak powodu"
):
    if minutes < 1:
        await interaction.response.send_message("Czas musi wynosić minimum 1 minutę", ephemeral=True)
        return

    await user.timeout(timedelta(minutes=minutes), reason=reason)

    await interaction.response.send_message(
        f"🔇 {user.mention} został wyciszony na **{minutes} min**\nPowód: {reason}"
    )

@mute.error
async def mute_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "Nie masz uprawnień do wyciszania użytkowników",
            ephemeral=True
        )

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("Brak TOKEN w zmiennych środowiskowych")

bot.run(TOKEN)
