import discord
import asyncio
import random
from discord.ext import commands
from discord.utils import get
from config.secrets import *
from utils.checks import *
from pymongo import MongoClient
import logging
from pprint import pformat


logger = logging.getLogger('discord')

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.debug('Connecting to Mongo...')
        self.mongo_client = MongoClient()
        self.rp_db = self.mongo_client['rp']
        self.xp = self.rp_db.xp
        self.commands_db = self.mongo_client['commands']
        self.com = self.commands_db.com        

    @commands.command(pass_context=True)
    @commands.has_role(ADMIN_ROLE)
    async def eval(self, ctx, query: str):
        try:
            res = await eval(query)
        except:
            res = eval(query)
        try:
            await ctx.send(pformat(res))
        except:
            try:
                await ctx.send(str(pformat(res))[:2000])
            except:
                await ctx.send(str(res)[:2000])


    @commands.command(aliases=["mute", "silence", "doom"])
    @commands.has_role(MOD_ROLE)
    async def hellfire(self, ctx, member: discord.Member):
        if member.id == 189761449013280768:
            await ctx.send("No.")
            return

        role = get(member.guild.roles, name='Eljudne')

        print(role)

        await member.add_roles(role)

    @commands.command(pass_context=True, aliases=['reboot', 'reload'])
    @commands.has_role(ADMIN_ROLE)
    async def restart(self, ctx):
        """Restarts the bot."""
        latest = update_bot(True)
        if latest:
            g = git.cmd.Git(working_dir=os.getcwd())
            g.execute(["git", "pull", "origin", "master"])
            try:
                await ctx.send(content=None, embed=latest)
            except:
                pass
            with open('quit.txt', 'w', encoding="utf8") as q:
                q.write('update')
            print('Downloading update and restarting...')
            await ctx.send('Downloading update and restarting (check your console to see the progress)...')

        else:
            print('Restarting...')
            with open('restart.txt', 'w', encoding="utf8") as re:
                re.write(str(ctx.message.channel.id))
            await ctx.send('Restarting...')

        # if self.bot.subpro:
        #     self.bot.subpro.kill()
        os._exit(0)

    @commands.command(pass_context=True, aliases=['updawg'])
    @commands.has_role(ADMIN_ROLE)
    async def update(self, ctx):
        '''Update the bot code.'''
        latest = update_bot(True)
        if latest:
            g = git.cmd.Git(working_dir=os.getcwd())
            g.execute(["git", "pull", "origin", "master"])
            try:
                await ctx.send(content=None, embed=latest)
            except:
                pass
            await ctx.send('Downloading update...')
        else:
            await ctx.send('No updates available.')

    @commands.command(pass_context=True)
    @commands.has_role(MOD_ROLE)
    async def kick(self, ctx, name: discord.Member, *, reason=""):
        """Kicks a user (if you have the permission)."""
        user = get_user(ctx.message, user)
        if user:
            try:
                await user.kick(reason=reason)
                return_msg = "Kicked user `{}`".format(user.mention)
                if reason:
                    return_msg += " for reason `{}`".format(reason)
                return_msg += "."
                await ctx.message.edit(content=return_msg)
            except discord.Forbidden:
                await ctx.message.edit(content='Could not kick user. Not enough permissions.')
        else:
            return await ctx.message.edit(content='Could not find user.')

    @commands.command(pass_context=True, aliases=['talk'])
    @commands.has_role(ADMIN_ROLE)
    async def say(self, ctx, *message):
        await ctx.send(' '.join(message))

    @commands.command(pass_context=True, aliases=['tag','new_command', 'map'])
    @commands.has_role(MOD_ROLE)
    async def add_command(self, ctx, command: str, *, new_command=''):
        res = self.com.find_one(
            {
                "tag": command
            }
        )
        if not res:
            self.com.insert_one(
                {
                    'tag': command,
                    'replacement': new_command
                }
            )
        else:
            self.com.update_one(
                {
                    "tag": command
                },
                {
                    '$set': {
                        'replacement': new_command
                    }
                }
            )
        await ctx.message.add_reaction("👍")