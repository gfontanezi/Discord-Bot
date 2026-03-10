import asyncio
import discord
from discord.ext import commands, tasks
import os
from itertools import cycle
from dotenv import load_dotenv

load_dotenv()

# Configuração de Intents (necessário para ler mensagens e membros)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Lista de status rotativos
bot_statuses = cycle([
    "Pokémon Brilliant Diamond e Shining Pearl!", 
    "CS2", 
    "Pokémon Legends: Arceus", 
    "GTA 6", 
    "Pokemon GO!", 
    "Youtube Shorts", 
    "League of Legends", 
    "Pokémon Black e White!", 
    "Valorant", 
    "Pokémon HeartGold e SoulSilver", 
    "Fortnite", 
    "Netflix"
])

# Tarefa para trocar o status a cada 60 segundos
@tasks.loop(seconds=60)
async def change_bot_status():
    await bot.change_presence(activity=discord.Game(next(bot_statuses)))

@bot.event
async def on_ready():
    print(f'Bot está online como {bot.user}!')
    
    # Verificação para evitar erro se o bot reconectar
    if not change_bot_status.is_running():
        change_bot_status.start()
    
    print("Bot pronto para uso. (Use !sync para sincronizar comandos / se necessário)")

# --- COMANDO DE SINCRONIZAÇÃO (NOVO) ---
# Use '!sync' no chat para registrar os comandos de barra (/)
# Somente o dono do bot pode usar este comando.
@bot.command(name='sync')
@commands.is_owner() 
async def sync(ctx):
    msg = await ctx.send("Sincronizando comandos...")
    try:
        synced = await bot.tree.sync()
        await msg.edit(content=f"Sincronizado {len(synced)} comandos com sucesso!")
        print(f"Comandos sincronizados pelo usuário {ctx.author}: {len(synced)}")
    except Exception as e:
        await msg.edit(content=f"Erro ao sincronizar: {e}")
        print(f"Erro de sync: {e}")

# --- Comandos de Exemplo ---

# Comando de Barra (Slash)
@bot.tree.command(name="ola", description="Diz olá para a pessoa.")
async def ola_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f'Olá, {interaction.user.mention}, que bom te ver aqui!')

# Comando de Prefixo (!ola)
@bot.command(name="ola", aliases=['olá', 'oi', 'bomdia', 'boatarde', 'boanoite', 'opa'])
async def ola_prefix(ctx):
    await ctx.send(f'Olá, {ctx.author.mention}, que bom te ver aqui!')

# Carregamento das Cogs (Plugins)
async def load_extensions():
    # Garante que a pasta cogs existe
    if not os.path.exists("cogs"):
        print("Pasta 'cogs' não encontrada.")
        return

    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Carregado: {filename}")
            except Exception as e:
                print(f"Erro ao carregar {filename}: {e}")

async def main():
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if TOKEN is None:
        print("❌ ERRO: Token do Discord não encontrado! Verifique o arquivo .env.")
        return

    async with bot:
        await load_extensions()
        try:
            await bot.start(TOKEN)
        except discord.errors.LoginFailure:
            print("❌ ERRO: Token inválido. Verifique o arquivo .env.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Permite fechar o bot com Ctrl+C sem mostrar erros feios
        pass