import json
import time
import git
import discord
import os
import aiohttp
# from cogs.utils.dataIO import dataIO
from urllib.parse import quote as uriquote

# try:
#     from lxml import etree
# except ImportError:
#     from bs4 import BeautifulSoup
# from urllib.parse import parse_qs, quote_plus
#from cogs.utils import common


# @common.deprecation_warn()
def load_config():
    with open('config/config.json', 'r') as f:
        return json.load(f)


# # @common.deprecation_warn()
# def load_optional_config():
#     with open('settings/optional_config.json', 'r') as f:
#         return json.load(f)


# # @common.deprecation_warn()
# def load_moderation():
#     with open('settings/moderation.json', 'r') as f:
#         return json.load(f)


# # @common.deprecation_warn()
# def load_notify_config():
#     with open('settings/notify.json', 'r') as f:
#         return json.load(f)  
    

# # @common.deprecation_warn()
# def load_log_config():
#     with open('settings/log.json', 'r') as f:
#         return json.load(f)


# def has_passed(oldtime):
#     if time.time() - 20.0 < oldtime:
#         return False
#     return time.time()


# def set_status(bot):
#     if bot.default_status == 'idle':
#         return discord.Status.idle
#     elif bot.default_status == 'dnd':
#         return discord.Status.dnd
#     else:
#         return discord.Status.invisible


# def user_post(key_users, user):
#     if time.time() - float(key_users[user][0]) < float(key_users[user][1]):
#         return False, [time.time(), key_users[user][1]]
#     else:
#         log = dataIO.load_json("settings/log.json")
#         now = time.time()
#         log["keyusers"][user] = [now, key_users[user][1]]
#         dataIO.save_json("settings/log.json", log)
#         return True, [now, key_users[user][1]]


# def gc_clear(gc_time):
#     if time.time() - 3600.0 < gc_time:
#         return False
#     return time.time()


# def game_time_check(oldtime, interval):
#     if time.time() - float(interval) < oldtime:
#         return False
#     return time.time()


# def avatar_time_check(oldtime, interval):
#     if time.time() - float(interval) < oldtime:
#         return False
#     return time.time()


def update_bot(message):
    g = git.cmd.Git(working_dir=os.getcwd())
    g.execute(["git", "fetch", "origin", "master"])
    update = g.execute(["git", "remote", "show", "origin"])
    if ('up to date' in update or 'fast-forward' in update) and message:
        print('{}'.format(update))
        return False
    else:
        if message is False:
            version = 4
        else:
            version = g.execute(["git", "rev-list", "--right-only", "--count", "master...origin/master"])
        version = description = str(int(version) + 1)
        if int(version) > 4:
            version = "4"
        commits = g.execute(["git", "rev-list", "--max-count=%s" % version, "origin/master"])
        commits = commits.split('\n')
        em = discord.Embed(color=0x24292E, title='Latest changes for Charlie:', description='%s release(s) behind.' % description)
        for i in range(int(version)-1):
            title = g.execute(["git", "log", "--format=%ar", "-n", "1", "%s" % commits[i]])
            field = g.execute(["git", "log", "--pretty=oneline", "--abbrev-commit", "--shortstat", "%s" % commits[i], "^%s" % commits[i+1]])
            field = field[8:].strip()
            link = 'https://github.com/appu1232/Discord-Selfbot/commit/%s' % commits[i]
            em.add_field(name=title, value='%s\n[Code changes](%s)' % (field, link), inline=False)
        # em.set_thumbnail(url='https://image.flaticon.com/icons/png/512/25/25231.png')
        # em.set_footer(text='Full project: https://github.com/appu1232/Discord-Selfbot')
        return em


def cmd_prefix_len():
    config = load_config()
    return len(config['cmd_prefix'])


def embed_perms(message):
    try:
        check = message.author.permissions_in(message.channel).embed_links
    except:
        check = True

    return check


# def get_user(message, user):
#     try:
#         member = message.mentions[0]
#     except:
#         member = message.guild.get_member_named(user)
#     if not member:
#         try:
#             member = message.guild.get_member(int(user))
#         except ValueError:
#             pass
#     if not member:
#         return None
#     return member


# def find_channel(channel_list, text):
#     if text.isdigit():
#         found_channel = discord.utils.get(channel_list, id=int(text))
#     elif text.startswith("<#") and text.endswith(">"):
#         found_channel = discord.utils.get(channel_list,
#                                           id=text.replace("<", "").replace(">", "").replace("#", ""))
#     else:
#         found_channel = discord.utils.get(channel_list, name=text)
#     return found_channel


# async def get_google_entries(query):
#     url = 'https://www.google.com/search?q={}'.format(uriquote(query))
#     params = {
#         'safe': 'off',
#         'lr': 'lang_en',
#         'h1': 'en'
#     }
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'
#     }
#     entries = []
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url, params=params, headers=headers) as resp:
#             if resp.status != 200:
#                 config = load_optional_config()
#                 async with session.get("https://www.googleapis.com/customsearch/v1?q=" + quote_plus(query) + "&start=" + '1' + "&key=" + config['google_api_key'] + "&cx=" + config['custom_search_engine']) as resp:
#                     result = json.loads(await resp.text())
#                 return None, result['items'][0]['link']

#             try:
#                 root = etree.fromstring(await resp.text(), etree.HTMLParser())
#                 search_nodes = root.findall(".//div[@class='g']")
#                 for node in search_nodes:
#                     url_node = node.find('.//h3/a')
#                     if url_node is None:
#                         continue
#                     url = url_node.attrib['href']
#                     if not url.startswith('/url?'):
#                         continue
#                     url = parse_qs(url[5:])['q'][0]
#                     entries.append(url)
#             except NameError:
#                 root = BeautifulSoup(await resp.text(), 'html.parser')
#                 for result in root.find_all("div", class_='g'):
#                     url_node = result.find('h3')
#                     if url_node:
#                         for link in url_node.find_all('a', href=True):
#                             url = link['href']
#                             if not url.startswith('/url?'):
#                                 continue
#                             url = parse_qs(url[5:])['q'][0]
#                             entries.append(url)
#     return entries, root


# def attach_perms(message):
#     return message.author.permissions_in(message.channel).attach_files


# def parse_prefix(bot, text):
#     prefix = bot.cmd_prefix
#     if type(prefix) is list:
#         prefix = prefix[0]
#     return text.replace("[c]", prefix).replace("[b]", bot.bot_prefix)
