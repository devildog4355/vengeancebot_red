from discord.ext import commands
from discord.ext import commands
from .utils.chat_formatting import box
from .utils.dataIO import dataIO
from .utils import checks
from random import choice
import asyncio
import json
import aiohttp
import os

class Imgflip:

    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "data/imgflip/settings.json"
        self.settings = dataIO.load_json(self.settings_file)
        self.url = "https://api.imgflip.com/caption_image?template_id={0}&username={1}&password={2}&text0={3}&text1={4}"
        self.search = "https://api.imgflip.com/get_memes?username={0}&password={1}"
        self.username = self.settings["IMGFLIP_USERNAME"]
        self.password = self.settings["IMGFLIP_PASSWORD"]

    async def get_meme_id(self, meme):
        url = self.search.format(self.username, self.password)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.search) as r:
                    results = await r.json()
                for memes in results["data"]["memes"]:
                    if meme.lower() in memes["name"].lower():
                        print(meme)
                        return memes["id"]
        except:
            await self.get_memes()

    @commands.command(pass_context=True, alias=["listmemes"])
    async def getmemes(self, ctx):
        url = self.search.format(self.username, self.password)
        prefix = self.get_prefix(ctx.message.server, ctx.message.content)
        memelist = "```{}meme or id;text1;text2\n\n".format(prefix)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.search) as r:
                results = await r.json()
            for memes in results["data"]["memes"]:
                memelist += memes["name"] + ", "
                if len(memelist) > 1500:
                    await self.bot.say(memelist + "```")
                    memelist = "```"
            await self.bot.say(memelist[:len(memelist)-2] + "``` Find a meme https://imgflip.com/memetemplates click blank template and get the Template ID for more!")

    @commands.command(pass_context=True)
    async def meme(self, ctx, *, memeText:str):
        """ Pulls a custom meme from imgflip"""
        msg = memeText.split(";")
        prefix = self.get_prefix(ctx.message.server, ctx.message.content)
        if len(msg) == 3:
            if len(msg[0]) > 1 and len([msg[1]]) < 20 and len([msg[2]]) < 20:
                username = self.settings["IMGFLIP_USERNAME"]
                password = self.settings["IMGFLIP_PASSWORD"]
                meme = msg[0]
                text1 = msg[1]
                text2 = msg[2]
                if not meme.isdigit():
                    meme = await self.get_meme_id(meme)
                url = self.url.format(meme, username, password, text1, text2)
                try:
                    async with aiohttp.get(url) as r:
                        result = await r.json()
                    if result["data"] != []:
                        url = result["data"]["url"]
                        await self.bot.say(url)
                except:
                    await self.bot.process_commands("getmemes")
            else:
                await self.bot.process_commands("getmemes")
        else:
            await self.bot.process_commands("getmemes")

    def get_prefix(self, server, msg):
        prefixes = self.bot.settings.get_prefixes(server)
        for p in prefixes:
            if msg.startswith(p):
                return p
        return None

    @commands.group(pass_context=True, name='imgflipset')
    @checks.admin_or_permissions(manage_server=True)
    async def _imgflipset(self, ctx):
        """Command for setting required access information for the API"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_imgflipset.command(pass_context=True, name='username')
    @checks.is_owner()
    async def set_username(self, ctx, cons_key):
        """Sets the consumer key"""
        message = ""
        if cons_key is not None:
            settings = self.settings
            settings["IMGFLIP_USERNAME"] = cons_key
            settings = dataIO.save_json(self.settings_file, self.settings)
            message = "Consumer key saved!"
        else:
            message = "No consumer key provided!"
        await self.bot.say('```{}```'.format(message))

    @_imgflipset.command(pass_context=True, name='password')
    @checks.is_owner()
    async def set_password(self, ctx, cons_secret):
        """Sets the consumer secret"""
        message = ""
        if cons_secret is not None:
            settings = self.settings
            settings["IMGFLIP_PASSWORD"] = cons_secret
            settings = dataIO.save_json(self.settings_file, self.settings)
            message = "Consumer secret saved!"
        else:
            message = "No consumer secret provided!"
        await self.bot.say('```{}```'.format(message))


def check_folder():
    if not os.path.exists("data/imgflip"):
        print("Creating data/imgflip folder")
        os.makedirs("data/imgflip")


def check_file():
    data = {'IMGFLIP_USERNAME': '', 'IMGFLIP_PASSWORD': ''}
    f = "data/imgflip/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Imgflip(bot))
