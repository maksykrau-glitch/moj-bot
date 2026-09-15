import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

aktywne_mute = {}
aktywne_bany = {}


@bot.event
async def on_ready():
    guild = discord.Object(id=1486819364328968503)

    bot.tree.clear_commands(guild=guild)
    bot.tree.copy_global_to(guild=guild)

    await bot.tree.sync(guild=guild)

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

    kanal = znajdz_dziennik_kar(interaction.guild)

    if kanal is None:
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

        aktywne_mute[user.id] = {
            "minutes": minutes,
            "reason": reason,
            "moderator": interaction.user.display_name
        }

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

        await kanal.send(embed=embed)

        await interaction.response.send_message(
            "✅ Użytkownik został wyciszony",
            ephemeral=True
        )

        await asyncio.sleep(minutes * 60)

        member = interaction.guild.get_member(user.id)

        if member and member.is_timed_out():
            await member.timeout(None, reason="Mute zakończony")

        dane = aktywne_mute.pop(user.id, None)

        if dane:
            embed_koniec = discord.Embed(
                description=(
                    f"**Mute użytkownika {user.display_name} skończył się.**\n\n"
                    f"**Ile trwał mute:** {dane['minutes']} minut\n"
                    f"**Za co:** {dane['reason']}\n\n"
                    f"**Moderator:** {dane['moderator']}\n"
                    f"**Jaki bot:** {bot.user.display_name}"
                ),
                color=discord.Color.red()
            )

            await kanal.send(embed=embed_koniec)

    except discord.Forbidden:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Bot nie ma odpowiednich uprawnień",
                ephemeral=True
            )


@bot.tree.command(name="unmute", description="Usuwa wyciszenie użytkownika")
@app_commands.describe(
    user="Osoba, której chcesz usunąć mute"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(
    interaction: discord.Interaction,
    user: discord.Member
):
    kanal = znajdz_dziennik_kar(interaction.guild)

    if kanal is None:
        await interaction.response.send_message(
            "❌ Nie znaleziono kanału dziennik-kar",
            ephemeral=True
        )
        return

    try:
        await user.timeout(
            None,
            reason=f"Unmute przez {interaction.user.display_name}"
        )

        dane = aktywne_mute.pop(user.id, None)

        if dane:
            embed = discord.Embed(
                description=(
                    f"**Mute użytkownika {user.display_name} został usunięty.**\n\n"
                    f"**Ile trwał mute:** {dane['minutes']} minut\n"
                    f"**Za co:** {dane['reason']}\n\n"
                    f"**Moderator:** {dane['moderator']}\n"
                    f"**Jaki bot:** {bot.user.display_name}"
                ),
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                description=(
                    f"**Mute użytkownika {user.display_name} został usunięty.**\n\n"
                    f"**Moderator:** {interaction.user.display_name}\n"
                    f"**Jaki bot:** {bot.user.display_name}"
                ),
                color=discord.Color.red()
            )

        await kanal.send(embed=embed)

        await interaction.response.send_message(
            "✅ Mute został usunięty",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Bot nie ma odpowiednich uprawnień",
            ephemeral=True
        )


@bot.tree.command(name="bann", description="Banuje użytkownika")
@app_commands.describe(
    user="Osoba do zbanowania",
    reason="Powód bana"
)
@app_commands.checks.has_permissions(ban_members=True)
async def bann(
    interaction: discord.Interaction,
    user: discord.Member,
    reason: str = "Brak powodu"
):
    kanal = znajdz_dziennik_kar(interaction.guild)

    if kanal is None:
        await interaction.response.send_message(
            "❌ Nie znaleziono kanału dziennik-kar",
            ephemeral=True
        )
        return

    try:
        aktywne_bany[user.id] = {
            "reason": reason,
            "moderator": interaction.user.display_name,
            "nick": user.display_name
        }

        await user.ban(reason=reason)

        embed = discord.Embed(
            description=(
                f"**Użytkownik {user.display_name} dostał bana.**\n\n"
                f"**Za co:** {reason}\n\n"
                f"**Moderator:** {interaction.user.display_name}\n"
                f"**Jaki bot:** {bot.user.display_name}"
            ),
            color=discord.Color.green()
        )

        await kanal.send(embed=embed)

        await interaction.response.send_message(
            "✅ Użytkownik został zbanowany",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Bot nie ma odpowiednich uprawnień",
            ephemeral=True
        )


@bot.tree.command(name="unnban", description="Usuwa bana użytkownika")
@app_commands.describe(
    user_id="ID użytkownika"
)
@app_commands.checks.has_permissions(ban_members=True)
async def unnban(
    interaction: discord.Interaction,
    user_id: str
):
    kanal = znajdz_dziennik_kar(interaction.guild)

    if kanal is None:
        await interaction.response.send_message(
            "❌ Nie znaleziono kanału dziennik-kar",
            ephemeral=True
        )
        return

    try:
        user = await bot.fetch_user(int(user_id))

        await interaction.guild.unban(
            user,
            reason=f"Unban przez {interaction.user.display_name}"
        )

        dane = aktywne_bany.pop(user.id, None)

        if dane:
            nick = dane["nick"]
            reason = dane["reason"]
            moderator = dane["moderator"]
        else:
            nick = user.display_name
            reason = "Brak zapisanych informacji"
            moderator = interaction.user.display_name

        embed = discord.Embed(
            description=(
                f"**Ban użytkownika {nick} został usunięty.**\n\n"
                f"**Za co:** {reason}\n\n"
                f"**Moderator:** {moderator}\n"
                f"**Jaki bot:** {bot.user.display_name}"
            ),
            color=discord.Color.red()
        )

        await kanal.send(embed=embed)

        await interaction.response.send_message(
            "✅ Ban został usunięty",
            ephemeral=True
        )

    except ValueError:
        await interaction.response.send_message(
            "❌ ID użytkownika musi być liczbą",
            ephemeral=True
        )

    except discord.NotFound:
        await interaction.response.send_message(
            "❌ Nie znaleziono tego bana",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Bot nie ma odpowiednich uprawnień",
            ephemeral=True
        )


@bot.tree.command(name="kickk", description="Wyrzuca użytkownika z serwera")
@app_commands.describe(
    user="Osoba do wyrzucenia",
    reason="Powód wyrzucenia"
)
@app_commands.checks.has_permissions(kick_members=True)
async def kickk(
    interaction: discord.Interaction,
    user: discord.Member,
    reason: str = "Brak powodu"
):
    kanal = znajdz_dziennik_kar(interaction.guild)

    if kanal is None:
        await interaction.response.send_message(
            "❌ Nie znaleziono kanału dziennik-kar",
            ephemeral=True
        )
        return

    try:
        nick = user.display_name

        await user.kick(reason=reason)

        embed = discord.Embed(
            description=(
                f"**Użytkownik {nick} został wyrzucony z serwera.**\n\n"
                f"**Za co:** {reason}\n\n"
                f"**Moderator:** {interaction.user.display_name}\n"
                f"**Jaki bot:** {bot.user.display_name}"
            ),
            color=discord.Color.green()
        )

        await kanal.send(embed=embed)

        await interaction.response.send_message(
            "✅ Użytkownik został wyrzucony",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Bot nie ma odpowiednich uprawnień",
            ephemeral=True
        )


@mute.error
@unmute.error
@bann.error
@unnban.error
@kickk.error
async def command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "❌ Nie masz odpowiednich uprawnień do tej komendy",
            ephemeral=True
        )


TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("Brak TOKEN w zmiennych środowiskowych")

bot.run(TOKEN)
