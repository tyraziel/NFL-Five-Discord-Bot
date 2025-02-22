import discord

from discord.ext import commands
from discord import Color

from dotenv import dotenv_values

from PIL import Image
import io

import argparse
import requests
import urllib.parse
import json
import time
import random

import re
import sqlite3

import logging

import nflfive as nfl5

from bot_cache import BotCache

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)-16s] [%(levelname)-8s] %(module)s.%(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', handlers=[logging.StreamHandler(), logging.FileHandler("./bot-log.log")])
logger = logging.getLogger()

version = 'v1.0.0-beta'

cliParser = argparse.ArgumentParser(prog='nflfive_bot', description='NFL Five Card Fetcher Bot', epilog='', add_help=False)
cliParser.add_argument('-e', '--env', choices=['DEV', 'PROD'], default='DEV', action='store')
cliParser.add_argument('-l', '--loadcache', default=False, action='store_true')
cliParser.add_argument('-d', '--debug', default=False, action='store_true')
cliParser.add_argument('-t', '--test', default=False, action='store_true')
cliArgs = cliParser.parse_args()

if cliArgs.debug:
    logger.setLevel(logging.DEBUG)
    dmlogger.setLevel(logging.DEBUG)
    scCacheLogger.setLevel(logging.DEBUG)
    logger.debug("DEBUG TURNED ON")
    
dev_env = dotenv_values(".devenv")
prod_env = dotenv_values(".prodenv")

bot_env = dev_env
if('PROD' == cliArgs.env.upper()):
    bot_env = prod_env
    logger.info(f'THIS IS RUNNING IN PRODUCTION MODE AND WILL CONNECT TO PRODUCTION BOT TO THE MAIN NFL FIVE DISCORD SERVER')
else:
    logger.info(f'This is running DEVELOPMENT MODE and the DEVELOPMENT bot will connect to your test server')

intents = discord.Intents.default()
intents.message_content = True

botCache = BotCache()

bot = commands.Bot(command_prefix=['^'], intents=intents) #command_prefix can be one item - i.e. '!' or a list - i.e. ['!','#','$']

card_fetch_pattern = re.compile("\[\[(\w[\w'\- ]*\$?)\]\]", re.IGNORECASE | re.MULTILINE)
card_fetch_pattern_2 = re.compile("!(\w[\w'\- ]*\$?)!", re.IGNORECASE | re.MULTILINE)

card_set_number_pattern = re.compile(r"^([a-zA-Z]{1,2}\d+)-([A-Z\d]+)\$?$")

db_con = None
db_cur = None

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="NFL Five Lo-Fi"))
    logger.info(f'We have logged in as {bot.user} with status {bot.status}')

    startTime = time.time()
    logger.info(f'Loading Database.....')    
    global db_con
    db_con = sqlite3.connect("nfl-five.db")
    global db_cur 
    db_cur = db_con.cursor()
    endTime = time.time()
    logger.info(f'Database Loaded!  Took {endTime - startTime:.5f}s')


