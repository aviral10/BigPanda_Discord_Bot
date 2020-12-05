import discord
from discord.ext import commands
import re
import asyncio
import psycopg2
import requests
import random
from dotenv import load_dotenv
import os
load_dotenv()
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_pass = os.getenv("DB_PASS")
creds = f"dbname='{db_name}' user='{db_user}' host='{db_pass}' password='{db_pass}'"

class Trivia(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def trivia(self, ctx):
        """: Trivia question: /trivia, answering 1 question successfully gets you registered"""
        url = "https://opentdb.com/api.php?amount=50&category=18&type=multiple"
        with requests.get(url) as response:
            regex = '\&(.*?)\;'
            data = response.json()['results'][random.randint(0,49)]
            question = data['question'].replace("&#039;", "'").replace("&quot;", "\"")
            answer = data['correct_answer'].replace("&#039;", "'").replace("&quot;", "\"")
            #print(answer)
            inc_answers = data['incorrect_answers']
            question = re.sub(regex, '', question)
            answer = re.sub(regex, '', answer)
            d = {"a": "", "b": "", "c": "", "d": ""}
            inc_answers.append(answer)
            random.shuffle(inc_answers)
            for i in range(4):
                word = inc_answers[i].replace("&#039;", "'").replace("&quot;", "\"")
                word = re.sub(regex, '', word)
                d[chr(ord('a') + i)] = word

            def check(m):
                return m.author == ctx.author

            embed = discord.Embed(
                title=f'\U0001f4d6 Question: {question}',
                colour=discord.Colour.dark_purple(),
            )
            await ctx.send(embed=embed)
            try:
                embed = discord.Embed(
                    colour=discord.Colour.blue(),
                    description=f'''```py\nYour answer: (Type a,b,c,d)\nA: {d['a']}\nB: {d['b']}\nC: {d['c']}\nD: {d['d']}\n```''',
                )
                await ctx.send(embed=embed)
                a = await self.client.wait_for('message', check=check, timeout=15)
                content = str(a.content)
                #print(d[content.lower()[0]].lower(), answer.lower())
                if len(content) > 1:
                    embed = discord.Embed(
                        colour=discord.Colour.red(),
                        description=f'''{content} is incorrect\nCorrect answer: `{answer}`''',
                    )
                    await ctx.send(embed=embed)
                    return
                if d[content.lower()[0]].lower() == answer.lower():
                    earn = random.randint(1, 4)
                    embed = discord.Embed(
                        colour=discord.Colour.green(),

                        description=f'''That was Correct\nYou earned {earn} bytes :keyboard:''',
                    )
                    await ctx.send(embed=embed)
                    db = psycopg2.connect(creds)
                    cursor = db.cursor()
                    sql = ("SELECT user_id,inbank,inhand FROM currency WHERE guild_id = %s and user_id = %s")
                    val = (str(ctx.guild.id), str(ctx.author.id))
                    cursor.execute(sql, val)
                    result = cursor.fetchone()

                    if result is None:
                        sql = ("INSERT INTO currency(guild_id,user_id,inhand,inbank) VALUES(%s,%s,%s,%s)")
                        val = (str(ctx.guild.id), str(ctx.author.id), str(earn), str(0))
                        cursor.execute(sql, val)
                        db.commit()
                    else:
                        prev_value = int(result[2])
                        sql = ("UPDATE currency SET inhand = %s WHERE guild_id = %s and user_id = %s")
                        val = (str(prev_value + earn), str(ctx.guild.id), str(ctx.author.id))
                        cursor.execute(sql, val)
                        db.commit()
                    cursor.close()
                    db.close()
                else:
                    embed = discord.Embed(
                        colour=discord.Colour.red(),
                        description=f'''{content[0]} is incorrect\nCorrect answer: `{answer}`''',
                    )
                    await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                await ctx.send(f'> Sorry, you took too long\nCorrect answer: `{answer}`')
                return

    @commands.command()
    async def trivia_help(self, ctx):
        """: trivia help"""
        embed = discord.Embed(
                        colour=discord.Colour.blue(),
                        description=f"Answer the questions correctly to earn bytes\n",
                    )
        await ctx.send(embed=embed)



def setup(client):
    client.add_cog(Trivia(client))