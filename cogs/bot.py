import discord
from discord.ext import commands, tasks
import os
import re
import yt_dlp
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()

class BotMedia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.folder_downloads = "./downloads"
        
        cd_media = os.getenv('COOLDOWN_MEDIA', '60')
        
        self.cooldown_value = float(cd_media)
        self.limit_filesize = int(os.getenv('LIMIT_FILESIZE_MB', '200'))
        self.disk_clear_min = int(os.getenv('DISK_CLEAR_MINUTES', '30'))
        self.shared_cooldown = commands.CooldownMapping.from_cooldown(1, self.cooldown_value, commands.BucketType.default)
        self.clearDisk.start()

    def cog_unload(self):
        self.clearDisk.cancel()

    @tasks.loop(minutes=30)
    async def clearDisk(self):
        bot_playing = any(vc.is_playing() for vc in self.bot.voice_clients)
        
        if not bot_playing and os.path.exists(self.folder_downloads):
            for file in os.listdir(self.folder_downloads):
                full_path = os.path.join(self.folder_downloads, file)
                try:
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                except Exception as e:
                    print(f"Error deleting {file}: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        content = message.content
        new_content = None
        
        if "instagram.com" in content:
            new_content = content.replace("instagram.com", "kkinstagram.com")
        elif "x.com" in content:
            new_content = content.replace("x.com", "fxtwitter.com")
        elif "twitter.com" in content:
            new_content = content.replace("twitter.com", "fxtwitter.com")

        if new_content:
            try:
                await message.delete()
                await message.channel.send(f"[{message.author.display_name}]({new_content})")
            except:
                pass

    async def shared_cooldown_check(self, ctx):
        bucket = self.shared_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.default)
        return True

    def verify_yt_filesize(self, url):
        ydl_opts = {'format': 'worst', 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                size = info.get('filesize') or info.get('filesize_approx')
                if size and (size / (1024 * 1024)) > self.limit_filesize:
                    return False
                return True
        except:
            return False

    def upload_litterbox(self, file_path):
        url = "https://litterbox.catbox.moe/resources/internals/api.php"
        data = {"reqtype": "fileupload", "time": "1h"}
        with open(file_path, 'rb') as f:
            response = requests.post(url, data=data, files={"fileToUpload": f})
            return response.text if response.status_code == 200 else None

    @commands.command()
    async def mp3(self, ctx, *, url):
        if not await self.shared_cooldown_check(ctx): return
        
        if not self.verify_yt_filesize(url):
            return await ctx.send(f"{ctx.author.mention} -> 💩🪠 (Arquivo muito grande)")

        os.makedirs(self.folder_downloads, exist_ok=True)
        path_output = os.path.join(self.folder_downloads, f'audio_{ctx.author.id}')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': path_output,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        final_path = f"{path_output}.mp3"
        link = self.upload_litterbox(final_path)
        await ctx.send(f"{ctx.author.mention} -> [Download Mp3]({link})")
        if os.path.exists(final_path): os.remove(final_path)

    @commands.command()
    async def stop(self, ctx):
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc: vc.stop()
        await ctx.message.add_reaction("⏹️")

async def setup(bot):
    await bot.add_cog(BotMedia(bot))