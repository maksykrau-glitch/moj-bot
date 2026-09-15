@bot.tree.command(name="wycisz", description="Wycisza użytkownika")
@app_commands.checks.has_permissions(moderate_members=True)
async def wycisz(
    interaction: discord.Interaction,
    uzytkownik: discord.Member,
    minuty: int,
    powod: str
):
    try:
        if minuty <= 0:
            await interaction.response.send_message(
                "❌ Liczba minut musi być większa niż 0",
                ephemeral=True
            )
            return

        czas = datetime.timedelta(minutes=minuty)

        # Wyciszenie użytkownika
        await uzytkownik.timeout(czas, reason=powod)

        # Szukanie kanału dziennik kar
        kanal_logow = None

        for kanal in interaction.guild.text_channels:
            nazwa = kanal.name.lower()
            oczyszczona = "".join(c for c in nazwa if c.isalnum())

            if "dziennikkar" in oczyszczona:
                kanal_logow = kanal
                break

        if kanal_logow is None:
            await interaction.response.send_message(
                "❌ Nie znaleziono kanału dziennik kar",
                ephemeral=True
            )
            return

        # 🟢 TABELKA ROZPOCZĘCIA MUTE
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

        # Odpowiedź tylko dla moderatora
        await interaction.response.send_message(
            f"✅ Wyciszono **{uzytkownik.display_name}** na **{minuty} minut**",
            ephemeral=True
        )

        # Czekanie aż mute się skończy
        await asyncio.sleep(minuty * 60)

        # 🔴 TABELKA ZAKOŃCZENIA MUTE
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
                "❌ Nie mogę wyciszyć tego użytkownika",
                ephemeral=True
            )

    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"❌ Wystąpił błąd: `{e}`",
                ephemeral=True
            )
