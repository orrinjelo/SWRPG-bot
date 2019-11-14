import discord
import asyncio
import random
import aiohttp
import re
from discord.ext import commands
from config.secrets import *
from utils.checks import embed_perms, cmd_prefix_len
import logging
from urllib import parse
from urllib.request import Request, urlopen

logger = logging.getLogger('discord')

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop, headers={"User-Agent": "AppuSelfBot"})


    def coinflip(self):
        return random.randint(0, 1)

    @commands.command()
    async def flipcoin(self, ctx):
        '''Flip a coin, get a result.'''
        if self.coinflip() == 0:
            await ctx.send("Heads")
        else:
            await ctx.send("Tails")


    @commands.command(aliases=['user', 'uinfo', 'info', 'ui'])
    async def userinfo(self, ctx, *, name=""):
        """Get user info. Ex: !info @Jeloman"""
        if ctx.invoked_subcommand is None:
            pre = cmd_prefix_len()
            if name:
                try:
                    user = ctx.message.mentions[0]
                except:
                    user = ctx.guild.get_member_named(name)
                if not user:
                    user = ctx.guild.get_member(int(name))
                if not user:
                    await ctx.send('Could not find user.')
                    return
            else:
                user = ctx.message.author

            # Thanks to IgneelDxD for help on this
            if str(user.avatar_url)[54:].startswith('a_'):
                avi = 'https://images.discordapp.net/avatars/' + str(user.avatar_url)[35:-10]
            else:
                avi = user.avatar_url

            role = user.top_role.name
            if role == "@everyone":
                role = "N/A"
            voice_state = None if not user.voice else user.voice.channel
            if embed_perms(ctx.message):
                em = discord.Embed(timestamp=ctx.message.created_at, colour=0x708DD0)
                em.add_field(name='User ID', value=user.id, inline=True)
                em.add_field(name='Nick', value=user.nick, inline=True)
                em.add_field(name='Status', value=user.status, inline=True)
                em.add_field(name='In Voice', value=voice_state, inline=True)
                em.add_field(name='Game', value=user.activity, inline=True)
                em.add_field(name='Highest Role', value=role, inline=True)
                em.add_field(name='Account Created', value=user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
                em.add_field(name='Join Date', value=user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
                em.set_thumbnail(url=avi)
                em.set_author(name=user, icon_url='https://i.imgur.com/RHagTDg.png')
                await ctx.send(embed=em)
            else:
                msg = '**User Info:** ```User ID: %s\nNick: %s\nStatus: %s\nIn Voice: %s\nGame: %s\nHighest Role: %s\nAccount Created: %s\nJoin Date: %s\nAvatar url:%s```' % (user.id, user.nick, user.status, voice_state, user.activity, role, user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), avi)
                await ctx.send(msg)

            await ctx.message.delete()

    @commands.command()
    async def avi(self, ctx, txt: str = None):
        """View bigger version of user's avatar. Ex: !avi @Jeloman"""
        if txt:
            try:
                user = ctx.message.mentions[0]
            except:
                user = ctx.guild.get_member_named(txt)
            if not user:
                user = ctx.guild.get_member(int(txt))
            if not user:
                await ctx.send('Could not find user.')
                return
        else:
            user = ctx.message.author

        # Thanks to IgneelDxD for help on this
        if str(user.avatar_url)[54:].startswith('a_'):
            avi = 'https://images.discordapp.net/avatars/' + str(user.avatar_url)[35:-10]
        else:
            avi = user.avatar_url
        if embed_perms(ctx.message):
            em = discord.Embed(colour=0x708DD0)
            em.set_image(url=avi)
            await ctx.send(embed=em)
        else:
            await ctx.send(avi)
        await ctx.message.delete()            


    @commands.command(aliases=['sd'],pass_context=True)
    async def selfdestruct(self, ctx, amount, *message):
        """Builds a self-destructing message. Ex: !sd 5 'secret message'"""
        await ctx.message.delete()
        killmsg = await ctx.send('{}'.format(' '.join(message)))
        timer = int(amount.strip())
        # Animated countdown because screw rate limit amirite
        destroy = await ctx.send(content='The above message will self-destruct in:')
        msg = await ctx.send('``%s  |``' % timer)
        for i in range(0, timer, 4):
            if timer - 1 - i == 0:
                await destroy.delete()
                await msg.edit(content='``0``')
                break
            else:
                await msg.edit(content='``%s  |``' % int(timer - 1 - i))
                await asyncio.sleep(1)
            if timer - 1 - i != 0:
                if timer - 2 - i == 0:
                    await destroy.delete()
                    await msg.edit(content='``0``')
                    break
                else:
                    await msg.edit(content='``%s  /``' % int(timer - 2 - i))
                    await asyncio.sleep(1)
            if timer - 2 - i != 0:
                if timer - 3 - i == 0:
                    await destroy.delete()
                    await msg.edit(content='``0``')
                    break
                else:
                    await msg.edit(content='``%s  -``' % int(timer - 3 - i))
                    await asyncio.sleep(1)
            if timer - 3 - i != 0:
                if timer - 4 - i == 0:
                    await destroy.delete()
                    await msg.edit(content='``0``')
                    break
                else:
                    await msg.edit(content='``%s  \ ``' % int(timer - 4 - i))
                    await asyncio.sleep(1)
        await msg.edit(content=':bomb:')
        await asyncio.sleep(.5)
        await msg.edit(content=':fire:')
        await killmsg.edit(content=':fire:')
        await asyncio.sleep(.5)
        await msg.delete()
        await killmsg.delete()
        

    @commands.command(aliases=['yt', 'vid', 'video'])
    async def youtube(self, ctx, *msg):
        """Search for videos on YouTube."""
        logger.debug(msg)
        search = parse.quote(' '.join(msg))
        youtube_regex = re.compile('\/watch\?v=[\d\w\-]*')
        async with self.session.get("https://www.youtube.com/results", params={"search_query": search}) as resp:
            response = await resp.text()
        await ctx.message.delete()
        url = youtube_regex.findall(response)[0]
        await ctx.send("https://www.youtube.com{}".format(url))        

    @commands.command()
    async def hello(self, ctx):
        """Adds two numbers together."""
        await ctx.send("Hello!")


    # @commands.command()
    # async def foobar(self, ctx, a, b):
    #     """Adds two numbers together."""
    #     await ctx.send("A: {}".format(a))
    #     await ctx.send("B: {}".format(b))


    # @commands.command()
    # async def fooby(self, ctx, a, *, b='none'):
    #     """Adds two numbers together."""
    #     await ctx.send("A: {}".format(a))
    #     await ctx.send("B: {}".format(b))


    # @commands.command()
    # async def fooboo(self, ctx, *, a='x', b='y'):
    #     """Adds two numbers together."""
    #     await ctx.send("A: {}".format(a))
    #     await ctx.send("B: {}".format(b))


    # @commands.command()
    # async def farboo(self, ctx, *, a: int=0, b: str ='y'):
    #     """Adds two numbers together."""
    #     await ctx.send("A: {}".format(a))
    #     await ctx.send("B: {}".format(b))

