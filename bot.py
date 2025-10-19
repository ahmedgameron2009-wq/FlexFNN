# bot.py
# FlexFN Discord Bot - genera licencias JWT
# Comando: !gen <dias> <nota>
#  -> 0 = ilimitada, >0 = caducidad en N días

import os
import jwt
import discord
from datetime import datetime, timedelta, timezone

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
SECRET_KEY = os.environ.get("SECRET_KEY", "CAMBIA_ESTA_CLAVE_SUPER_SECRETA")
ALGORITHM = "HS256"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def make_token(days: int, meta: dict = None):
    payload = {"iat": int(datetime.now(timezone.utc).timestamp()), "type": "license"}
    if meta:
        payload.update(meta)
    if days > 0:
        exp = datetime.now(timezone.utc) + timedelta(days=days)
        payload["exp"] = int(exp.timestamp())
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode()
    return token

@client.event
async def on_ready():
    print(f"Bot iniciado como {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("!gen "):
        parts = message.content.split(maxsplit=2)
        try:
            days = int(parts[1])
        except (IndexError, ValueError):
            await message.channel.send("Uso: `!gen <días>` (0 = ilimitada)")
            return

        note = parts[2] if len(parts) >= 3 else ""
        token = make_token(days, {"creator": str(message.author), "note": note})
        try:
            await message.author.send(f"🎟️ Licencia generada (días={days}):\n```\n{token}\n```")
            await message.channel.send(f"{message.author.mention} te he enviado la licencia por DM ✅")
        except discord.Forbidden:
            await message.channel.send(f"🎟️ Licencia:\n```\n{token}\n```")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ ERROR: falta DISCORD_TOKEN en variables de entorno")
    else:
        client.run(DISCORD_TOKEN)
