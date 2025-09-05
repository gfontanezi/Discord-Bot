import asyncio
from asyncio import run_coroutine_threadsafe
from discord.ui import View, Select, Button
from discord import SelectOption
import discord
from discord.ext import commands
from urllib import parse, request
import re
import os
from yt_dlp import YoutubeDL
import json
import lyricsgenius
from dotenv import load_dotenv

# Classe de Botões
class SongSelect(Select):
    def __init__(self, songs):
        options = [
            discord.SelectOption(label=f"{i+1} - {title[:95]}", value=str(i))
            for i, title in enumerate(songs)
        ]
        super().__init__(placeholder="Escolha uma opção", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        self.view.chosen_index = int(self.values[0])
        self.view.interaction = interaction
        self.view.stop()

class CancelButton(Button):
    def __init__(self):
        super().__init__(label="Cancelar", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        self.view.cancelled = True
        self.view.interaction = interaction
        self.view.stop()

class SearchView(View):
    def __init__(self, songs):
        super().__init__(timeout=60)
        self.chosen_index = None
        self.cancelled = False
        self.interaction = None
        self.add_item(SongSelect(songs))
        self.add_item(CancelButton())

# Cog de Música
class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = {}
        self.is_paused = {}
        self.musicQueue = {}
        self.queueIndex = {} 
        self.vc = {} 

        self.loop_single = {}
        self.loop_queue = {}

        load_dotenv()

        TOKEN = os.getenv('GENIUS_TOKEN')
        if TOKEN is None:
            raise ValueError("Token do Discord não encontrado! Verifique se o arquivo .env existe e contém a variável DISCORD_TOKEN.")
        
        
        if not TOKEN:
            self.genius = None 
        else:
            try:
                self.genius = lyricsgenius.Genius(TOKEN,
                    verbose=False,
                    remove_section_headers=True,
                    skip_non_songs=True,
                    timeout=10
                    ) 
                print("Cliente LyricsGenius inicializado com sucesso.")
            except Exception as e:
                print(f"Erro ao inicializar LyricsGenius: {e}")
                self.genius = None

        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        # Cores para embeds
        self.embedBlue = 0x2c76dd
        self.embedRed = 0xd1141
        self.embedGreen = 0x58cc02
        self.embedPurple = 0x9b59b6
        self.embedYellow = 0xFFD700
        self.embedYellow2 = 0xFFFF00
        self.embedOrange = 0xFFA500

    # Eventos
    @commands.Cog.listener()
    async def on_ready(self):
        print("Music Cog está pronto!")
        for guild in self.bot.guilds:
            await self.initialize_guild_state(guild.id)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"Entrou no servidor: {guild.name} (ID: {guild.id})")
        await self.initialize_guild_state(guild.id)

    async def initialize_guild_state(self, guild_id):
        # Inicializa o estado para um servidor específico.
        gid = int(guild_id)
        if gid not in self.musicQueue:
            self.musicQueue[gid] = []
            self.queueIndex[gid] = 0
            self.vc[gid] = None
            self.is_paused[gid] = False
            self.is_playing[gid] = False
            self.loop_single[gid] = False
            self.loop_queue[gid] = False
            print(f"Estado inicializado para o servidor ID: {gid}")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Desconectar se o bot ficar sozinho no canal
        gid = int(member.guild.id)
        if gid not in self.vc or not self.vc.get(gid): # Verifica se o estado do servidor foi inicializado
             await self.initialize_guild_state(gid) # Inicializa se não foi

        # Verifica se o bot estava conectado
        if not self.vc.get(gid) or not self.vc[gid].is_connected():
            return

        # Verifica se o canal de antes existe e é diferente do canal de depois (ou se saiu do canal)
        if member.id != self.bot.user.id and before.channel and (not after.channel or after.channel.id != before.channel.id):
            # Verifica se o canal que o membro saiu é o canal onde o bot está e os membros restantes, sem contar outros bots 
            if before.channel.id == self.vc[gid].channel.id:
                remaining_members = self.vc[gid].channel.members
                human_members = [m for m in remaining_members if not m.bot]

                if not human_members: 
                    print(f"Bot sozinho no canal {before.channel.name}, desconectando...")
                    self.is_playing[gid] = self.is_paused[gid] = False
                    self.musicQueue[gid] = []
                    self.queueIndex[gid] = 0
                    await self.vc[gid].disconnect()
                    self.vc[gid] = None


    # Funções de Embed 
    def now_playing_embed(self, guild_id, song):
        embed = discord.Embed(
            title="Tocando Agora 🎶",
            description=f"[{song['title']}]({song['link']})",
            colour=self.embedGreen # Verde para indicar sucesso/tocando
        )
        if song.get('thumbnail'):
             embed.set_thumbnail(url=song['thumbnail'])

        embed.set_footer(text="Dj Pikachu no comando!", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        return embed

    def added_song_embed(self, ctx, song):
        embed = discord.Embed(
            title="Adicionada à Fila ✅",
            description=f"[{song['title']}]({song['link']})",
            colour=self.embedBlue # Azul para informação
        )
        if song.get('thumbnail'):
            embed.set_thumbnail(url=song['thumbnail'])
        embed.set_footer(text=f'Música adicionada por {ctx.author.display_name}', icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        return embed

    def removed_song_embed(self, ctx, song):
        embed = discord.Embed(
            title="Música Removida da Fila ❌",
            description=f"[{song['title']}]({song['link']})",
            colour=self.embedRed
        )
        if song.get('thumbnail'):
            embed.set_thumbnail(url=song['thumbnail'])
        embed.set_footer(text=f'Música removida por {ctx.author.display_name}', icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        return embed

    # -Funções Auxiliares de Música-
    # Garante que o bot entre no canal
    async def join_VC(self, ctx, channel):
        gid = int(ctx.guild.id)
        if gid not in self.vc: await self.initialize_guild_state(gid)

        if self.vc.get(gid) is None or not self.vc[gid].is_connected():
            self.vc[gid] = await channel.connect()
            if self.vc[gid]:
                print(f"Conectado ao canal de voz: {channel.name} no servidor {ctx.guild.name}")
            else:
                 print(f"Falha ao conectar no canal de voz: {channel.name}")
                 await ctx.send("Não consegui me conectar ao canal de voz.")
                 return False
        elif self.vc[gid].channel.id != channel.id:
             print(f"Movendo para o canal de voz: {channel.name} no servidor {ctx.guild.name}")
             await self.vc[gid].move_to(channel)

        return True


    # Função para extrair música solicitada pelo search
    def get_YT_title(self, videoID):
        params = {"format": "json", "url": f"https://www.youtube.com/watch?v={videoID}"}
        url = "https://www.youtube.com/oembed"
        queryString = parse.urlencode(params)
        url = url + '?' + queryString
        try:
            with request.urlopen(url) as response:
                responseText = response.read()
                data = json.loads(responseText.decode())
                return data.get('title', 'Título Desconhecido')
        except Exception as e:
            print(f"Erro ao obter título via oembed para {videoID}: {e}")
            return "Título Desconhecido"

    # Função para mostrar os 10 primeiros resultados de uma pesquisa
    def search_YT(self, search):
        query = parse.urlencode({"search_query": search})
        try:
            # Adiciona um User-Agent para parecer um navegador comum
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            req = request.Request(f"https://www.youtube.com/results?{query}", headers=headers)
            with request.urlopen(req) as html:
                video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            # Remove duplicados mantendo a ordem e pega os 10 primeiros resultados únicos
            return list(dict.fromkeys(video_ids))[:10]
        except Exception as e:
            print(f"Erro ao buscar no YouTube com regex: {e}")
            return []

    # Função para pegar o áudio da música no Youtube
    async def extract_YT(self, url):
        def sync_extract():
            #Opções da extração
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'extract_flat': False,
                'force_generic_extractor': False,
                'source_address': '0.0.0.0'
            }
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    # Verifica se é um vídeo único
                    if 'entries' in info:
                         # Se for uma lista, pega o primeiro
                         info = info['entries'][0]

                    # Limpa os dados antes de retornar
                    return {
                        'link': info.get('webpage_url', url),
                        'thumbnail': info.get('thumbnail'),
                        'source': info.get('url'),
                        'title': info.get('title', 'Título Desconhecido'),
                        'duration': info.get('duration'),
                    }
            except Exception as e:
                print(f"Erro no yt-dlp ao extrair '{url}': {e}")
                return None 
        return await asyncio.to_thread(sync_extract)
    
    # Função para pegar a letra da música
    def clean_song_title(self, title):
        # Remove conteúdo entre parênteses e colchetes
        title = re.sub(r'\([^)]*\)', '', title)
        title = re.sub(r'\[[^\]]*\]', '', title)
        # Remove palavras-chave comuns (case-insensitive)
        keywords = ['official', 'music', 'video', 'audio', 'lyrics', 'lyric', 'hd', 'hq', 'live', 'ft.', 'feat.']
        # Constrói um regex para encontrar essas palavras como palavras inteiras
        pattern = r'\b(' + '|'.join(keywords) + r')\b'
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        title = ' '.join(title.split())
        return title.strip()

    # Função para a próxima música tocar quando uma acabar
    def play_next(self, ctx):
        # Callback executado após uma música terminar
        gid = int(ctx.guild.id)
        if gid not in self.vc or not self.vc.get(gid): return 
        # Garante que o estado do loop existe para este gid
        if gid not in self.loop_single: self.loop_single[gid] = False
        if gid not in self.loop_queue: self.loop_queue[gid] = False


        if self.is_paused[gid]: # Não faça nada se estiver pausado
            return

        # Lógica do loop
        should_play_next_normally = True
        next_index = self.queueIndex[gid] # Assume que vamos repetir ou ficar parado por padrão

        if self.loop_single.get(gid, False):
            # Loop single ativo: não incrementa o índice, apenas pega a música atual de novo
            print(f"Loop single ativo para GID {gid}. Repetindo índice {self.queueIndex[gid]}.")
            next_index = self.queueIndex[gid]
            should_play_next_normally = False 
        elif self.queueIndex[gid] + 1 < len(self.musicQueue[gid]):
             # Não é loop single, e há uma próxima música na fila
             next_index = self.queueIndex[gid] + 1
             should_play_next_normally = False 
        elif self.loop_queue.get(gid, False) and self.musicQueue[gid]:
             # Fim da fila, mas loop queue está ativo e a fila não está vazia
             print(f"Loop queue ativo para GID {gid}. Voltando ao início.")
             next_index = 0 # Volta para o início da fila
             should_play_next_normally = False
             coro_loop = ctx.send("🔁 Voltando ao início da fila!")
             run_coroutine_threadsafe(coro_loop, self.bot.loop)


        if should_play_next_normally:
             # Nenhuma condição de loop satisfeita, fim da fila normal
             print(f"Fim da fila (ou loop desativado) no servidor {gid}")
             self.is_playing[gid] = False
             self.queueIndex[gid] += 1 
             coro_end = ctx.send("⏹️ Fim da fila de músicas!")
             run_coroutine_threadsafe(coro_end, self.bot.loop)
             return

        self.queueIndex[gid] = next_index # Atualiza o índice atual
        song_info = self.musicQueue[gid][self.queueIndex[gid]]
        song = song_info[0]
        source = song.get('source')

        if not source:
             print(f"Erro: Música '{song.get('title')}' no índice {self.queueIndex[gid]} não tem URL de source.")
             # Tenta pular para a próxima
             error_msg = f"Erro ao obter link para {song.get('title', 'próxima música')}. Tentando pular..."
             run_coroutine_threadsafe(ctx.send(error_msg), self.bot.loop)
             # Chama play_next de novo para tentar o próximo índice
             self.bot.loop.call_later(0.5, self.play_next_safe, ctx, None)
             return

        # Envia o embed "Tocando Agora"
        if not self.loop_single.get(gid, False): # Só envia se não for loop single
             coro = ctx.send(embed=self.now_playing_embed(gid, song))
             future = run_coroutine_threadsafe(coro, self.bot.loop)
             try:
                 future.result(timeout=5)
             except TimeoutError:
                 print("Timeout ao enviar 'Tocando Agora' do callback play_next")
             except Exception as e:
                 print(f"Erro ao enviar 'Tocando Agora' do callback play_next: {e}")
        else:
             print(f"Loop single: Não enviando 'Tocando Agora' para evitar spam para GID {gid}")


        # Toca a música 
        try:
             # Verifica se ainda está conectado
             if not self.vc.get(gid) or not self.vc[gid].is_connected():
                  print(f"Bot desconectado antes de tocar a próxima música em GID {gid}. Parando.")
                  self.is_playing[gid] = False
                  return

             self.vc[gid].play(
                 discord.FFmpegPCMAudio(source, **self.FFMPEG_OPTIONS),
                 after=lambda e: self.play_next_safe(ctx, e) 
             )
             self.is_playing[gid] = True 
             self.is_paused[gid] = False 
        except discord.errors.ClientException as e:
              print(f"ClientException ao iniciar playback em play_next para {song.get('title')} GID {gid}: {e}")
              run_coroutine_threadsafe(ctx.send(f"Erro ao tocar {song.get('title')}: {e}"), self.bot.loop)
              self.is_playing[gid] = False 
        except Exception as e:
             print(f"Erro genérico ao iniciar playback em play_next para {song.get('title')} GID {gid}: {e}")
             run_coroutine_threadsafe(ctx.send(f"Erro inesperado ao tocar {song.get('title')}."), self.bot.loop)
             self.is_playing[gid] = False 
             self.bot.loop.call_later(0.5, self.play_next_safe, ctx, e)

    def play_next_safe(self, ctx, error):
        if error:
            print(f'Erro no player detectado no callback after: {error}')
        self.play_next(ctx)

    async def play_music(self, ctx):
        gid = int(ctx.guild.id)
        if gid not in self.musicQueue: 
            await self.initialize_guild_state(gid)

        if self.queueIndex[gid] < len(self.musicQueue[gid]):
            if not ctx.voice_client: # Se não estiver conectado, tenta conectar no canal atual
                target_channel = self.musicQueue[gid][self.queueIndex[gid]][1] 
                if not await self.join_VC(ctx, target_channel):
                     await ctx.send("Não foi possível conectar ao canal de voz para tocar a música.")
                     self.is_playing[gid] = False
                     self.is_paused[gid] = False
                     return

            self.is_playing[gid] = True
            self.is_paused[gid] = False

            song_info = self.musicQueue[gid][self.queueIndex[gid]]
            song = song_info[0]
            source = song.get('source')

            # Se não conseguir tocar a música, ele tenta tocar a próxima, se houver
            if not source:
                 await ctx.send(f"Erro: Não foi possível obter o link para tocar '{song.get('title')}'. Pulando...")
                 self.queueIndex[gid] += 1
                 await self.play_music(ctx)
                 return

            await ctx.send(embed=self.now_playing_embed(gid, song))

            try:
                 # Garante que está conectado antes de tocar
                 if not self.vc.get(gid) or not self.vc[gid].is_connected():
                      target_channel = song_info[1]
                      if not await self.join_VC(ctx, target_channel):
                           await ctx.send("Perdi a conexão de voz antes de tocar.")
                           self.is_playing[gid] = False
                           return

                 self.vc[gid].play(
                     discord.FFmpegPCMAudio(source, **self.FFMPEG_OPTIONS),
                     after=lambda e: self.play_next_safe(ctx, e)
                 )
            except discord.errors.ClientException as e:
                  await ctx.send(f"Erro ao tentar tocar: {e}. Verifique se já não estou tocando algo.")
                  self.is_playing[gid] = False # Reseta estado se deu erro ao iniciar
            except Exception as e:
                 await ctx.send(f"Ocorreu um erro inesperado ao iniciar a música: {e}")
                 print(f"Erro ao iniciar playback em play_music para {song.get('title')}: {e}")
                 self.is_playing[gid] = False
        else:
            print(f"play_music chamado com índice ({self.queueIndex[gid]}) fora do tamanho da fila ({len(self.musicQueue[gid])})")
            self.is_playing[gid] = False
            await ctx.send("Não há músicas na fila para tocar.")


    # -Comandos do Bot- 
    # Comando para tocar música
    @commands.command(name='play', aliases=['tocar', 'p'], help='Toca uma música ou adiciona à fila.')
    async def play(self, ctx, *, search: str = None):
        gid = int(ctx.guild.id)
        if gid not in self.musicQueue: await self.initialize_guild_state(gid)

        try:
            userChannel = ctx.author.voice.channel
            if not userChannel:
                await ctx.send("Você precisa estar em um canal de voz para usar este comando!")
                return
        except AttributeError:
            await ctx.send("Você precisa estar em um canal de voz para usar este comando!")
            return

        # Se !play for usado sem digitar nada e algo estiver pausado, retoma a música atual
        if search is None:
            if self.is_paused[gid] and self.vc.get(gid):
                self.vc[gid].resume()
                self.is_playing[gid] = True
                self.is_paused[gid] = False
                await ctx.send("▶️ Retomado!")
                return
            elif not self.is_playing[gid] and self.musicQueue[gid] and self.queueIndex[gid] < len(self.musicQueue[gid]):
                 await ctx.send("Reiniciando a música atual na fila...")
                 await self.play_music(ctx)
                 return
            elif self.is_playing[gid]:
                 await ctx.send("Já estou tocando algo. Use '!add' ou '!play <nome>' para adicionar à fila.")
                 return
            else:
                 await ctx.send("A fila está vazia e nada está pausado. Use '!play <nome>' para tocar algo.")
                 return

        await ctx.send(f"🔎 Procurando por `{search}`...")

        # Tenta extrair diretamente se for uma URL
        if "youtube.com/watch?v=" in search or "youtu.be/" in search:
             song = await self.extract_YT(search)
        else:
             # Se não for URL, ele pesquisa
             video_ids = self.search_YT(search)
             if not video_ids:
                 await ctx.send(f"Não encontrei resultados para `{search}` no YouTube.")
                 return
             # Pega o primeiro resultado da busca
             first_result_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
             song = await self.extract_YT(first_result_url)

        if not song or not song.get('source'):
            await ctx.send(f"Não consegui obter informações ou o link de áudio para `{search}`. Tente novamente ou com outros termos.")
            return

        self.musicQueue[gid].append([song, userChannel])

        # Se nada estiver tocando nem pausado, começa a tocar a música adicionada
        if not self.is_playing[gid] and not self.is_paused[gid]:
             if len(self.musicQueue[gid]) == 1:
                  self.queueIndex[gid] = 0
             # Se já havia músicas mas não estava tocando e ajusta o índice para a última adicionada
             elif self.queueIndex[gid] >= len(self.musicQueue[gid]) -1 :
                   self.queueIndex[gid] = len(self.musicQueue[gid]) - 1


             await self.play_music(ctx)
        else:
            # Se já está tocando ou pausado, apenas adiciona à fila e informa
            await ctx.send(embed=self.added_song_embed(ctx, song))

    # Comando para dar loop
    @commands.command(name='loop', aliases=['repeat'], help='Define o modo de repetição (single/queue/off).')
    async def loop(self, ctx, mode: str = None):
        gid = int(ctx.guild.id)
        if gid not in self.musicQueue: await self.initialize_guild_state(gid)

        if mode is None:
            # Mostra o status atual do loop
            status = "desativado"
            if self.loop_single.get(gid, False):
                status = "repetindo a música atual (single)"
            elif self.loop_queue.get(gid, False):
                status = "repetindo a fila (queue)"
            await ctx.send(f"🔁 Modo de loop atual: **{status}**.")
            return

        mode = mode.lower()
        if mode == 'single' or mode == 'track' or mode == 'one':
            self.loop_single[gid] = True
            self.loop_queue[gid] = False
            await ctx.send("🔁 Loop da música atual **ativado**.")
        elif mode == 'queue' or mode == 'all':
            self.loop_single[gid] = False
            self.loop_queue[gid] = True
            await ctx.send("🔁 Loop da fila **ativado**.")
        elif mode == 'off' or mode == 'none' or mode == 'disable':
            self.loop_single[gid] = False
            self.loop_queue[gid] = False
            await ctx.send("🔁 Loop **desativado**.")
        else:
            await ctx.send("Modo inválido. Use `single`, `queue` ou `off`.")

    # Comando add, adiciona uma música a fila, mas não reproduz no momento
    @commands.command(name='add', aliases=['adicionar', 'a'], help='Adiciona uma música à fila sem iniciar a reprodução.')
    async def add(self, ctx, *, search: str):
        gid = int(ctx.guild.id)
        if gid not in self.musicQueue: await self.initialize_guild_state(gid)

        try:
            userChannel = ctx.author.voice.channel
            if not userChannel:
                await ctx.send("Você precisa estar em um canal de voz para adicionar músicas!")
                return
        except AttributeError:
            await ctx.send("Você precisa estar em um canal de voz para adicionar músicas!")
            return

        await ctx.send(f"🔎 Procurando e adicionando `{search}` à fila...")

        # Tenta extrair diretamente se for uma URL
        if "youtube.com/watch?v=" in search or "youtu.be/" in search:
             song = await self.extract_YT(search)
        else:
             # Pesquisa se não for URL
             video_ids = self.search_YT(search)
             if not video_ids:
                 await ctx.send(f"Não encontrei resultados para `{search}` no YouTube.")
                 return
             first_result_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
             song = await self.extract_YT(first_result_url)

        if not song or not song.get('source'):
            await ctx.send(f"Não consegui obter informações ou o link de áudio para `{search}`.")
            return

        self.musicQueue[gid].append([song, userChannel])
        await ctx.send(embed=self.added_song_embed(ctx, song))

    # Comando para remover a última música adicionada à fila
    @commands.command(name='remove', aliases=['remover', 'r'], help='Remove a última música adicionada à fila.')
    async def remove(self, ctx):
        gid = int(ctx.guild.id)
        if gid not in self.musicQueue: await self.initialize_guild_state(gid)

        if not self.musicQueue[gid]:
            await ctx.send("A fila já está vazia.")
            return

        # Remove o último item da lista (a última música adicionada)
        removed_song_info = self.musicQueue[gid].pop()
        removed_song = removed_song_info[0]

        await ctx.send(embed=self.removed_song_embed(ctx, removed_song))

        # Se a fila ficou vazia e o bot estava conectado, para e/ou desconecta
        if not self.musicQueue[gid] and self.vc.get(gid) and self.vc[gid].is_connected():
            if self.is_playing[gid] or self.is_paused[gid]:
                print("Fila esvaziada via remove, parando player.")
                self.vc[gid].stop()
            self.is_playing[gid] = self.is_paused[gid] = False
            self.queueIndex[gid] = 0

        elif self.queueIndex[gid] >= len(self.musicQueue[gid]):
             print("Índice ajustado após remoção.")


    @commands.command(name='search', aliases=['find', 'f', 'pesquisar'], help='Pesquisa no YouTube e permite escolher qual adicionar.')
    async def search(self, ctx, *, query: str):
        gid = int(ctx.guild.id)
        if gid not in self.musicQueue: await self.initialize_guild_state(gid)

        try:
            userChannel = ctx.author.voice.channel
            if not userChannel:
                await ctx.send("Você deve estar em um canal de voz para pesquisar músicas!")
                return
        except AttributeError:
            await ctx.send("Você deve estar em um canal de voz para pesquisar músicas!")
            return

        await ctx.send(f"🔎 Pesquisando por: `{query}`...")

        songTokens = self.search_YT(query)
        if not songTokens:
            await ctx.send(f"Não encontrei resultados para `{query}`.")
            return

        # Busca os títulos (usando a função auxiliar)
        songNames = []
        temp_message = await ctx.send("Obtendo títulos dos resultados...")
        for token in songTokens:
            title = self.get_YT_title(token) 
            songNames.append(title if title else f"ID: {token}")
            await asyncio.sleep(0.1)

        await temp_message.delete()

        if not songNames:
             await ctx.send("Não consegui obter os títulos dos vídeos encontrados.")
             return

        # Cria a View com as opções
        view = SearchView(songNames)
        embed = discord.Embed(
            title="Resultados da Pesquisa 🔎",
            description="Escolha uma música abaixo:",
            colour=self.embedYellow2
        )
        message = await ctx.send(embed=embed, view=view)

        # Espera pela interação do usuário ou timeout
        await view.wait()
        await message.delete()

        if view.cancelled:
            await ctx.send("Pesquisa cancelada.")
            return
        if view.chosen_index is None:
            await ctx.send("Tempo esgotado para a escolha.")
            return

        chosen_index = view.chosen_index
        chosen_token = songTokens[chosen_index]
        chosen_url = f"https://www.youtube.com/watch?v={chosen_token}"

        await ctx.send(f"🛠️ Processando sua escolha: `{songNames[chosen_index]}`...")
        song = await self.extract_YT(chosen_url)

        if not song or not song.get('source'):
            await ctx.send("Não consegui obter as informações da música escolhida.")
            return

        self.musicQueue[gid].append([song, userChannel])

        # Envia confirmação
        confirm_embed = discord.Embed(
            title=f"Opção #{chosen_index+1} Adicionada!",
            description=f"[{song['title']}]({song['link']}) foi adicionada à fila.",
            colour=self.embedOrange
        )
        if song.get('thumbnail'):
            confirm_embed.set_thumbnail(url=song['thumbnail'])
        await ctx.send(embed=confirm_embed)

        # Se nada estiver tocando, inicia a reprodução
        if not self.is_playing[gid] and not self.is_paused[gid]:
            if len(self.musicQueue[gid]) == 1:
                self.queueIndex[gid] = 0
            elif self.queueIndex[gid] >= len(self.musicQueue[gid]) -1 :
                self.queueIndex[gid] = len(self.musicQueue[gid]) - 1
            await self.play_music(ctx)

    # Comando para pausar música
    @commands.command(name='pause', aliases=['pausar'], help='Pausa a música atual.')
    async def pause(self, ctx):
        gid = int(ctx.guild.id)
        if gid not in self.vc or not self.vc.get(gid) or not self.vc[gid].is_connected():
            await ctx.send("Não estou conectado a um canal de voz.")
            return
        if not self.is_playing[gid]:
            if self.is_paused[gid]:
                await ctx.send("A música já está pausada.")
            else:
                await ctx.send("Não há música tocando para pausar.")
            return

        self.vc[gid].pause()
        self.is_playing[gid] = False
        self.is_paused[gid] = True
        await ctx.send("⏸️ Pausado.")

    # Comando para retomar a música pausada
    @commands.command(name='resume', aliases=['despausar', 'continue'], help='Retoma a música pausada.')
    async def resume(self, ctx):
        gid = int(ctx.guild.id)
        if gid not in self.vc or not self.vc.get(gid) or not self.vc[gid].is_connected():
            await ctx.send("Não estou conectado a um canal de voz.")
            return
        if not self.is_paused[gid]:
            if self.is_playing[gid]:
                await ctx.send("A música já está tocando.")
            else:
                await ctx.send("Não há música pausada para retomar.")
            return

        self.vc[gid].resume()
        self.is_playing[gid] = True
        self.is_paused[gid] = False
        await ctx.send("▶️ Retomado!")

    # Comando para pular música
    @commands.command(name='skip', aliases=['pular', 's'], help='Pula a música atual.')
    async def skip(self, ctx):
        gid = int(ctx.guild.id)
        if gid not in self.vc or not self.vc.get(gid) or not self.vc[gid].is_connected():
            await ctx.send("Não estou tocando nada para pular.")
            return

        if self.is_playing[gid] or self.is_paused[gid]:
             await ctx.send("⏭️ Pulando música...")
             self.vc[gid].stop() # Isso acionará o (play_next) que tocará a próxima
             self.is_paused[gid] = False # Garante que não fique pausado
        else:
             await ctx.send("Não há música tocando ou pausada para pular.")

    @commands.command(name='lyrics', aliases=['letra', 'letras'], help='Busca a letra de uma música.')
    async def lyrics(self, ctx, *, query: str = None):
        gid = int(ctx.guild.id)
        if gid not in self.musicQueue: await self.initialize_guild_state(gid)

        # Verificação do Genius
        if not self.genius:
            await ctx.send("❌ A funcionalidade de letras não está disponível. O token da API do Genius não foi configurado corretamente.")
            return

        search_term = ""
        song_title = ""
        song_artist = "Artista Desconhecido"

        # Determinar o termo de busca
        if query is None:
            # Se não houver argumento, busca a música atual
            if (self.is_playing.get(gid, False) or self.is_paused.get(gid, False)) and 0 <= self.queueIndex.get(gid, -1) < len(self.musicQueue.get(gid, [])):
                current_song_info = self.musicQueue[gid][self.queueIndex[gid]]
                original_title = current_song_info[0].get('title', None)
                if not original_title:
                     await ctx.send("Não consegui obter o título da música atual.")
                     return
                # Limpa o título para melhor busca
                search_term = self.clean_song_title(original_title)
                song_title = original_title 
                # Ele vai tentar achar o artista e título da música caso não esteja claro
                if " - " in search_term:
                     parts = search_term.split(" - ", 1)
                     potential_artist = parts[0].strip()
                     potential_title = parts[1].strip()
                     # Se a primeira parte for mais curta, assume que é artista
                     if len(potential_artist.split()) <= 4: # Evita pegar frases longas
                         song_artist = potential_artist
                         search_term = f"{potential_title} {potential_artist}"
                     else:
                         song_artist = "Artista Desconhecido"
                         search_term = potential_title

                print(f"Buscando letra para música atual. Título original: '{original_title}', Termo de busca limpo: '{search_term}'")

            else:
                await ctx.send("Não há música tocando ou pausada. Use `!lyrics <nome da música>` para buscar.")
                return
        else:
            # Usa a query fornecida pelo usuário
            search_term = query
            song_title = query # Usa a query como título inicial para exibição
            print(f"Buscando letra para query: '{query}'")

        await ctx.send(f"🔎 Buscando letra para **'{search_term}'**...")

        try:
            # Busca no Genius
            # Usamos asyncio.to_thread para não bloquear o bot durante a busca na API
            song = await asyncio.to_thread(self.genius.search_song, search_term)

            if song is None:
                await ctx.send(f"😥 Desculpe, não encontrei a letra para '{search_term}'. Tente ser mais específico (ex: `!lyrics Nome da Musica Nome do Artista`).")
                return

            lyrics_text = song.lyrics
            # Atualiza título e artista com os dados encontrados pelo Genius
            song_title = song.title
            song_artist = song.artist

            # Envio da letra em pedaços (chunks) para evitar mensagens muito longas
            max_len = 1990
            chunks = [lyrics_text[i:i+max_len] for i in range(0, len(lyrics_text), max_len)]

            embed = discord.Embed(
                title=f"🎤 Letra de: {song_title}",
                description=f"**Artista:** {song_artist}\n\n{chunks[0]}", # Primeira parte na descrição
                color=self.embedPurple # Ou outra cor de sua escolha
            )
            if song.song_art_image_thumbnail_url:
                 embed.set_thumbnail(url=song.song_art_image_thumbnail_url)
            embed.set_footer(text=f"Letra encontrada via Genius | Página 1/{len(chunks)}")

            await ctx.send(embed=embed)

            # Envia o resto em mensagens separadas, se houver
            if len(chunks) > 1:
                for i, chunk in enumerate(chunks[1:], start=2):
                    # Espera um pouquinho para não ser taxado como spam pelo Discord
                    await asyncio.sleep(0.5)
                    await ctx.send(f"**{song_title} - Continuação (Página {i}/{len(chunks)}):**\n\n{chunk}")
            # --- Fim Envio ---

        except TimeoutError:
             await ctx.send("⏳ A busca pela letra demorou muito e foi cancelada. Tente novamente.")
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro inesperado ao buscar a letra: {e}")
            print(f"Erro detalhado no comando lyrics: {e}")


    # Comando para mostrar a música atual
    @commands.command(name='nowplaying', aliases=['np', 'tocando'], help='Mostra a música que está tocando agora.')
    async def nowplaying(self, ctx):
        gid = int(ctx.guild.id)
        if gid not in self.musicQueue: await self.initialize_guild_state(gid)

        if self.is_playing[gid] or self.is_paused[gid]:
            # Garante que o índice é válido
            if 0 <= self.queueIndex[gid] < len(self.musicQueue[gid]):
                current_song_info = self.musicQueue[gid][self.queueIndex[gid]]
                song = current_song_info[0]
                # Reutiliza o embed de 'now playing'
                embed = self.now_playing_embed(gid, song)
                if self.is_paused[gid]:
                    embed.title = "Música Pausada ⏸️"
                    embed.colour = self.embedYellow
                await ctx.send(embed=embed)
            else:
                # Caso estranho onde está tocando/pausado mas índice inválido
                await ctx.send("Estou em um estado inconsistente. Tentando corrigir...")
                print(f"Erro de estado em nowplaying: is_playing={self.is_playing[gid]}, is_paused={self.is_paused[gid]}, index={self.queueIndex[gid]}, queue_len={len(self.musicQueue[gid])}")
                # Tenta parar para forçar um reset no próximo comando
                if self.vc.get(gid) and self.vc[gid].is_connected():
                     self.vc[gid].stop()
                self.is_playing[gid] = self.is_paused[gid] = False
        else:
            await ctx.send("Não há nenhuma música tocando ou pausada no momento.")


    # Comando para mostrar a fila
    @commands.command(name='fila', aliases=['queue', 'q', 'list', 'lista'], help='Mostra a fila de músicas.')
    async def fila(self, ctx):
        gid = int(ctx.guild.id)
        if gid not in self.musicQueue: await self.initialize_guild_state(gid)

        if not self.musicQueue[gid]:
            await ctx.send("A fila está vazia.")
            return

        embed = discord.Embed(title="Fila de Músicas 🎶", colour=self.embedOrange)
        description = ""

        # Mostra a música atual se estiver tocando/pausada
        if (self.is_playing[gid] or self.is_paused[gid]) and 0 <= self.queueIndex[gid] < len(self.musicQueue[gid]):
             current_song = self.musicQueue[gid][self.queueIndex[gid]][0]
             status = "▶️ Tocando:" if self.is_playing[gid] else "⏸️ Pausada:"
             description += f"**{status}** [{current_song['title']}]({current_song['link']})\n\n**Próximas:**\n"
             start_index = self.queueIndex[gid] + 1
        else:
            # Mostra desde o início se nada estiver tocando
             description += "**Fila Vazia ou Música Atual Desconhecida**\n\n**Próximas:**\n"
             start_index = 0

        # Mostra as próximas músicas na fila
        if start_index < len(self.musicQueue[gid]):
            for i, (song_info) in enumerate(self.musicQueue[gid][start_index:], start=1):
                song = song_info[0]
                description += f"**{i}.** [{song['title']}]({song['link']})\n"
                if i >= 10: # Limita a 10 próximas músicas no embed
                    description += f"\n... e mais {len(self.musicQueue[gid]) - start_index - 10} música(s)."
                    break
        else:
             description += "*Nenhuma música na fila.*"

        embed.description = description
        await ctx.send(embed=embed)

    # Comando para limpar a fila
    @commands.command(name='clear', aliases=['cl', 'limpar'], help='Limpa toda a fila de músicas.')
    async def clear(self, ctx):
        gid = int(ctx.guild.id)
        if gid not in self.musicQueue: await self.initialize_guild_state(gid)

        if not self.musicQueue[gid]:
            await ctx.send("A fila já está vazia.")
            return

        self.musicQueue[gid] = []
        self.queueIndex[gid] = 0

        if self.vc.get(gid) and self.vc[gid].is_connected() and (self.is_playing[gid] or self.is_paused[gid]):
            await ctx.send("⏹️ Fila limpa e reprodução parada.")
            self.vc[gid].stop()
        else:
             await ctx.send("⏹️ Fila limpa.")
        
        self.loop_single[gid] = False
        self.loop_queue[gid] = False

        self.is_playing[gid] = False
        self.is_paused[gid] = False

    # Comando para o bot entrar no canal
    @commands.command(name='join', aliases=['entrar', 'j'], help='Faz o bot entrar no seu canal de voz.')
    async def join(self, ctx):
        try:
            channel = ctx.author.voice.channel
            if not channel:
                 await ctx.send("Você não está em um canal de voz!")
                 return
            if await self.join_VC(ctx, channel):
                 await ctx.send(f"Entrei em: **{channel.name}** 👋")
        except AttributeError:
             await ctx.send("Você não está em um canal de voz!")
        except Exception as e:
             await ctx.send(f"Ocorreu um erro ao tentar entrar no canal: {e}")
             print(f"Erro no comando join: {e}")

    @commands.command(name='leave', aliases=['sair', 'l', 'disconnect'], help='Faz o bot sair do canal de voz.')
    async def leave(self, ctx):
        gid = int(ctx.guild.id)
        if gid not in self.vc or not self.vc.get(gid) or not self.vc[gid].is_connected():
            await ctx.send("Não estou conectado a um canal de voz.")
            return

        # Limpa o estado antes de desconectar
        self.is_playing[gid] = self.is_paused[gid] = False
        if self.vc[gid].is_playing() or self.vc[gid].is_paused():
             self.vc[gid].stop()
        self.musicQueue[gid] = []
        self.queueIndex[gid] = 0

        self.loop_single[gid] = False
        self.loop_queue[gid] = False

        await self.vc[gid].disconnect()
        self.vc[gid] = None # Marca como desconectado
        await ctx.send("Até mais! 👋")

# Função para carregar o Cog
async def setup(bot):
    await bot.add_cog(MusicCog(bot))
    print("Music Cog carregado/recarregado.")