#using @bot.listen() will listen for messages, but will continue processing commands, so having the await bot.process_commands(message) when this is set with @bot.listen() decorator it will fire the command twice.
@bot.event  
async def on_message(message):

    # print(f'{message.created_at}, Guild: {message.guild}, Channel: {message.channel}, Author: {message.author}, Message: {message.content}')
    # print(f'{bot.activity}')

    if message.author == bot.user: #avoid infinite loops
        return
    if isinstance(message.channel, discord.DMChannel):
        dmlogger.info(f'{message.created_at}, Channel: {message.channel}, Author: {message.author}, Message: {message.content}')
        return

    if cliArgs.test and message.channel.name != 'bot-testing': #only allow processing of messages in the bot-testing channel
        return

    #Fix "auto-completed" en and em dashes
    message.content = message.content.replace('\u2013', '--')
    message.content = message.content.replace('\u2014', '--')
    #Fix fancy single quotes
    message.content = message.content.replace('\u2018', '\'')
    message.content = message.content.replace('\u2019', '\'')
    #Fix fancy double quotes
    message.content = message.content.replace('\u201C', '"')
    message.content = message.content.replace('\u201D', '"')

    #await message.channel.send(f"Got {message.content}")

    cards_to_search = []

    cards_to_search_pattern_one = card_fetch_pattern.findall(message.content)
    cards_to_search_pattern_two = card_fetch_pattern_2.findall(message.content)

    cards_to_search.extend(cards_to_search_pattern_one)
    cards_to_search.extend(cards_to_search_pattern_two)

    if len(cards_to_search) > 0:
        counter = 0
        #await message.channel.send(f"You want me to look up {len(cards_to_search)} cards?")
        for card_to_search in cards_to_search:
            large_card = False
            card_set_number_pattern_matches = card_set_number_pattern.findall(card_to_search)

            if len(card_set_number_pattern_matches) > 0:
                the_card_set_number = card_set_number_pattern_matches[0][0]
                the_card_set_short_name = card_set_number_pattern_matches[0][1]

                if the_card_set_short_name in ['19', '20', '21', '22', 'MCI']:

                    card_to_query = card_to_search

                    if card_to_query[-1] == "$":
                        large_card = True
                        card_to_query = card_to_query[:-1]

                    counter = counter + 1
                    if counter > 5:
                        await message.channel.send(f"You asked for too many cards at once!  Stopping!")
                        break

                    startTime = time.time()
                    the_card_found = False
                    the_card_color = Color.magenta()

                    if the_card_set_short_name != '19':
                        card_to_query = the_card_set_number

                    logger.info(f"Searching for Card: {card_to_query} from set {the_card_set_short_name}")

                    #First search should be set-card#
                    results = db_cur.execute("SELECT * FROM cards LEFT OUTER JOIN card_types on cards.card_type_id = card_types.card_type_id LEFT OUTER JOIN rarity on cards.rarity_id = rarity.rarity_id LEFT OUTER JOIN sets on cards.set_id = sets.set_id where card_set_number = ? COLLATE NOCASE and sets.set_short_name = ? COLLATE NOCASE", [card_to_query, the_card_set_short_name])

                    the_results = results.fetchall()

                    the_card_found = len(the_results) > 0

                    if the_card_found:
                        logger.info(f"Search Results: {the_results}")

                        the_card_number = the_results[0][1]
                        the_card_name = the_results[0][2]

                        the_card_rating = the_results[0][5]
                        the_card_team = the_results[0][6]
                        the_card_position = the_results[0][7]
                        the_card_side = the_results[0][8]
                        the_card_ability = the_results[0][9]
                        the_card_special_text = the_results[0][10]
                        #the_card_ = the_results[0][]

                        the_strength = the_results[0][11]
                        the_time_units = the_results[0][12]

                        the_offensive_play = the_results[0][13]
                        the_defensive_play = the_results[0][14]

                        the_card_sub_type = the_results[0][15]

                        the_card_effect = the_results[0][16]
                        the_card_timing = the_results[0][17]

                        the_card_type = the_results[0][20]
                        the_card_rarity = the_results[0][23]
                        
                        the_card_color = Color.light_grey()

                        the_card_set = the_results[0][26]
                        the_set_total_cards = the_results[0][29]

                        #If we want the card bigger
                        the_card_image = botCache.fetchCardImageURLWithCache(the_card_number, the_card_type, the_card_set, the_card_special_text)

                        #If we want the thumbnail of the card (default)
                        the_thumbnail_url = nfl5.generateUrl(the_card_number, the_card_type, the_card_set, the_card_special_text)
                        #f"https://paninigames.com/wp-content/uploads/2019/08/{the_card_number.lower()}.jpg"

                        endTime = time.time()

                        if the_card_special_text != "":
                            the_card_special_text = f" [{the_card_special_text.upper()}]"
                        if the_card_sub_type != "":
                            the_card_sub_type = f" - {the_card_sub_type}"

                        if large_card:
                            embed = discord.Embed(title=f"{the_card_name} ({the_card_number}){the_card_special_text}", color=the_card_color) #can also have url, description, color
                            with io.BytesIO(the_card_image.tobytes()) as image_binary:
                                the_card_image.save(image_binary, 'PNG')
                                image_binary.seek(0)
                                await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'), embed=embed)

                        else:
                            #If we want the thumbnail of the card (default)
                            embed = discord.Embed(title=f"{the_card_name} ({the_card_number}){the_card_special_text}", color=the_card_color) #can also have url, description, color
                            #embed.set_author(name=the_card_name)#, icon_url=the_set_icon_url) #icon_url is actually a url
                            embed.set_thumbnail(url=the_thumbnail_url)

                            if the_card_type == 'Player':
                                embed.add_field(name="Rating", value=f"{the_card_rating}", inline=True)
                                embed.add_field(name="Position", value=f"{the_card_position}", inline=True)
                                embed.add_field(name="Side", value=f"{the_card_side}", inline=True)
                                embed.add_field(name="Team", value=f"{the_card_team}", inline=False)
                                embed.add_field(name="Ability", value=f"{the_card_ability}", inline=False)

                            if the_card_type == 'Play':
                                embed.add_field(name="Strength", value=f"{the_strength}", inline=True)
                                embed.add_field(name="Time Units", value=f"{the_time_units}", inline=True)
                                embed.add_field(name="Offense", value=f"{the_offensive_play}", inline=False)
                                embed.add_field(name="Defense", value=f"{the_defensive_play}", inline=False)

                            if the_card_type == 'Action':
                                embed.add_field(name="Effect", value=f"{the_card_effect}", inline=False)
                                embed.add_field(name="Timing", value=f"{the_card_timing}", inline=False)

                            embed.add_field(name="Card Type", value=f"{the_card_type}{the_card_sub_type}", inline=False)
                            embed.add_field(name="Set", value=f"{the_card_set} ({the_set_total_cards})", inline=False)
                            embed.set_footer(text=f'Card Search took {endTime - startTime:.5f}s')
                            await message.channel.send(embed=embed)
                            
                    else:
                        logger.info(f"No results for Card Search: {card_to_search}")
                        await message.channel.send(f"No card found by the name of '{card_to_search}'")
                else:
                    logger.info(f"Set {the_card_set_short_name} does not exist.")
                    await message.channel.send(f"Set with a short name of {the_card_set_short_name} does not exist.")
            else:
                logger.info(f"Malformed request for Card Search: {card_to_search} - Might be a card name, trying to search via name.")

                #ORDER BY sets.set_year_released, cards.card_set_number
                results = db_cur.execute("SELECT * FROM cards LEFT OUTER JOIN card_types on cards.card_type_id = card_types.card_type_id LEFT OUTER JOIN rarity on cards.rarity_id = rarity.rarity_id LEFT OUTER JOIN sets on cards.set_id = sets.set_id where card_name = ? COLLATE NOCASE", [card_to_search])
                the_results = results.fetchall()
                too_many_results = len(the_results) > 10
                if not too_many_results:
                    result_counter = 0
                    search_results_output = ""
                    for card_result in the_results:
                        result_counter = result_counter + 1
                        logger.info(f"Search Result {result_counter}: {card_result}")
                        the_card_number = card_result[1]
                        the_card_set = card_result[26]
                        the_card_set_short_name = card_result[25]
                        if the_card_set_short_name != '19':
                            search_results_output = f"{search_results_output} {the_card_number}-{the_card_set_short_name},"
                        else:
                            search_results_output = f"{search_results_output} {the_card_number},"
                    search_results_output = search_results_output[:-1]
                    if len(the_results) > 0:
                        await message.channel.send(f"Search Request for '{card_to_search}' returned the following {len(the_results)} result(s):{search_results_output}")
                    else:
                        #Possibly in this case execute a fuzzy search?  https://www.datacamp.com/tutorial/fuzzy-string-python
                        await message.channel.send(f"Search Request for '{card_to_search}' returned no results.")
                else:
                    logger.info(f"Too many results returned for {card_to_search}.")
                    await message.channel.send(f"Search Request for '{card_to_search}' returned too many results {len(the_results)}.  Try a different search.")

                #### TRY VIA THE PLAYER NAME
                
    #else:
        #await message.channel.send(f"No cards to search here....")

    await bot.process_commands(message) #this will continue processing to allow commands to fire.

