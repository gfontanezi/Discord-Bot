import discord
from discord.ext import commands
import os
import easy_pil
import random
import asyncio
from functools import partial

class MemberJoinHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("MemberJoinHandler está pronto!")
    
    # Esta função roda fora do loop principal para não travar o bot
    def _gerar_imagem_boas_vindas(self, member_name, guild_name, member_count, avatar_bytes, bg_path):
        bg = easy_pil.Editor(bg_path).resize((1920, 1080))
        avatar_image = easy_pil.load_image(avatar_bytes) # Carrega bytes direto
        avatar = easy_pil.Editor(avatar_image).resize((250, 250)).circle_image()

        font_big = easy_pil.Font.poppins(size=90, variant="bold")
        font_small = easy_pil.Font.poppins(size=60, variant="bold")

        bg.paste(avatar, (835, 340))
        bg.ellipse((835, 340), 250, 250, outline="white", stroke_width=5)

        bg.text((960, 620), f"Bem vindo ao servidor {guild_name}!", font=font_big, stroke_width=2, stroke_fill="black", color="white", align="center")
        bg.text((960, 740), f"{member_name} é o membro #{member_count}!", font=font_small, stroke_width=2, stroke_fill="black", color="white", align="center")
        
        return bg.image_bytes

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.system_channel
        if not channel:
            return

        # Caminho absoluto para evitar erro de arquivo não encontrado
        base_path = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(base_path, "welcome_images")
        
        # Verificação se a pasta existe
        if not os.path.exists(images_dir):
            print(f"ERRO: Pasta {images_dir} não encontrada.")
            return

        images = [img for img in os.listdir(images_dir) if img.endswith(('.png', '.jpg', '.jpeg'))]
        if not images:
            print("ERRO: Nenhuma imagem encontrada na pasta welcome_images.")
            return
            
        random_bg = random.choice(images)
        bg_full_path = os.path.join(images_dir, random_bg)

        # Baixa o avatar de forma assíncrona
        avatar_asset = member.avatar or member.default_avatar
        avatar_bytes = await avatar_asset.read()

        # RODA O PROCESSAMENTO PESADO EM UMA THREAD SEPARADA
        # Isso impede que o bot trave enquanto edita a imagem
        try:
            fn = partial(self._gerar_imagem_boas_vindas, member.name, member.guild.name, member.guild.member_count, avatar_bytes, bg_full_path)
            final_buffer = await asyncio.to_thread(fn)
            
            img_file = discord.File(fp=final_buffer, filename="welcome.jpg")
            await channel.send(f"Olá, {member.mention}, obrigado por entrar no servidor! Leia as regras e divirta-se!", file=img_file)
        except Exception as e:
            print(f"Erro ao gerar imagem de boas-vindas: {e}")
            await channel.send(f"Bem vindo {member.mention}!")

async def setup(bot):
    await bot.add_cog(MemberJoinHandler(bot))