# 🤖 Bot Multifuncional para Discord

Um bot de Discord desenvolvido em Python usando `discord.py`. Este bot possui diversas funcionalidades, incluindo um sistema de música completo, economia conectada a um banco de dados, geração de imagens de boas-vindas e integração com o Reddit para busca de memes e imagens.

## ✨ Funcionalidades

*   🎵 **Música Avançada:** Reproduz áudio do YouTube (usando `yt-dlp`), pesquisa interativa com botões drop-down, controle de fila, loop (música/fila) e busca de letras via Genius API.
*   💰 **Economia (RPG):** Sistema de saldo com banco de dados SQLite assíncrono (`SQLAlchemy` + `aiosqlite`). Inclui comandos para ver saldo, fazer transferências (PIX) e explorar para ganhar moedas.
*   🖼️ **Boas-Vindas Personalizadas:** Gera um banner de boas-vindas com a foto de perfil do usuário sempre que alguém entra no servidor, renderizado em uma thread separada para não travar o bot.
*   📱 **Integração com Reddit:** Puxa postagens quentes (hot) de subreddits específicos como memes, gatos, shitpost, etc.
*   ⚙️ **Status Rotativo:** O bot altera automaticamente seu status de atividade a cada 60 segundos.

---

## 🛠️ Pré-requisitos

Antes de iniciar, você precisará ter instalado em sua máquina:

1. **[Python 3.8+](https://www.python.org/downloads/)**
2. **[FFmpeg](https://ffmpeg.org/download.html)** (Essencial para o sistema de música funcionar. Certifique-se de adicioná-lo ao `PATH` do sistema do seu computador).

---

## 📦 Instalação e Configuração

### 1. Estrutura de Pastas
Certifique-se de que a estrutura do seu projeto esteja assim:

```text
meu-bot/
├── main.py
├── db_economia_code.py
├── .env
├── cogs/
│   ├── economia.py
│   ├── meberjoin.py
│   ├── music.py
│   ├── ping.py
│   ├── reddit.py
│   └── welcome_images/  <-- (Coloque imagens .jpg ou .png de fundo aqui!)
```

### 2. Instalando Dependências
Crie um arquivo chamado `requirements.txt` com o seguinte conteúdo e instale-o:

```txt
discord.py==2.3.2
python-dotenv
yt-dlp
PyNaCl
lyricsgenius
easy-pil
asyncpraw
SQLAlchemy
aiosqlite
```
Execute no terminal:
```bash
pip install -r requirements.txt
```

### 3. Configurando Variáveis de Ambiente (`.env`)
Crie um arquivo chamado `.env` na raiz do projeto e preencha com suas credenciais:

```env
# Token do seu bot do Discord (Pegue no Discord Developer Portal)
DISCORD_TOKEN=seu_token_do_discord_aqui

# Token da API do Genius (Para letras de músicas - crie conta em genius.com/api-clients)
GENIUS_TOKEN=seu_token_do_genius_aqui

# Credenciais do Reddit (Para memes - crie um app em reddit.com/prefs/apps)
REDDIT_CLIENT_ID=seu_client_id_do_reddit
REDDIT_CLIENT_SECRET=seu_client_secret_do_reddit
```

### 4. Imagens de Boas-Vindas
Para o sistema de boas-vindas funcionar sem erros, você **precisa** adicionar pelo menos uma imagem (ex: `fundo.png`) dentro da pasta `cogs/welcome_images/`. O bot escolherá uma imagem aleatória desta pasta para gerar o banner.

---

## 📜 Lista de Comandos

O prefixo padrão do bot é `!`.

### 🎵 Música
*   `!play <nome ou link>` - Toca uma música ou retoma a reprodução.
*   `!search <nome>` - Pesquisa uma música e permite escolher entre 10 opções usando um menu interativo.
*   `!pause` / `!resume` - Pausa ou despausa a música.
*   `!skip` - Pula para a próxima música da fila.
*   `!fila` - Mostra as próximas músicas.
*   `!nowplaying` - Mostra a música atual.
*   `!loop <single/queue/off>` - Alterna o modo de repetição.
*   `!add <nome ou link>` - Adiciona à fila sem forçar a reprodução.
*   `!remove` - Remove a última música adicionada à fila.
*   `!lyrics [nome da musica]` - Busca a letra da música atual ou de uma música específica.
*   `!clear` - Limpa a fila e para a reprodução.
*   `!join` / `!leave` - Faz o bot entrar ou sair do canal de voz.

### 💰 Economia
*   `!saldo` - Mostra seu saldo atual de moedas.
*   `!pix @usuario <valor>` - Transfere moedas para outro usuário.
*   `!explorar` - Trabalha/explora para ganhar moedas (possui tempo de recarga de 10 segundos).

### 📱 Reddit
*   `!meme` - Envia um meme aleatório do `r/memes`.
*   `!shitpost` - Envia uma imagem do `r/shitposting`.
*   `!gatos` - Envia a foto de um gato do `r/cats`.
*   `!pikachusurpreso` - Envia um meme do `r/SurprisedPikachu`.
*   `!craft` - Envia stickers/crafts de CS2 do `r/cs2_stickercrafts`.

### 🛠️ Utilidades e Moderação
*   `!ping` - Mostra a latência do bot em milissegundos.
*   `!ola` ou `/ola` - Comando básico de saudação.
*   `!sync` - *(Apenas Dono)* Sincroniza os comandos de barra (`/`) (Slash Commands) com os servidores do Discord.

---

## 🚀 Como Iniciar o Bot

Com as dependências instaladas e o arquivo `.env` configurado, basta rodar o arquivo principal:

```bash
python main.py
```
Se tudo estiver correto, você verá a mensagem no terminal:
`Bot está online como NomeDoSeuBot#1234!`

---

## ⚠️ Possíveis Erros e Soluções

1. **"Erro ao conectar no canal de voz" / Bot entra e não toca nada:**
   * Verifique se o **FFmpeg** está instalado corretamente e adicionado às variáveis de ambiente do Windows/Linux. Sem ele, o `discord.py` não consegue reproduzir áudio.
2. **"Módulo de Economia não cria saldo":**
   * O arquivo `dados_economia.db` será criado automaticamente na primeira vez que o bot rodar e o módulo for carregado.
3. **Comandos `/` (Slash) não aparecem:**
   * Certifique-se de rodar o comando `!sync` no chat do servidor logado como dono do bot.
4. **"Erro de intents" ao ligar o bot:**
   * Vá no [Discord Developer Portal](https://discord.com/developers/applications), entre no seu bot, vá na aba "Bot" e ative todas as três chaves em **Privileged Gateway Intents** (Presence, Server Members, e Message Content).
