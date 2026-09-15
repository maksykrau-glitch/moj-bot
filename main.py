import os
import asyncio
import datetime
import add_commands
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================
# BOT START
# =========================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Zalogowano jako {bot.user}")


# =========================
# ZNAJDOWANIE DZIENNIKA KAR
# =========================

def znajdz_dziennik_kar(guild):
    for kanal in guild.text_channels:
        nazwa = kanal.name.lower()
        oczyszczona = "".join(c for c in nazwa if c.isalnum())

        if "dziennikkar" in oczyszczona:
            return kanal

    return None


# =========================
# WYCISZENIE
# =========================

@bot.tree.command(
    name="wycisz",
    description="Wycisza użytkownika"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def wycisz(
    interaction: discord.Interaction,
    uzytkownik: discord.Member,
    minuty: int,
    powod: str
):
    if minuty <= 0:
        await interaction.response.send_message(
            "❌ Liczba minut musi być większa niż 0",
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
        czas = datetime.timedelta(minutes=minuty)

        await uzytkownik.timeout(
            czas,
            reason=powod
        )

        # 🟢 MUTE ROZPOCZĘTY

        embed = discord.Embed(
            description=(
                f"**{uzytkownik.display_name} został wyciszony.**\n\n"
                f"**Na ile minut:** {minuty}\n"
                f"**Za co:** {powod}\n\n"
                f"**Moderator:** {interaction.user.display_name}\n"
                f"**Jaki bot:** {bot.user.display_name}"
            ),
            color=discord.Color.green()
        )

        await kanal_logow.send(embed=embed)

        await interaction.response.send_message(
            f"✅ Wyciszono **{uzytkownik.display_name}** na **{minuty} minut**",
            ephemeral=True
        )

        # Czekanie na koniec mute

        await asyncio.sleep(minuty * 60)

        # 🔴 MUTE ZAKOŃCZONY

        embed_koniec = discord.Embed(
            description=(
                f"**Mute użytkownika {uzytkownik.display_name} skończył się.**\n\n"
                f"**Na ile minut:** {minuty}\n"
                f"**Za co:** {powod}\n\n"
                f"**Moderator:** {interaction.user.display_name}\n"
                f"**Jaki bot:** {bot.user.display_name}"
            ),
            color=discord.Color.red()
        )

        await kanal_logow.send(embed=embed_koniec)

    except discord.Forbidden:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Nie mam odpowiednich uprawnień",
                ephemeral=True
            )

    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"❌ Wystąpił błąd: `{e}`",
                ephemeral=True
            )


# =========================
# URUCHOMIENIE
# =========================

bot.run(TOKEN)
