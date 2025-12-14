from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands
from datetime import datetime
import os

# ===============================
# CONFIGURAÇÕES
# ===============================



TOKEN = os.getenv("SEU_TOKEN")
LOG_CHANNEL_ID = 1449271957026504877
MOD_ROLE_ID = 561438076367273994
PREFIX = "!"

# ===============================
# INTENTS
# ===============================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ===============================
# FUNÇÕES AUXILIARES
# ===============================

@bot.event
async def on_guild_join(guild):
    print(f"Entrei no servidor: {guild.name} ({guild.id})")

async def send_log(guild, title, description, color=discord.Color.red()):
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    await channel.send(embed=embed)

def is_moderator():
    async def predicate(ctx):
        return any(role.id == MOD_ROLE_ID for role in ctx.author.roles)
    return commands.check(predicate)

# ===============================
# EVENTOS
# ===============================

@bot.event
async def on_ready():
    print("================================")
    print("BOT ONLINE COM SUCESSO")
    print(f"Logado como: {bot.user}")
    print("================================")

# ===============================
# COMANDOS
# ===============================

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
@is_moderator()
async def ban(ctx, member: discord.Member, *, reason="Sem motivo informado"):
    try:
        await member.ban(reason=reason)
    except discord.Forbidden:
        return await ctx.send("❌ Não tenho permissão para banir esse usuário.")
    except discord.HTTPException:
        return await ctx.send("❌ Erro ao tentar banir o usuário.")

    await send_log(
        ctx.guild,
        "🔨 BANIMENTO",
        f"👤 **Usuário:** {member}\n"
        f"🛡️ **Moderador:** {ctx.author}\n"
        f"📄 **Motivo:** {reason}"
    )

    await ctx.send(f"✅ {member} foi banido.")

@bot.command()
@is_moderator()
@commands.guild_only()
async def unban(ctx, user_id: int):
    try:
        banned_user = None

        async for ban_entry in ctx.guild.bans():
            if ban_entry.user.id == user_id:
                banned_user = ban_entry.user
                break

        if not banned_user:
            return await ctx.send("❌ Esse usuário não está banido.")

        await ctx.guild.unban(banned_user)

        await send_log(
            ctx.guild,
            "♻️ DESBANIMENTO",
            f"👤 Usuário: {banned_user}\n"
            f"🛡️ Moderador: {ctx.author}",
            discord.Color.green()
        )

        await ctx.send(f"✅ {banned_user} foi desbanido com sucesso.")

    except discord.Forbidden:
        await ctx.send("❌ Não tenho permissão para desbanir usuários.")
    except discord.HTTPException:
        await ctx.send("❌ Erro ao tentar desbanir o usuário.")

@bot.command()
@is_moderator()
async def addrole(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        return await ctx.send("❌ Cargo não encontrado.")

    await member.add_roles(role)

    await send_log(
        ctx.guild,
        "➕ CARGO ADICIONADO",
        f"👤 **Usuário:** {member}\n"
        f"🎭 **Cargo:** {role.name}\n"
        f"🛡️ **Moderador:** {ctx.author}"
    )

    await ctx.send(f"✅ Cargo `{role.name}` adicionado a {member}.")

@bot.command()
@is_moderator()
async def removerole(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        return await ctx.send("❌ Cargo não encontrado.")

    await member.remove_roles(role)

    await send_log(
        ctx.guild,
        "➖ CARGO REMOVIDO",
        f"👤 **Usuário:** {member}\n"
        f"🎭 **Cargo:** {role.name}\n"
        f"🛡️ **Moderador:** {ctx.author}"
    )

    await ctx.send(f"✅ Cargo `{role.name}` removido de {member}.")

# ===============================
# AUDITORIA AUTOMÁTICA
# ===============================

@bot.event
async def on_member_ban(guild, user):
    await send_log(
        guild,
        "🚨 BANIMENTO (AUTOMÁTICO)",
        f"👤 **Usuário:** {user}"
    )

@bot.event
async def on_member_unban(guild, user):
    await send_log(
        guild,
        "♻️ DESBANIMENTO (AUTOMÁTICO)",
        f"👤 **Usuário:** {user}",
        discord.Color.green()
    )

@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        added = set(after.roles) - set(before.roles)
        removed = set(before.roles) - set(after.roles)


# ===============================
# INICIALIZAÇÃO
# ===============================

bot.run(TOKEN)
