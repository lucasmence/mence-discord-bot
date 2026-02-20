import discord
from discord.ext import commands, tasks
import os
import re
import ffmpeg
from pytube import YouTube
import yt_dlp
import requests

FOLDER_DOWNLOADS = "./downloads"
token = os.getenv('DISCORD_TOKEN')
prefix = os.getenv('PREFIX')  
userId = os.getenv('USER_ID')
cooldownMediaCommand = os.getenv('COOLDOWN_MEDIA')  

shared_cooldown = commands.CooldownMapping.from_cooldown(1, cooldownMediaCommand, commands.BucketType.default)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

@tasks.loop(minutes=5.0)
async def clearDisk():
    botPlaying = False
    for vc in bot.voice_clients:
        if vc.is_playing():
            botPlaying = True
            break
    
    if not botPlaying:
        if os.path.exists(FOLDER_DOWNLOADS):
            files = os.listdir(FOLDER_DOWNLOADS)
            if files:
                for file in files:
                    fullPath = os.path.join(FOLDER_DOWNLOADS, file)
                    try:
                        if os.path.isfile(fullPath):
                            os.remove(fullPath)
                    except Exception as e:
                        print(f"Error {file}: {e}")

@bot.event
async def on_ready():
    print(f'Success: {bot.user}')
    if not clearDisk.is_running():
        clearDisk.start()

@bot.check
async def verify_present_user(ctx):
    discordUser = ctx.guild.get_member(userId)  
    if discordUser is None:
        return False  
    
    return True

async def shared_cooldown_check(ctx):
    try:
        await ctx.message.delete()
    except:
        pass 

    bucket = shared_cooldown.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()
    if retry_after:
        raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.default)
    return True

def deleteFile(path):
    if os.path.isfile(path):
        os.remove(path)

def verifyYoutubeFilesize(url, limitMb=200):
    ydl_opts = {
        'format': 'worst',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            bytesSize = info.get('filesize') or info.get('filesize_approx')

            if bytesSize:
                mbSize = bytesSize / (1024 * 1024)
                if mbSize > limitMb:
                    return False
                return True
            
            return False

    except Exception as e:
        return False

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        time = round(error.retry_after)
        await ctx.send(f"{ctx.author.mention} ⏳ {time}s")
    else:
        print(f"Error: {error}")

def litterbox_upload(filePath):
    url = "https://litterbox.catbox.moe/resources/internals/api.php"
    
    dados = {
        "reqtype": "fileupload",
        "time": "1h"
    }

    try:
        with open(filePath, 'rb') as f:
            filesList = {"fileToUpload": f}
            response = requests.post(url, data=dados, files=filesList)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"Upload error: {response.status_code}")
                return None
                
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"Upload error: {e}")

@bot.command()
@commands.check(shared_cooldown_check)
async def mp3(ctx, *, message):
    try:
        await ctx.message.delete()
    except:
        pass 

    fileSizeBlock = verifyYoutubeFilesize(message)
    if not fileSizeBlock:
        await ctx.channel.send(f"{ctx.author.mention} -> 💩🪠")
        return

    folderOutput = "downloads"
    os.makedirs(folderOutput, exist_ok=True)
    
    pathOutput = os.path.join(folderOutput, 'audiomp3')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': pathOutput, 
        'quiet': True,
        'no_warnings': True,
        'source_address': '0.0.0.0', 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message])
    except Exception as e:
        print(f"Download error: {e}")
        return None

    audioPath = "downloads/audiomp3.mp3"
    downloadUrl = litterbox_upload(audioPath)
    content = f"{ctx.author.mention} -> [Download Mp3]({downloadUrl})"
    deleteFile(audioPath)
    await ctx.channel.send(content)
    

@bot.command()
@commands.check(shared_cooldown_check)
async def mp4(ctx, *, message):
    try:
        await ctx.message.delete()
    except:
        pass 

    fileSizeBlock = verifyYoutubeFilesize(message)
    if not fileSizeBlock:
        await ctx.channel.send(f"{ctx.author.mention} -> 💩🪠")
        return

    folderOutput = "downloads"
    os.makedirs(folderOutput, exist_ok=True)
    
    pathOutput = os.path.join(folderOutput, 'video.mp4')

    ydl_opts = {
        'format': 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst',
        'outtmpl': pathOutput, 
        'quiet': True,
        'no_warnings': True,
        'source_address': '0.0.0.0', 
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message])
    except Exception as e:
        print(f"Download error: {e}")
        return None

    videoPath = "downloads/video.mp4"
    downloadUrl = litterbox_upload(videoPath)
    content = f"{ctx.author.mention} -> [Download Mp4]({downloadUrl})"
    deleteFile(videoPath)
    await ctx.channel.send(content)

@bot.command()
@commands.check(shared_cooldown_check)
async def play(ctx, *, message):
    try:
        await ctx.message.delete()
    except:
        pass 

    fileSizeBlock = verifyYoutubeFilesize(message)
    if not fileSizeBlock:
        await ctx.channel.send(f"{ctx.author.mention} -> 💩🪠")
        return

    folderOutput = "downloads"
    os.makedirs(folderOutput, exist_ok=True)
    
    pathOutput = os.path.join(folderOutput, 'audio')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': pathOutput, 
        'quiet': True,
        'no_warnings': True,
        'source_address': '0.0.0.0', 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message])
    except Exception as e:
        print(f"Download error: {e}")
        return None

    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    if not voice_client:
        if ctx.author.voice:
            voice_client = await ctx.author.voice.channel.connect()
        else:
            return

    if not voice_client.is_playing():
        audioPath = "downloads/audio.mp3"
        audio_source = discord.FFmpegPCMAudio(audioPath)
        voice_client.play(audio_source, after=lambda e: ctx.send(":+1:"))

@bot.command()
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
    try:
        await ctx.message.delete()
    except:
        pass 

@bot.command()
async def exit(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client:
        await voice_client.disconnect()
    try:
        await ctx.message.delete()
    except:
        pass 

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith(prefix):
        await bot.process_commands(message)
        return

    instagramRegex = r"(https?://(?:www\.)?instagram\.com/(?:p|reels|reel)/([^/?#&]+))"
    match = re.search(instagramRegex, message.content)

    if match:
        linkDefault = match.group(1)
        linkNew = linkDefault.replace("instagram.com", "kkinstagram.com")
           
        try:
            await message.delete()
        except:
            return

        content = f"[{message.author.display_name}]({linkNew})"
        await message.channel.send(content)

    twitterRegex = r"(https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+/status/[0-9]+)"
    match = re.search(twitterRegex, message.content)

    if match:
        linkDefault = match.group(1)
        linkNew = linkDefault.replace("x.com", "fxtwitter.com")
            
        try:
            await message.delete()
        except:
            return

        content = f"[{message.author.display_name}]({linkNew})"  
        await message.channel.send(content)

    await bot.process_commands(message)

if token:
    bot.run(token)
else:
    print("Error: DISCORD_TOKEN not found!")
