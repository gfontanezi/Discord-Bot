import asyncio
import discord
from discord.ext import commands, tasks
import os
from itertools import cycle
from dotenv import load_dotenv

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

bot_statuses = cycle(["Pokémon Brilliant Diamond e Shining Pearl!", "CS2", "Pokémon Legends: Arceus", "GTA 6", "Pokemon GO!", "Youtube Shorts", "League of Legends", "Pokémon Black e White!", "Valorant", "Pokémon HeartGold e SoulSilver", "Fortnite", "Netflix",])

#trocar status do bot a cada 60 segundos, para algum aleatório da lista bot_statuses
@tasks.loop(seconds=60)
async def change_bot_status():
    await bot.change_presence(activity=discord.Game(next(bot_statuses)))

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')


if TOKEN is None:
    raise ValueError("Token do Discord não encontrado! Verifique se o arquivo .env existe e contém a variável DISCORD_TOKEN.")



@bot.event
async def on_ready():
    print('Bot está online!')
    change_bot_status.start()
    try:
        synced_commands = await bot.tree.sync()
        print(f"Sincronizado {len(synced_commands)} comandos com sucesso!")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")

#define algum comando que será chamado com "!comando"
@bot.tree.command(name="ola", description="Diz olá para a pessoa.")
async def ola(interaction: discord.Interaction):
    await interaction.response.send_message(f'Olá, {interaction.user.mention}, que bom te ver aqui!')

#define algum comando que será executado quando mandar "!comando"
@bot.command(aliases=['olá', 'oi', 'bomdia', 'boatarde', 'boanoite', 'opa'])
async def ola(ctx):
    await ctx.send(f'Olá, {ctx.author.mention}, que bom te ver aqui!')

async def load():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f'cogs.{filename[:-3]}')
        
async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)

asyncio.run(main())
