import discord
from discord.ext import commands
from random import choice
import asyncpraw as praw
import emoji
import os # Necessário para ler o .env

class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Pega as credenciais do arquivo .env
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")

        # Verifica se as credenciais foram carregadas
        if not client_id or not client_secret:
            print("⚠️ AVISO: Credenciais do Reddit (ID ou Secret) não encontradas no arquivo .env!")
            self.reddit = None
        else:
            # Inicializa com as variáveis seguras
            self.reddit = praw.Reddit(
                client_id=client_id, 
                client_secret=client_secret, 
                user_agent="script:memealeatorio:v1.0 (by u/Ready_Protection8385)"
            )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} está pronto!')

    # Função auxiliar para verificar se o Reddit carregou
    async def check_reddit(self, ctx):
        if self.reddit is None:
            await ctx.send("❌ O comando não pode ser executado porque as credenciais do Reddit não foram configuradas.")
            return False
        return True

    @commands.command(aliases=['memes'])
    async def meme(self, ctx: commands.Context):
        if not await self.check_reddit(ctx): return

        try:
            subreddit = await self.reddit.subreddit("memes")
            posts_list = []

            async for post in subreddit.hot(limit=30):
                if not post.over_18 and post.author is not None and any(post.url.endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.gif']):
                    author_name = post.author.name
                    posts_list.append((post.url, author_name))
                if post.author is None:
                    posts_list.append((post.url, "N/A"))
            
            if posts_list:
                random_post = choice(posts_list)
                meme_embed = discord.Embed(title="Meme aleatório", description="Mostra algum meme aleatório de r/memes", color=discord.Color.random())
                meme_embed.set_author(name=f"Meme pedido por {ctx.author.name}", icon_url=ctx.author.avatar)
                meme_embed.set_image(url=random_post[0])
                meme_embed.set_footer(text=f"Postado por {random_post[1]}.", icon_url=None)
                await ctx.send(embed=meme_embed)
            else:
                await ctx.send(emoji.emojize("Não consegui encontrar memes :sob:. Tente novamente mais tarde.", language='alias'))
        except Exception as e:
            print(f"Erro no comando meme: {e}")
            await ctx.send("Ocorreu um erro ao buscar o meme.")

    @commands.command()
    async def shitpost(self, ctx: commands.Context):
        if not await self.check_reddit(ctx): return

        try:
            subreddit = await self.reddit.subreddit("shitposting")
            posts_list = []

            async for post in subreddit.hot(limit=30):
                if not post.over_18 and post.author is not None and any(post.url.endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.gif']):
                    author_name = post.author.name
                    posts_list.append((post.url, author_name))
                if post.author is None:
                    posts_list.append((post.url, "N/A"))
            
            if posts_list:
                random_post = choice(posts_list)
                shitpost_embed = discord.Embed(title="Shitpost aleatório", description="Mostra algum shitpost aleatório de r/shitposting", color=discord.Color.random())
                shitpost_embed.set_author(name=f"Shitpost pedido por {ctx.author.name}", icon_url=ctx.author.avatar)
                shitpost_embed.set_image(url=random_post[0])
                shitpost_embed.set_footer(text=f"Postado por {random_post[1]}.", icon_url=None)
                await ctx.send(embed=shitpost_embed)
            else:
                await ctx.send(emoji.emojize("Não consegui encontrar shitpost :sob:. Tente novamente mais tarde.", language='alias'))
        except Exception as e:
            print(f"Erro no comando shitpost: {e}")
            await ctx.send("Ocorreu um erro ao buscar o shitpost.")
    
    @commands.command(aliases=['gato'])
    async def gatos(self, ctx: commands.Context):
        if not await self.check_reddit(ctx): return

        try:
            subreddit = await self.reddit.subreddit("cats")
            posts_list = []

            async for post in subreddit.hot(limit=30):
                if not post.over_18 and post.author is not None and any(post.url.endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.gif']):
                    author_name = post.author.name
                    posts_list.append((post.url, author_name))
                if post.author is None:
                    posts_list.append((post.url, "N/A"))
            
            if posts_list:
                random_post = choice(posts_list)
                cats_embed = discord.Embed(title="Gatos aleatórios", description="Mostra algum gato aleatório de r/cats", color=discord.Color.random())
                cats_embed.set_author(name=f"Gato aleatório pedido por {ctx.author.name}", icon_url=ctx.author.avatar)
                cats_embed.set_image(url=random_post[0])
                cats_embed.set_footer(text=f"Postado por {random_post[1]}.", icon_url=None)
                await ctx.send(embed=cats_embed)
            else:
                await ctx.send(emoji.emojize("Não consegui encontrar gatos :sob:. Tente novamente mais tarde.", language='alias'))
        except Exception as e:
            print(f"Erro no comando gatos: {e}")
            await ctx.send("Ocorreu um erro ao buscar o gato.")

    @commands.command()
    async def pikachusurpreso(self, ctx: commands.Context):
        if not await self.check_reddit(ctx): return

        try:
            subreddit = await self.reddit.subreddit("SurprisedPikachu")
            posts_list = []

            async for post in subreddit.hot(limit=30):
                if not post.over_18 and post.author is not None and any(post.url.endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.gif']):
                    author_name = post.author.name
                    posts_list.append((post.url, author_name))
                if post.author is None:
                    posts_list.append((post.url, "N/A"))
            
            if posts_list:
                random_post = choice(posts_list)
                pikachu_embed = discord.Embed(title="Pikachu surpreso", description="Mostra algum pikachu surpreso ou suas variações aleatório de r/SurprisedPikachu", color=discord.Color.random())
                pikachu_embed.set_author(name=f"Pikachu pedido por {ctx.author.name}", icon_url=ctx.author.avatar)
                pikachu_embed.set_image(url=random_post[0])
                pikachu_embed.set_footer(text=f"Postado por {random_post[1]}.", icon_url=None)
                await ctx.send(embed=pikachu_embed)
            else:
                await ctx.send(emoji.emojize("Não consegui encontrar pikachus :sob:. Tente novamente mais tarde.", language='alias'))
        except Exception as e:
            print(f"Erro no comando pikachu: {e}")
            await ctx.send("Ocorreu um erro ao buscar o pikachu.")

    @commands.command()
    async def craft(self, ctx: commands.Context):
        if not await self.check_reddit(ctx): return

        try:
            subreddit = await self.reddit.subreddit("cs2_stickercrafts")
            posts_list = []

            async for post in subreddit.hot(limit=60):
                if not post.over_18 and post.author is not None and any(post.url.endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.gif']):
                    author_name = post.author.name
                    posts_list.append((post.url, author_name))
                if post.author is None:
                    posts_list.append((post.url, "N/A"))
            
            if posts_list:
                random_post = choice(posts_list)
                craft_embed = discord.Embed(title="Sticker crafts", description="Mostra algum craft do cs aleatório de r/cs2_stickercrafts", color=discord.Color.random())
                craft_embed.set_author(name=f"Craft pedido por {ctx.author.name}", icon_url=ctx.author.avatar)
                craft_embed.set_image(url=random_post[0])
                craft_embed.set_footer(text=f"Postado por {random_post[1]}.", icon_url=None)
                await ctx.send(embed=craft_embed)
            else:
                await ctx.send(emoji.emojize("Não consegui encontrar crafts :sob:. Tente novamente mais tarde.", language='alias'))
        except Exception as e:
            print(f"Erro no comando craft: {e}")
            await ctx.send("Ocorreu um erro ao buscar o craft.")

    def cog_unload(self):
        # Fecha a sessão do reddit de forma segura se ela existir
        if self.reddit:
            self.bot.loop.create_task(self.reddit.close())

async def setup(bot):
    await bot.add_cog(Reddit(bot))