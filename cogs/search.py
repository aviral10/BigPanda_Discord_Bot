import datetime
import discord
import json
import re
from discord.ext import commands
import functools
import googletrans
import requests
import random


class BAsearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='translate')
    async def _translate(self, ctx, text, *, langs=""):
        """: Translate things you don't understand
        """

        def convert(s: str) -> dict:
            a = s.lower().split()
            res = {
                a[i]: a[i + 1]
                for i in range(len(a)) if a[i] in ("from", "to")
            }
            res["from"] = res.get("from") or "auto"
            res["to"] = res.get("to") or "en"
            return res

        try:
            langdict = convert(langs)
        except IndexError:
            raise commands.BadArgument("Invalid language format.")
        translator = googletrans.Translator()
        tmp = functools.partial(
            translator.translate,
            text,
            src=langdict["from"],
            dest=langdict["to"])
        try:
            async with ctx.typing():
                res = await self.bot.loop.run_in_executor(None, tmp)
        except ValueError as e:
            raise commands.BadArgument(e.args[0].capitalize())
        await ctx.send(res.text.replace("@", "@\u200b"))

    @commands.command(pass_context=True)
    async def urban(self, ctx, *, word):
        ': Search the Urban Dictionary'
        try:
            query = "+".join(word.split())
            url = "http://api.urbandictionary.com/v0/define?term="
            with requests.get(url + query) as response:
                data = response.json()
                if len(data['list']) == 0:
                    await ctx.send(
                        f'''Unable to find {word} in Urban dictionary''',
                        delete_after=3)
                    return
                item = data['list'][0]

                if len(item['definition']) <= 2000:
                    embed = discord.Embed(
                        title=f'\U0001f4d6 {word} ',
                        colour=discord.Colour.dark_purple(),
                        description=f'''{item['definition'].replace('[', '').replace(']', '')}''',
                        url=f'''{item['permalink']}'''
                    )
                    embed.add_field(
                        name='Examples', value=f'''{item['example'].replace('[', '').replace(']', '')}''')
                    embed.add_field(
                        name='Upvotes',
                        value=
                        f'''{item['thumbs_up']})'''
                    )
                    embed.add_field(
                        name='Downvotes',
                        value=
                        f'''{item['thumbs_down']})'''
                    )
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title=f'\U0001f4d6 {word}',
                        colour=discord.Colour.dark_purple(),
                        description=
                        f'''{item['definition'][:1800].replace('[', '').replace(']', '')}[...continue reading]({item['permalink']})'''
                    )
                    embed.add_field(
                        name='Examples', value=f'''{item['example'].replace('[', '').replace(']', '')}''')
                    embed.add_field(
                        name='Upvotes',
                        value=
                        f'''{item['thumbs_up']})'''
                    )
                    embed.add_field(
                        name='Downvotes',
                        value=
                        f'''{item['thumbs_down']})'''
                    )
                    await ctx.send(embed=embed)
        except IndexError:
            await ctx.send(
                f'''Unable to find {word} in Urban dictionary''',
                delete_after=3)

    @commands.command(passcontext=True)
    async def youtube(self, ctx, *, arg):
        ': Search YouTube '
        query = str(arg)
        # print("query: ", query)
        url = "https://www.youtube.com/results?search_query="
        with requests.get(url + query) as response:
            # regex = '/watch\?v\=[a-zA-z0-9/_/-/*]+'
            regex = '/watch\?v\=(.*?)\"'
            # regex = r'/watch\?v=[a-zA-Z0-9]+'
            match = re.findall(regex, response.text)[0]
            payload = "https://www.youtube.com/watch?v=" + match
            # print(payload)
            await ctx.send(f"> Here is your result for: {query}\n{payload}")

    @commands.command(passcontext=True)
    async def tenor(self, ctx,*,arg):
        """: Tenor gif, Use: /tenor [QUERY]"""
        apikey = "ZHEH40K6HKJY"  # test value
        lmt = 8
        search_term = str(arg)
        URL = f"https://api.tenor.com/v1/search?q={search_term}&key={apikey}&limit={lmt}"
        # print(URL)
        r = requests.get(URL)
        if r.status_code == 200:
            # load the GIFs using the urls for the smaller GIF sizes
            top_8gifs = json.loads(r.content)
            urls = [top_8gifs['results'][i]['url'] for i in range(lmt)]
            await ctx.send(random.choice(urls))
        else:
            await ctx.send("Had some error")

    @commands.command(
        name="pokemon",
        aliases=["Pokemon", " pokemon", " Pokemon", "info", " info"])
    async def pokemon(self, ctx, *, pokemon):
        ''': Check info about pokemon'''
        from pokedex import pokedex
        pokedex = pokedex.Pokedex(
            version='v1',
            user_agent='ExampleApp (https://example.com, v2.0.1)')
        x = pokedex.get_pokemon_by_name(f'''{pokemon}''')
        embed = discord.Embed(
            title=f'''{x[0]['name']}''',
            description=f'''Discovered in generation {x[0]['gen']}''',
            color=discord.Colour.dark_purple())
        embed.add_field(
            name='Species', value=f'''{x[0]['species']}''', inline=False)
        if not x[0]['gender']:
            embed.add_field(name='Gender', value="No Gender", inline=False)
        else:
            embed.add_field(
                name='Gender',
                value=
                f'''Male:  {x[0]['gender'][0]}%\nFemale:  {x[0]['gender'][1]}%''',
                inline=False)
        embed.add_field(
            name='Type',
            value=f'''{', '.join(str(i) for i in x[0]['types'])}''',
            inline=False)
        embed.set_image(url=f'''{x[0]['sprite']}''')
        embed.add_field(
            name='Abilities',
            value=
            f'''{', '.join(str(i)for i in x[0]['abilities']['normal'])}''',
            inline=False)
        if not x[0]['abilities']['hidden']:
            embed.add_field(
                name='Hidden Abilities',
                value="No hidden talents like me",
                inline=False)
        else:
            embed.add_field(
                name='Hidden Abilities',
                value=
                f'''{', '.join(str(i)for i in x[0]['abilities']['hidden'])}''',
                inline=False)
        embed.add_field(
            name='Egg Groups',
            value=f'''{', '.join(str(i)for i in x[0]['eggGroups'])}''',
            inline=False)
        embed.add_field(
            name='Evolution',
            value=
            f'''{' => '.join(str(i)for i in x[0]['family']['evolutionLine'])}''',
            inline=False)
        embed.add_field(name='Height', value=x[0]['height'], inline=False)
        embed.add_field(name='Weight', value=x[0]['weight'], inline=False)
        if x[0]['legendary']:
            a = 'Legendary'
        elif x[0]['starter']:
            a = 'Starter'
        elif x[0]['mythical']:
            a = 'Mythical'
        elif x[0]['ultraBeast']:
            a = 'Ultra Beast'
        elif x[0]['mega']:
            a = 'Mega'
        else:
            a = '-'
        embed.add_field(name='Notes', value=a, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(BAsearch(client))