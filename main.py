import os
import asyncio
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


def znajdz_dziennik_kar(guild):
    for kanal in guild.text_channels:
        nazwa = kanal.name.lower()
        oczyszczona = "".join(c for c in nazwa if c.isalnum())

        if "dziennikkar" in oczyszczona:
            return kanal

    return None


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
        await interaction.response.send_message(
            "Czas musi wynosić minimum 1 minutę",
            ephemeral=True
        )
        return

    kanal_logow = znajdz_dziennik_kar(interaction.guild)

    if kanal_logow is None:
        await interaction.response.send_message(
            "❌ Nie znaleziono kanału dziennik-kar",
            ephemeral=True
        )
        return

    try:
        await user.timeout(
            timedelta(minutes=minutes),
            reason=reason
        )

        embed = discord.Embed(
            description=(
                f"**{user.display_name} został wyciszony.**\n\n"
                f"**Na ile minut:** {minutes}\n"
                f"**Za co:** {reason}\n\n"
                f"**Moderator:** {interaction.user.display_name}\n"
                f"**Jaki bot:** {bot.user.display_name}"
            ),
            color=discord.Color.green()
        )

        await kanal_logow.send(embed=embed)

        await interaction.response.send_message(
            f"🔇 {user.mention} został wyciszony na **{minutes} min**\n"
            f"Powód: {reason}"
        )

        await asyncio.sleep(minutes * 60)

        embed_koniec = discord.Embed(
            description=(
                f"**Mute użytkownika {user.display_name} skończył się.**\n\n"
                f"**Na ile minut:** {minutes}\n"
                f"**Za co:** {reason}\n\n"
                f"**Moderator:** {interaction.user.display_name}\n"
                f"**Jaki bot:** {bot.user.display_name}"
            ),
            color=discord.Color.red()
        )

        await kanal_logow.send(embed=embed_koniec)

    except discord.Forbidden:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Bot nie ma odpowiednich uprawnień",
                ephemeral=True
            )

    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"❌ Wystąpił błąd: `{e}`",
                ephemeral=True
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
