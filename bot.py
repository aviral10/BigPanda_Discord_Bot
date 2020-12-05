import random
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from discord.ext.commands.errors import *
import datetime
from discord.ext import tasks
import requests
import asyncio

load_dotenv()
intents = discord.Intents.all()
client = commands.Bot(command_prefix='/', intents=intents)
client.remove_command("help")


###########
@client.command()
@commands.has_role("masterPanda")
async def load(ctx, extension):
    """: Load a cog"""
    client.load_extension(f"cogs.{extension}")


@client.command()
@commands.has_role("masterPanda")
async def unload(ctx, extension):
    """: Unload a cog"""
    client.unload_extension(f"cogs.{extension}")


@client.command()
@commands.has_role("masterPanda")
async def reload(ctx, extension):
    """: Reload a cog"""
    client.reload_extension(f"cogs.{extension}")

for filename in os.listdir('./cogs'):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")


@client.event
async def on_ready():
    change_status.start()
    print("Bot is Online!")


@tasks.loop(seconds=3600)
async def change_status():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f": /help"))

######

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, (BadUnionArgument, CommandOnCooldown, PrivateMessageOnly,
                          NoPrivateMessage, MissingRequiredArgument, ConversionError)):
        return await ctx.send(f"> {str(error)}")
    elif isinstance(error, MissingPermissions):
        return await ctx.send("> You don't have permissions to use this command")
    elif isinstance(error, MissingAnyRole):
        return await ctx.send("> You don't have permissions to use this command")
    elif isinstance(error, BadArgument):
        return await ctx.send(f"> Invalid argument. Please try again.")
    else:
        await ctx.send(f"> Unrecognised command, try again\n")


# Commands:
@client.command()
async def ping(ctx):
    """: Test command to check bot's response time
    """
    await ctx.send(f"Pong! {round(client.latency*1000)}ms")


@client.command()
@commands.has_any_role("Admin", "masterPanda")
async def clear(ctx, amount=5):
    """: Admin command to clear chats, e.g. clear(10)"""
    await ctx.channel.purge(limit=amount)



hellos = ['Howdy!', 'Hey there', 'Aloha', 'Bonjour', 'Hi']
@client.command(aliases=["sayhi"])
async def sayHi(ctx):
    """: Says Hi to you
    """
    await ctx.send(f"{random.choice(hellos)} {ctx.author.mention}!")


@client.command(aliases=["sayhito"])
async def sayHito(ctx, member):
    """: Say Hi to a mentioned member
    """
    await ctx.send(f"{random.choice(hellos)} {member}!")


@client.command(aliases=["answerme", "8ball"])
async def _8ball(ctx, *, question):
    """: Classic 8 ball game, use: /answerme question
    """
    responses = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes – definitely', 'Ohh yeah',
               'As I see it, yes', 'Most likely', 'Yes Signs point to yes', 'try again',
               'Ask again later', 'Dont count on it', 'My reply is no', 'My sources say no', 'Very doubtful']
    await ctx.send(f"Question: {question}\nAnswer: {random.choice(responses)}")


@client.command()
async def joke(ctx):
    """: Get a joke: /joke
    """
    with requests.get("http://www.official-joke-api.appspot.com/random_joke") as response:
        data = response.json()
        if response.status_code == 200:
            await ctx.send(f"> {data['setup']}")
            def check(m):
                return m.author == ctx.author
            try:
                a = await client.wait_for('message', check=check, timeout=30)
                embed = discord.Embed(description=f"{data['punchline']}", color=ctx.author.color)
                await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                embed = discord.Embed(description=f"{data['punchline']}", color=ctx.author.color)
                await ctx.send(embed=embed)
        else:
            await ctx.send("`Had Some Error`")


@client.command(aliases=["ins"])
async def insult(ctx, user:discord.User=None):
    """: Insult someone: /ins <@mention>
    """
    headers = {"json": "text/json"}
    with requests.get("https://insult.mattbas.org/api/insult.json/", headers=headers) as response:
        mess = response.json()["insult"]
    if len(mess) == 0:
        ctx.send("`Had Some Error`")
    else:
        if user is None:
            await ctx.send(f"> {mess}")
        else:
            await ctx.send(f"> {user.name} is{mess[7:]}")


@client.command()
async def help(ctx):
    embed = discord.Embed(
        title=f'''Commands: ''',
        description=f'''Bot prefix: `/`''',
        color=discord.Colour.green())
    embed.add_field(
        name='General', value=f'''```
answerme    : Classic 8 ball game, use: /answerme question
joke        : Get a joke: /joke
insult      : Insult someone: /ins <@mention>
ping        : Test command to check bot's response time
sayHi       : Says Hi to you
sayHito     : Say Hi to a mentioned member```
''', inline=False)
    embed.add_field(
        name='Leveling', value=f'''```
rank        : Display your rank: /rank or /rank <@mention>
rank_help   : Rank help
rank_list   : Displays top 10 Active Members in the server```
    ''', inline=False)
    embed.add_field(
        name='Python', value=f'''```
python      : Run Simple python codes use: /python xyz```
            ''', inline=False)
    embed.add_field(
        name='Currency', value=f'''```
deposit     : Deposit your in-hand bytes to bank
donate      : Donate bytes to a server member: 
              /donate <amount> <mention>
rich_list   : List of top 10 wealthiest members in the server
steal       : Steal someone's in hand bytes: 
              /steal <@mention>
wealth      : Display your wealth: /bank, /wealth, /balance
trivia      : Earn bytes: /trivia
buy_role    : Buy yourself a custom role(300 bytes).
              Use: /buy_role <color_in_hex> <name>
              example: /buy_role 3dffe5 Gay
update_role : Customize your role name: 
              /update_role 3dffe5 Not Gay
              or /update_role 3dffe5 (To only update color)
                ```''', inline=False)
    embed.add_field(
        name='Misc', value=f'''```
pokemon     : Check info about pokemon
              /pokemon bulbasaur
translate   : Translate things you don't understand
urban       : Search the Urban Dictionary: /urban word
youtube     : Search YouTube: /youtube SEARCH_CONTENT
tenor       : Tenor gifs: /tenor QUERY
                ```''', inline=False)
    embed.add_field(
        name='Tags', value=f'''```
Available for [lvl 5]+
add_tag     : Add a custom tag: /add_tag <tagname>
del_tag     : Delete an existing tag:/del_tag <tagname>
list_tags   : Display the list of tags: /list_tags
tag         : Call a tag: /tag <tagname>
update_tag  : Update an existing tag: /update_tag <tagname>
                ```''', inline=False)
    await ctx.send(embed=embed)

# Run the BOT
BOT_TOKEN = os.getenv("BOT_TOKEN")
client.run(BOT_TOKEN)

