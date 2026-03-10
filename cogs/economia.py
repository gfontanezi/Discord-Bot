import discord
from discord.ext import commands
from db_economia_code import Usuario, async_session, init_db
from sqlalchemy import select
from asyncio import sleep
from random import randint

class Economia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Inicializa as tabelas quando o bot ligar
        await init_db()
        print("Módulo de Economia: Banco de dados inicializado.")

    # Função auxiliar para pegar ou criar usuário de forma assíncrona
    async def obter_usuario(self, session, discord_id):
        stmt = select(Usuario).filter_by(discord_id=discord_id)
        result = await session.execute(stmt)
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            usuario = Usuario(discord_id=discord_id)
            session.add(usuario)
            # Não fazemos commit aqui para permitir transações maiores fora
        return usuario

    @commands.command()
    async def saldo(self, ctx: commands.Context):
        async with async_session() as session:
            usuario = await self.obter_usuario(session, ctx.author.id)
            await session.commit() # Salva a criação se o usuário era novo
            await ctx.reply(f"Olá, {ctx.author.name}! Seu saldo atual é de **{usuario.saldo}** 💸!")

    @commands.command()
    async def pix(self, ctx: commands.Context, membro_alvo: discord.Member, valor: int):
        if valor <= 0:
            await ctx.reply("O valor deve ser maior que zero.")
            return
        
        if membro_alvo.id == ctx.author.id:
            await ctx.reply("Você não pode transferir para si mesmo.")
            return

        async with async_session() as session:
            async with session.begin(): # Inicia uma transação atômica
                remetente = await self.obter_usuario(session, ctx.author.id)
                
                if remetente.saldo < valor:
                    await ctx.reply(f"Saldo insuficiente! Você tem apenas {remetente.saldo} 💸.")
                    return

                destinatario = await self.obter_usuario(session, membro_alvo.id)
                
                remetente.saldo -= valor
                destinatario.saldo += valor
            
            # O commit acontece automaticamente ao sair do bloco 'async with session.begin()' se não houver erro
            await ctx.reply(f"✅ Transferência de {valor} 💸 para {membro_alvo.name} realizada com sucesso!")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def explorar(self, ctx: commands.Context):
        tempo_exploracao = 5
        msg = await ctx.reply(f"🗺️ Explorando... Aguarde {tempo_exploracao} segundos.")
        
        await sleep(tempo_exploracao) 
        notas = randint(15, 30)
        
        async with async_session() as session:
            async with session.begin():
                usuario = await self.obter_usuario(session, ctx.author.id)
                usuario.saldo += notas
        
        await msg.edit(content=f"Exploração finalizada! {ctx.author.mention}, você encontrou **{notas}** 💸 notas!")

    @explorar.error
    async def explorar_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"⏳ Aguarde **{error.retry_after:.1f}s** para explorar novamente.")
        else:
            print(f"Erro no explorar: {error}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Economia(bot))