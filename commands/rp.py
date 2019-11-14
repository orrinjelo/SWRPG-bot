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
from pymongo import MongoClient
from datetime import datetime as dt
from pprint import pformat

logger = logging.getLogger('discord')

class Roleplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop, headers={"User-Agent": "AppuSelfBot"})
        self.mongo_client = MongoClient()
        self.rp_db = self.mongo_client['rp']
        self.xp = self.rp_db.xp
        self.characters = self.rp_db.characters

    async def log_post(self, message):
        player_id = hash(message.author)
        res = self.xp.find_one(
            {
                'id': player_id
            }
        )
        if not res:
            res = await self.create_xp(message=message)
        
        player_hist = res['history']
        player_xp = res['xp']
        now = dt.now()
        date = str(now.year*10000 + now.month*100 + now.day)
        if date in player_hist:
            player_hist[date] += 1
        else:
            player_hist[date] = 1
            player_xp += 1

        self.xp.update_one(
            {
                'id': player_id
            },
            {
                '$set': {
                    'history': player_hist,
                    'xp': player_xp
                }
            }
        )

    async def create_xp(self, ctx=None, message=None, member=None):
        if not message:
            message = ctx.message
        if not member:
            member = message.author
        player_id = hash(member)
        player_name = str(member)
        res = self.xp.find_one(
            {
                'name': player_name
            }
        )
        if res:
            channel = self.bot.get_channel(BOT_DEBUG_CHANNEL)
            await channel.send('Error: {}({}) already exists in database'.format(player_name, player_id))
            return res
        ret = {
            'id': player_id,
            'name': player_name,
            'xp': 0,
            'history': {}
        }
        self.xp.insert_one(ret)
        return ret


    async def report_characters_pid(self, ctx, player_id):
        char = self.characters.find_one(
            {
                'id': player_id
            }
        )
        # # Thanks to IgneelDxD for help on this
        # if str(user.avatar_url)[54:].startswith('a_'):
        #     avi = 'https://images.discordapp.net/avatars/' + str(user.avatar_url)[35:-10]
        # else:
        #     avi = user.avatar_url        
        if char:
            if embed_perms(ctx.message):
                em = discord.Embed(colour=0x708DD0)
                name = char['name'] if char['name'] else 'None'
                character = char['character']['name'] if char['character']['name'] else 'None'
                career = char['character']['career'] if char['character']['career'] else 'None'
                specializations = ', '.join(char['character']['specializations']) if char['character']['specializations'] else 'None'
                species = char['character']['species'] if char['character']['species'] else 'None'
                appearance = char['character']['appearance_brief'] if char['character']['appearance_brief'] else 'None'
                em.add_field(name='Player', value=name, inline=True)
                em.add_field(name='Character', value=character, inline=True)
                em.add_field(name='Characteristics', value=' '.join(['**{0}**:{1}'.format(s, char['character']['base_skills'][s]) for s in char['character']['base_skills']]), inline=True)
                em.add_field(name='Career', value=career, inline=True)
                em.add_field(name='Species', value=species, inline=True)
                em.add_field(name='Specializations', value=specializations, inline=True)
                em.add_field(name='Appearance', value=appearance, inline=True)
                try:
                    em.set_thumbnail(url=char['character']['thumbnail'])
                except:
                    pass
                await ctx.send(embed=em)
            else:
                msg = 'Unimplemented'
                await ctx.send(msg)        
        else:
            await ctx.send('Character not found.')

    async def get_player_by_ctx(self, ctx):
        player_id = hash(ctx.message.author)
        res = self.xp.find_one(
            {
                'id': player_id
            }
        )
        if not res:
            res = await self.create_xp(ctx=ctx)
        return res

    async def get_player_by_id(self, ctx, player_id):
        res = self.xp.find_one(
            {
                'id': hash(player_id)
            }
        )
        if not res:
            res = await self.create_xp(ctx=ctx)
        return res

    async def get_player_by_member(self, ctx, member):
        res = self.xp.find_one(
            {
                'id': hash(member)
            }
        )
        if not res:
            res = await self.create_xp(ctx=ctx, member=member)
        return res

    @commands.command(pass_context=True, aliases=['new_character'])
    async def newchar(self, ctx, name):
        await ctx.send('This feature remains to be implemented.')

    @commands.command(pass_context=True, aliases=['character'])
    async def char(self, ctx):
        message = ctx.message
        member = message.author
        player_id = hash(member)
        await self.report_characters_pid(ctx, player_id)

    @commands.command(pass_context=True, aliases=['listxpraw'])
    async def xplistraw(self, ctx):
        res = self.xp.find()
        for entry in res:
            await ctx.send(pformat(entry))

    @commands.command(pass_context=True, aliases=['listxp'])
    async def xplist(self, ctx):
        res = self.xp.find()
        for entry in res:
            user = ctx.guild.get_member_named(entry['name'])
            try:
                if user.nick:
                    username = user.nick
                else:
                    username = user.name
            except:
                username = user.name
            await ctx.send('{} has {} XP.'.format(username, entry['xp']))

    @commands.command(pass_context=True)
    @commands.has_role(ADMIN_ROLE)
    async def find_one(self, ctx, query: str):
        res = self.xp.find_one(
            eval(query)
        )
        await ctx.send(pformat(res))

    @commands.command(pass_context=True)
    @commands.has_role(ADMIN_ROLE)
    async def update_one(self, ctx, query: str, request: str):
        res = self.xp.update_one(
            eval(query),
            eval(request)
        )
        await ctx.send(pformat(res))

    @commands.has_role(GAMEMASTER_ROLE)
    @commands.command(pass_context=True)
    async def givexp(self, ctx, points: int, *, name: discord.Member=None):
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
        res = await self.get_player_by_member(ctx, user)
        self.xp.update_one(
            {
                'id': res['id']
            },
            {'$set': {
                'xp': res['xp'] + points
            }}
        )
        await ctx.send("{0}'s XP is increased by {1}.".format(res['name'], points))

    @commands.has_role(GAMEMASTER_ROLE)
    @commands.command(aliases=['set_xp'],pass_context=True)
    async def setxp(self, ctx, points: int, *, name: discord.Member=None):
        # await ctx.send("{},{}".format(points, name))
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
        res = await self.get_player_by_member(ctx, user)
        # await ctx.send("{},{},{},{}".format(user,hash(user),res,hash(ctx.message.author)))
        self.xp.update_one(
            {
                'id': res['id']
            },
            {'$set': {
                'xp': points
            }}
        )
        await ctx.send("{0}'s XP is set to {1}.".format(str(user), points))

    @commands.command(aliases=['experience'],pass_context=True)
    async def xp(self, ctx, name: discord.Member=None):
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
        res = await self.get_player_by_member(ctx,user)
        msg = await ctx.send('{} has {} xp.'.format(str(user), res['xp']))  

    @commands.command(aliases=['test'],pass_context=True)
    async def xptest(self, ctx):
        logger.debug('Calling XPtest')
        msg = await ctx.send('You have 10000000 xp.')  