@bot.command(name='buildPickCache', aliases=['bPC'], hidden=True)
@commands.is_owner()
async def buildPickCache(ctx, *args):
    startTime = time.time()
    #await ctx.message.id.delete()
    await ctx.author.send(f'Building Pick Cache... for {len(jsd.jumpstart)} items')
    theCurrentSet = ""
    #processingTTL =  (when do we want to send a message?  based on some TTL I'd suppose?)
    for dataList in jsd.jumpstart:
        startTime2 = time.time()
        botCache.fetchThemeImageWithCacheScryfallCardImage(dataList['Set'], dataList['Theme'])
        endTime2 = time.time()
        if(theCurrentSet != dataList['Set']):
            theCurrentSet = dataList['Set']
            await ctx.author.send(f"Caching Theme Card Images for Set '{dataList['Set']}'")
        time.sleep(100/1000)

    endTime = time.time()
    await ctx.author.send(f'Done Building Pick Cache... took {endTime - startTime:.5f}s')
    await ctx.author.send(content=str(botCache), suppress_embeds=True)

@bot.command(name='purgeListCache', aliases=['pLC'], hidden=True)
@commands.is_owner()
async def purgeImageCache(ctx, *args):
    startTime = time.time()
    #await ctx.message.id.delete()
    await ctx.author.send(f'Purging List Cache...')
    botCache.purgeListCache()
    endTime = time.time()
    await ctx.author.send(f'Done Purging List Cache... took {endTime - startTime:.5f}s')

