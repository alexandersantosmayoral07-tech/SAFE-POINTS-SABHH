import discord
from discord.ext import commands
import json
import os
from flask import Flask
from threading import Thread

# ======================
# CONFIGURACIÓN
# ======================

PREFIX = "+"
TOKEN = os.getenv("TOKEN")  # Token en Secrets
LOG_CHANNEL_ID = 1456092888952737833

STAFF_IDS = [
    1418712877426016319,
    1416613885997355029
]

MAX_POINTS = 50

ROLE_REWARDS = {
    10: 1454953357360759018,
    20: 1454956321672790137,
    30: 1454956952504369202,
    40: 1454958077412376769,
    50: 1454958494649155746
}

POINTS_FILE = "points.json"

# ======================
# FLASK / PREVIEW (UPTIME)
# ======================

app = Flask("")

@app.route("/")
def home():
    return "SAFE POINTS SABH • ONLINE"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_flask).start()

# ======================
# BOT SETUP
# ======================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

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
    return ctx.author.id in STAFF_IDS

# ======================
# EVENTOS
# ======================

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")

# ======================
# HELP
# ======================

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📘 SAFE POINTS SABH",
        description="Sistema profesional de puntos y roles",
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
            "`+joke @user tiempo`"
        ),
        inline=False
    )

    embed.set_footer(text="Hecho por Kuro • SAFE POINTS SABH")
    await ctx.send(embed=embed)

# ======================
# COMANDOS MIEMBROS
# ======================

@bot.command()
async def ola(ctx):
    embed = discord.Embed(
        description=f"👋 Hola {ctx.author.mention}, ¿cómo estás?",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def points(ctx):
    data = load_points()
    pts = data.get(str(ctx.author.id), 0)

    embed = discord.Embed(
        title="⭐ Tus puntos",
        description=f"Tienes **{pts}/{MAX_POINTS}** puntos",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

@bot.command()
async def ranking(ctx):
    data = load_points()
    ranking = sorted(data.items(), key=lambda x: x[1], reverse=True)[:10]

    text = ""
    for i, (uid, pts) in enumerate(ranking, start=1):
        member = ctx.guild.get_member(int(uid))
        if member:
            text += f"**{i}.** {member.mention} — `{pts}` pts\n"

    embed = discord.Embed(
        title="🏆 Ranking",
        description=text or "Sin datos",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

@bot.command()
async def perfil(ctx):
    data = load_points()
    pts = data.get(str(ctx.author.id), 0)

    embed = discord.Embed(
        title="📄 Perfil",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Usuario", value=ctx.author.mention)
    embed.add_field(name="Puntos", value=f"{pts}/{MAX_POINTS}")
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)

# ======================
# COMANDOS TEXTO
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
# COMANDOS STAFF
# ======================

@bot.command()
async def dar(ctx, member: discord.Member, cantidad: int):
    if not is_staff(ctx):
        return

    data = load_points()
    uid = str(member.id)
    data[uid] = min(MAX_POINTS, data.get(uid, 0) + cantidad)
    save_points(data)

    for pts, role_id in ROLE_REWARDS.items():
        if data[uid] >= pts:
            role = ctx.guild.get_role(role_id)
            if role and role not in member.roles:
                await member.add_roles(role)

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
# JOKE (SIMULADO - NO CASTIGA)
# ======================

@bot.command()
async def joke(ctx, member: discord.Member, tiempo: str = "5m"):
    if not is_staff(ctx):
        return

    embed = discord.Embed(
        title="🔇 Joke Mute",
        description=(
            f"👤 **Usuario:** {member.mention}\n"
            f"⏱ **Tiempo:** {tiempo}\n\n"
            "⚠️ *Esto es solo una broma, no se aplicó ningún castigo real*"
        ),
        color=discord.Color.dark_grey()
    )

    await ctx.send(embed=embed)
    await send_log(ctx.guild, embed)

# ======================
# RUN
# ======================

bot.run(TOKEN)
