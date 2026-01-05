import discord
from discord.ext import commands
import json
import os
from flask import Flask
from threading import Thread
import asyncio

# ======================
# CONFIGURACIÓN
# ======================

PREFIX = "+"
TOKEN = os.getenv("TOKEN")  # TOKEN en Secrets

LOG_CHANNEL_ID = 1456092888952737833

STAFF_IDS = [
    1418712877426016319,
    1416613885997355029
]

MAX_POINTS = 50
MAX_TIMEOUT = 31536000  # 1 año en segundos

ROLE_REWARDS = {
    10: 1454953357360759018,
    20: 1454956321672790137,
    30: 1454956952504369202,
    40: 1454958077412376769,
    50: 1454958494649155746
}

POINTS_FILE = "points.json"

# ======================
# FLASK / PREVIEW
# ======================

app = Flask("")

@app.route("/")
def home():
    return "SAFE POINTS SABH • ONLINE ✅"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_flask).start()

# ======================
# BOT SETUP
# ======================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

# ======================
# UTILIDADES
# ======================

def load_points():
    if not os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "w") as f:
            json.dump({}, f)
    with open(POINTS_FILE, "r") as f:
        return json.load(f)

def save_points(data):
    with open(POINTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def send_log(guild, embed):
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

def is_staff(ctx):
    return ctx.author.id in STAFF_IDS or ctx.author.guild_permissions.moderate_members

# ======================
# EVENTOS
# ======================

@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")

# LOG CANALES MOVIDOS
@bot.event
async def on_guild_channel_update(before, after):
    if before.position == after.position and before.category_id == after.category_id:
        return

    await asyncio.sleep(1.5)

    async for entry in after.guild.audit_logs(
        limit=1,
        action=discord.AuditLogAction.channel_update
    ):
        executor = entry.user
        break
    else:
        return

    channel = after.guild.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title="📁 Canal movido",
        color=discord.Color.orange()
    )
    embed.add_field(name="Canal", value=after.mention, inline=False)
    embed.add_field(name="Moderador", value=executor.mention, inline=False)

    await channel.send(embed=embed)

# ======================
# HELP
# ======================

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📘 SAFE POINTS SABH",
        description="Sistema profesional de puntos y moderación",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="👥 Miembros",
        value=(
            "`+points` `+ranking` `+perfil` `+ola`\n"
            "`+heaven` `+angel` `+montero`\n"
            "`+kuro` `+itadori` `+noob`"
        ),
        inline=False
    )

    embed.add_field(
        name="🛡️ Staff",
        value=(
            "`+dar @user cantidad`\n"
            "`+restar @user cantidad`\n"
            "`+resetpoints @user`\n"
            "`+joke @user tiempo motivo`"
        ),
        inline=False
    )

    embed.set_footer(text="SAFE POINTS SABH • Bot estable")
    await ctx.send(embed=embed)

# ======================
# COMANDOS MIEMBROS
# ======================

@bot.command()
async def ola(ctx):
    await ctx.send(
        embed=discord.Embed(
            description=f"👋 Hola {ctx.author.mention}, ¿cómo estás?",
            color=discord.Color.green()
        )
    )

@bot.command()
async def points(ctx):
    pts = load_points().get(str(ctx.author.id), 0)
    await ctx.send(
        embed=discord.Embed(
            title="⭐ Tus puntos",
            description=f"Tienes **{pts}/{MAX_POINTS}** puntos",
            color=discord.Color.gold()
        )
    )

@bot.command()
async def ranking(ctx):
    data = load_points()
    ranking = sorted(data.items(), key=lambda x: x[1], reverse=True)[:10]
    text = ""
    for i, (uid, pts) in enumerate(ranking, start=1):
        m = ctx.guild.get_member(int(uid))
        if m:
            text += f"**{i}.** {m.mention} — `{pts}` pts\n"

    await ctx.send(
        embed=discord.Embed(
            title="🏆 Ranking",
            description=text or "Sin datos",
            color=discord.Color.purple()
        )
    )

@bot.command()
async def perfil(ctx):
    pts = load_points().get(str(ctx.author.id), 0)
    embed = discord.Embed(title="📄 Perfil", color=discord.Color.blurple())
    embed.add_field(name="Usuario", value=ctx.author.mention)
    embed.add_field(name="Puntos", value=f"{pts}/{MAX_POINTS}")
    await ctx.send(embed=embed)

# ======================
# COMANDOS TEXTO (NO CAMBIADOS)
# ======================

@bot.command()
async def heaven(ctx):
    await ctx.send("🔥 **Heaven** — el mejor estafador de chilitos")

@bot.command()
async def montero(ctx):
    await ctx.send("👑 **Montero** — owner de la comunidad y programador destacado")

@bot.command()
async def itadori(ctx):
    await ctx.send("🛡️ **Itadori** — el mejor head admin")

@bot.command()
async def angel(ctx):
    await ctx.send("💻 **Angel** — programador destacado")

@bot.command()
async def kuro(ctx):
    await ctx.send("🖤 **Kuro** — creador del bot")

@bot.command()
async def noob(ctx):
    await ctx.send("🤡 noob")

# ======================
# COMANDOS STAFF (PUNTOS)
# ======================

@bot.command()
async def dar(ctx, member: discord.Member, cantidad: int):
    if not is_staff(ctx):
        return

    data = load_points()
    uid = str(member.id)
    data[uid] = min(MAX_POINTS, data.get(uid, 0) + cantidad)
    save_points(data)

    embed = discord.Embed(
        title="➕ Puntos añadidos",
        description=f"{member.mention} ahora tiene **{data[uid]}** puntos",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    await send_log(ctx.guild, embed)

@bot.command()
async def restar(ctx, member: discord.Member, cantidad: int):
    if not is_staff(ctx):
        return

    data = load_points()
    uid = str(member.id)
    data[uid] = max(0, data.get(uid, 0) - cantidad)
    save_points(data)

    embed = discord.Embed(
        title="➖ Puntos restados",
        description=f"{member.mention} ahora tiene **{data[uid]}** puntos",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)
    await send_log(ctx.guild, embed)

@bot.command()
async def resetpoints(ctx, member: discord.Member):
    if not is_staff(ctx):
        return

    data = load_points()
    data[str(member.id)] = 0
    save_points(data)

    embed = discord.Embed(
        title="♻️ Reset de puntos",
        description=f"Puntos de {member.mention} reiniciados",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)
    await send_log(ctx.guild, embed)

# ======================
# COMANDO JOKE (MUTE)
# ======================

@bot.command()
async def joke(ctx, member: discord.Member, segundos: int, *, motivo="Broma"):
    if not is_staff(ctx):
        return

    if segundos > MAX_TIMEOUT:
        segundos = MAX_TIMEOUT

    await member.timeout(
        discord.utils.utcnow() + discord.timedelta(seconds=segundos),
        reason=motivo
    )

    embed = discord.Embed(
        title="🔇 Joke aplicado",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="Usuario", value=member.mention, inline=False)
    embed.add_field(name="Duración", value=f"{segundos} segundos", inline=False)
    embed.add_field(name="Motivo", value=motivo, inline=False)
    embed.set_footer(text=f"Aplicado por {ctx.author}")

    await ctx.send(embed=embed)
    await send_log(ctx.guild, embed)

# ======================
# RUN
# ======================

bot.run(TOKEN)