@bot.command(name='purgeImageCache', aliases=['pIC'], hidden=True)
@commands.is_owner()
async def purgeImageCache(ctx, *args):
    startTime = time.time()
    #await ctx.message.id.delete()
    await ctx.author.send(f'Purging Image Cache...')
    botCache.purgeImageCache()
    endTime = time.time()
    await ctx.author.send(f'Done Purging Image Cache... took {endTime - startTime:.5f}s')

@bot.command(name='purgeScryfallCache', aliases=['pSC'], hidden=True)
@commands.is_owner()
async def purgeScryfallCache(ctx, *args):
    startTime = time.time()
    #await ctx.message.id.delete()
    await ctx.author.send(f'Purging Scryfall JSON Card Cache...')
    botCache.purgeScryfallJSONCardCache()
    endTime = time.time()
    await ctx.author.send(f'Done Purging Scryfall JSON Card Cache... took {endTime - startTime:.5f}s')

@bot.command(name='stats', aliases=[])
async def statistics(ctx, *args):
    await ctx.send(content=str(botCache), suppress_embeds=True)

@bot.command(aliases=['information', 'fancontent', 'license'])
async def info(ctx):
    await ctx.send(content=f"NFL Five Card Fetcher Bot {version}\n\nThis Discord Bot is unofficial Fan Content. Not approved/endorsed by Panini. Portions of the materials used are property of Panini. ©Panini.\n\nSource Code is released under the MIT License https://github.com/tyraziel/NFL-Five-Discord-Bot/ -- 2025", suppress_embeds=True)

bot.run(bot_env['BOT_TOKEN'])
