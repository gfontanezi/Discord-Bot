import discord
from discord.ext import commands
from db_economia_code import Usuario, _Sessao
from asyncio import sleep
from random import randint

def obter_usuario(discord_id):
    # Obtém um usuário do banco de dados ou o cria se não existir.
    with _Sessao() as sessao:
        usuario_db = sessao.query(Usuario).filter_by(discord_id=discord_id).first()
        if not usuario_db:
            usuario_db = Usuario(discord_id=discord_id)
            sessao.add(usuario_db)
            sessao.commit()
        return usuario_db
    

class Economia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def saldo(self, ctx: commands.Context):
        # Verifica o saldo atual do usuário.
        usuario_db = obter_usuario(ctx.author.id)
        saldo_usuario = usuario_db.saldo
        await ctx.reply(f"Olá, {ctx.author.name}! Seu saldo atual é de **{saldo_usuario}** 💸!")

    @commands.command()
    async def pix(self, ctx: commands.Context, membro_alvo: discord.Member, valor: int):
        # Transfere moedas para outro membro.
        if valor <= 0:
            await ctx.reply("O valor a ser transferido deve ser maior que zero.")
            return
        
        if membro_alvo == ctx.author:
            await ctx.reply("Você não pode transferir moedas para si mesmo.")
            return

        usuario_db = obter_usuario(ctx.author.id)
        
        if valor > usuario_db.saldo:
            await ctx.reply(f"Desculpe, {ctx.author.name}, você não tem saldo suficiente para transferir {valor} 💸.")
            return

        usuario_alvo_db = obter_usuario(membro_alvo.id)

        with _Sessao() as sessao:
            # Reanexa os objetos à sessão para garantir que estão "vivos"
            usuario_db = sessao.merge(usuario_db)
            usuario_alvo_db = sessao.merge(usuario_alvo_db)

            usuario_db.saldo -= valor
            usuario_alvo_db.saldo += valor
            sessao.commit()

            await ctx.reply(f"Transferência bem-sucedida! Você transferiu {valor} 💸 para {membro_alvo.name}. Seu novo saldo é {usuario_db.saldo} 💸.")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.member) # 1 uso a cada 10 segundos por membro
    async def explorar(self, ctx: commands.Context):
        # Explora para encontrar moedas.
        tempo_exploracao = 5
        mensagem_aguarde = await ctx.reply(f"Explorando... Isso levará {tempo_exploracao} segundos. Por favor, aguarde.")
        
        await sleep(tempo_exploracao)

        notas_ganhas = randint(15, 30)
        usuario_db = obter_usuario(ctx.author.id)

        with _Sessao() as sessao:
            usuario_db = sessao.merge(usuario_db)
            usuario_db.saldo += notas_ganhas
            sessao.commit()

        await mensagem_aguarde.edit(content=f"Exploração finalizada! {ctx.author.mention}, você encontrou **{notas_ganhas}** 💸 notas!")

    @explorar.error
    async def explorar_error(self, ctx: commands.Context, error):
        # Tratador de erros específico para o comando explorar.
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"Calma lá, {ctx.author.name}! Você já explorou recentemente. Por favor, aguarde **{error.retry_after:.2f}** segundos antes de tentar novamente.")
        else:
            print(f"Ocorreu um erro no comando explorar: {error}")
            await ctx.reply("Ocorreu um erro inesperado ao tentar executar este comando.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Economia(bot))