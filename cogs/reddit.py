import discord
from discord.ext import commands
from random import choice
import asyncpraw as praw
import emoji

class Reddit(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.reddit = praw.Reddit(client_id="toEzrrK0Yb6IVyMvYWjGpw", client_secret="JQmvuQpiEEXKqsSlkIWQk8XkTcPwHg", user_agent="script:memealeatorio:v1.0 (by u/Ready_Protection8385)")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} está pronto!')

    @commands.command(aliases=['memes'])
    async def meme(self, ctx: commands.Context):

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

            meme_embed = discord.Embed(title="Meme aleatório", description="Mostra algum meme aleatório de r/memes",color=discord.Color.random())
            meme_embed.set_author(name=f"Meme pedido por {ctx.author.name}", icon_url=ctx.author.avatar)
            meme_embed.set_image(url=random_post[0])
            meme_embed.set_footer(text=f"Postado por {random_post[1]}.", icon_url=None)
            await ctx.send(embed=meme_embed)
        
        else:
            await ctx.send(emoji.emojize("Não consegui encontrar memes :sob:. Tente novamente mais tarde.", language='alias'))

    @commands.command()
    async def shitpost(self, ctx: commands.Context):

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

            shitpost_embed = discord.Embed(title="Shitpost aleatório", description="Mostra algum shitpost aleatório de r/shitposting",color=discord.Color.random())
            shitpost_embed.set_author(name=f"shitpost pedido por {ctx.author.name}", icon_url=ctx.author.avatar)
            shitpost_embed.set_image(url=random_post[0])
            shitpost_embed.set_footer(text=f"Postado por {random_post[1]}.", icon_url=None)
            await ctx.send(embed=shitpost_embed)
        
        else:
            await ctx.send(emoji.emojize("Não consegui encontrar shipost :sob:. Tente novamente mais tarde.", language='alias'))
    
    @commands.command(aliases=['gato'])
    async def gatos(self, ctx: commands.Context):

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

            cats_embed = discord.Embed(title="Gatos aleatórios", description="Mostra algum gato aleatório de r/cats",color=discord.Color.random())
            cats_embed.set_author(name=f"Gato aleatório pedido por {ctx.author.name}", icon_url=ctx.author.avatar)
            cats_embed.set_image(url=random_post[0])
            cats_embed.set_footer(text=f"Postado por {random_post[1]}.", icon_url=None)
            await ctx.send(embed=cats_embed)
        
        else:
            await ctx.send(emoji.emojize("Não consegui encontrar gatos :sob:. Tente novamente mais tarde.", language='alias'))

    @commands.command()
    async def pikachusurpreso(self, ctx: commands.Context):

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

            pikachu_embed = discord.Embed(title="Pikachu surpreso", description="Mostra algum pikachu surpreso ou suas variações aleatório de r/SurprisedPikachu",color=discord.Color.random())
            pikachu_embed.set_author(name=f"Pikachu pedido por {ctx.author.name}", icon_url=ctx.author.avatar)
            pikachu_embed.set_image(url=random_post[0])
            pikachu_embed.set_footer(text=f"Postado por {random_post[1]}.", icon_url=None)
            await ctx.send(embed=pikachu_embed)
        
        else:
            await ctx.send(emoji.emojize("Não consegui encontrar pikachus :sob:. Tente novamente mais tarde.", language='alias'))

    @commands.command()
    async def craft(self, ctx: commands.Context):

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

            craft_embed = discord.Embed(title="Sticker crafts", description="Mostra algum craft do cs aleatório de r/cs2_stickercrafts",color=discord.Color.random())
            craft_embed.set_author(name=f"Craft pedido por {ctx.author.name}", icon_url=ctx.author.avatar)
            craft_embed.set_image(url=random_post[0])
            craft_embed.set_footer(text=f"Postado por {random_post[1]}.", icon_url=None)
            await ctx.send(embed=craft_embed)
        
        else:
            await ctx.send(emoji.emojize("Não consegui encontrar crafts :sob:. Tente novamente mais tarde.", language='alias'))

    def cog_unload(self):
        self.bot.loop.create_task(self.reddit.close())

async def setup(bot):
    await bot.add_cog(Reddit(bot)) 