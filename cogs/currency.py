import discord
from discord.ext import commands
from discord.ext.commands import BucketType
import re
import asyncio
import psycopg2
from datetime import datetime
import random

from dotenv import load_dotenv
import os
load_dotenv()
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_pass = os.getenv("DB_PASS")
creds = f"dbname='{db_name}' user='{db_user}' host='{db_pass}' password='{db_pass}'"

class Currency(commands.Cog):

    def __init__(self, client):
        self.client = client
    @commands.command(aliases=['bank', 'Bank', 'balance'])
    async def wealth(self, ctx, user:discord.User=None):
        """: Display your wealth
        """
        if user is not None:
            db = psycopg2.connect(creds)
            cursor = db.cursor()
            sql = ("SELECT user_id, inbank, inhand FROM currency WHERE guild_id = %s and user_id = %s")
            val = (str(ctx.guild.id), str(user.id))
            cursor.execute(sql, val)
            result = cursor.fetchone()
            if result is None:
                await ctx.send("> That user is not yet registered")
            else:
                embed = discord.Embed(
                    description=f"{user.name} is worth `{str(result[1])}` bytes :keyboard: and has `{str(result[2])}` bytes in hand :eyes:"
                )
                await ctx.send(embed=embed)
            cursor.close()
            db.close()
        elif user is None:
            db = psycopg2.connect(creds)
            cursor = db.cursor()
            sql = ("SELECT user_id, inbank, inhand FROM currency WHERE guild_id = %s and user_id = %s")
            val = (str(ctx.guild.id), str(ctx.author.id))
            cursor.execute(sql,val)
            result = cursor.fetchone()
            if result is None:
                await ctx.send("> That user is not yet registered")
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.name} is worth `{str(result[1])}` bytes :keyboard: and has `{str(result[2])}` bytes in hand :eyes:"
                )
                await ctx.send(embed=embed)
            cursor.close()
            db.close()


    @commands.command()
    async def rich_list(self, ctx):
        """: List of top 5 wealthiest members in the server
        """
        db = psycopg2.connect(creds)
        cursor = db.cursor()
        sql = "SELECT inbank,inhand,user_id FROM currency WHERE guild_id = %s"
        val = (str(ctx.guild.id),)
        cursor.execute(sql, val)
        res = cursor.fetchall()
        mess1 = ":keyboard: Wealthiest members :keyboard: :"
        mess = ""
        mess += "{: <5} {: <8} {: <8} {: <10}\n".format("Rank", "In Bank", "In Hand", "User")
        x = 1
        finarr = []
        for ele in res:
            payload = [int(ele[0]), int(ele[1]), ele[2]]
            finarr.append(payload)
        finarr.sort(reverse=True)
        for ele in finarr:
            if x == 11:
                break

            name_user = "NULL"
            try:
                user = self.client.get_user(int(ele[2]))
                name_user = user.name
            except:
                name_user = "NOTFOUND"

            mess += "{: <5} {: <8} {: <8} {: <10}\n".format(x, "₿ " + str(ele[0]), "₿ " + str(ele[1]), name_user)
            x += 1
        await ctx.send(f"{mess1}```py\n{mess}```")

    @commands.command()
    async def deposit(self, ctx):
        """: Deposit your in-hand bytes to bank
        """
        db = psycopg2.connect(creds)
        cursor = db.cursor()
        sql = ("SELECT user_id, inbank, inhand FROM currency WHERE guild_id = %s and user_id = %s")
        val = (str(ctx.guild.id), str(ctx.author.id))
        cursor.execute(sql, val)
        result = cursor.fetchone()
        if result is None:
            await ctx.send(f"> You are not registered")
        elif int(result[2]) == 0:
            await ctx.send(f"> You got nothing to deposit, go steal from someone!")
        else:
            sql = ("UPDATE currency SET inhand = %s, inbank = %s WHERE guild_id = %s and user_id = %s")
            val = (str(0), str(int(result[2]) + int(result[1])), str(ctx.guild.id), str(ctx.author.id))
            cursor.execute(sql, val)
            db.commit()
            embed = discord.Embed(
                description=f"Successfully transferred `{result[2]} bytes` :keyboard: to bank"
            )
            await ctx.send(embed=embed)
        cursor.close()
        db.close()

    @commands.command()
    async def steal(self, ctx,user:discord.User=None):
        """: Steal someone's in hand bytes
            Before you steal make sure you are registered, to register: /trivia , answer 1 question correctly"""
        if user is None:
            await ctx.send("Error: /steal <mention>")
            return
        if user.id == ctx.author.id:
            st = random.randint(1,4)

            db = psycopg2.connect(creds)
            cursor = db.cursor()
            sql = ("SELECT user_id, inbank FROM currency WHERE guild_id = %s and user_id = %s")
            val = (str(ctx.guild.id), str(user.id))
            cursor.execute(sql, val)
            result_user = cursor.fetchone()
            if result_user is None:
                await ctx.send(f"> No User found!, play some /trivia")
                return
            sql = ("UPDATE currency SET inbank = %s WHERE guild_id = %s and user_id = %s")
            val = (str(int(result_user[1])-st), str(ctx.guild.id), str(ctx.author.id))
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            await ctx.send(f"> Don't try to be a smartass. Here, I'm stealing `{st} bytes` from you.")
            return
        db = psycopg2.connect(creds)
        cursor = db.cursor()
        sql = ("SELECT user_id, inbank, inhand FROM currency WHERE guild_id = %s and user_id = %s")
        val = (str(ctx.guild.id), str(user.id))
        cursor.execute(sql, val)
        result_user = cursor.fetchone()

        sql = ("SELECT user_id, inbank, inhand FROM currency WHERE guild_id = %s and user_id = %s")
        val = (str(ctx.guild.id), str(ctx.author.id))
        cursor.execute(sql, val)
        result_me = cursor.fetchone()
        if result_me is None:
            await ctx.send("> You are not yet registered, try some /trivia")
            cursor.close()
            db.close()
            return

        if result_user is None:
            await ctx.send("The user is not registered")
        elif int(result_user[2]) <= 1:
            await ctx.send(f"> {user.name} has next to nothing in hand")
        else:
            dt = datetime.now()
            sql = ("SELECT user_id,time FROM cooldown WHERE guild_id = %s and user_id = %s")
            val = (str(ctx.guild.id), str(ctx.author.id))
            cursor.execute(sql, val)
            c_res = cursor.fetchone()
            eligible = True
            if c_res is not None:
                diff = datetime.now() - c_res[1]
                diff = diff.total_seconds()
                if diff >= 3600:
                    eligible = True
                    sql = ("UPDATE cooldown SET time = %s WHERE guild_id = %s and user_id = %s")
                    val = (dt,str(ctx.guild.id), str(ctx.author.id))
                    cursor.execute(sql, val)
                    db.commit()
                else:
                    diff = 3600 - diff
                    await ctx.send(f"> Hold on amigo, try again in `{diff//60}` minutes and `{int(diff%60)}` seconds")
                    eligible = False
            else:
                sql = ("INSERT INTO cooldown(guild_id,user_id,time,type) VALUES(%s,%s,%s,%s)")
                val = (str(ctx.guild.id), str(ctx.author.id), dt, "steal")
                cursor.execute(sql, val)
                db.commit()


            steal_amt = random.randint(0, int(result_user[2]) // 2 + 1)
            #print("Steal: ", steal_amt)
            if eligible:
                if steal_amt == 0:
                    payup = random.randint(0, int(result_user[2]) // 2 + 1)

                    sql = ("UPDATE currency SET inbank = %s WHERE guild_id = %s and user_id = %s")
                    val = (str(int(result_me[1]) - payup), str(ctx.guild.id), str(ctx.author.id))
                    cursor.execute(sql, val)
                    db.commit()
                    sql = ("UPDATE currency SET inhand = %s WHERE guild_id = %s and user_id = %s")
                    val = (str(int(result_user[2]) + payup), str(ctx.guild.id), str(user.id))
                    cursor.execute(sql, val)
                    db.commit()

                    await ctx.send(
                        f"> you got caught stealing from `{user.name}` and as a penalty you pay him `{payup}` bytes")
                else:
                    sql = ("SELECT user_id, inbank, inhand FROM currency WHERE guild_id = %s and user_id = %s")
                    val = (str(ctx.guild.id), str(ctx.author.id))
                    cursor.execute(sql, val)
                    result_me = cursor.fetchone()


                    sql = ("UPDATE currency SET inhand = %s WHERE guild_id = %s and user_id = %s")
                    val = (str(int(result_me[2])+steal_amt), str(ctx.guild.id), str(ctx.author.id))
                    cursor.execute(sql, val)
                    db.commit()
                    sql = ("UPDATE currency SET inhand = %s WHERE guild_id = %s and user_id = %s")
                    val = (str(int(result_user[2]) - steal_amt), str(ctx.guild.id), str(user.id))
                    cursor.execute(sql, val)
                    db.commit()
                    await ctx.send(f"> You have stolen `{steal_amt} bytes` :keyboard: from {user.name}")
        cursor.close()
        db.close()


    @commands.command()
    async def donate(self, ctx, arg, user:discord.User=None):
        """: Donate bytes to a server member: /donate <amount> <mention>
        """
        if user is None:
            await ctx.send("> Mention a user, you want to donate to")
        else:
            if user.id == ctx.author.id:
                await ctx.send(f"> Can't donate to yourself")
                return
            db = psycopg2.connect(creds)
            cursor = db.cursor()
            sql = ("SELECT user_id, inbank, inhand FROM currency WHERE guild_id = %s and user_id = %s")
            val = (str(ctx.guild.id), str(user.id))
            cursor.execute(sql, val)
            result_user = cursor.fetchone()
            value = int(arg)
            if result_user is None:
                await ctx.send("The user is not registered")
            else:
                sql = ("SELECT user_id, inbank, inhand FROM currency WHERE guild_id = %s and user_id = %s")
                val = (str(ctx.guild.id), str(ctx.author.id))
                cursor.execute(sql, val)
                result_me = cursor.fetchone()
                if result_me is None:
                    await ctx.send(f"> You are not yet registered, play some /trivia")
                    cursor.close()
                    db.close()
                    return
                if value > int(result_me[1]):
                    await ctx.send("> You don't have enough :keyboard: bytes")
                else:
                    sql = ("UPDATE currency SET inbank = %s WHERE guild_id = %s and user_id = %s")
                    val = (str(int(result_me[1]) - value), str(ctx.guild.id), str(ctx.author.id))
                    cursor.execute(sql, val)
                    db.commit()
                    sql = ("UPDATE currency SET inhand = %s WHERE guild_id = %s and user_id = %s")
                    val = (str(int(result_user[2]) + value), str(ctx.guild.id), str(user.id))
                    cursor.execute(sql, val)
                    db.commit()
                    await ctx.send(f"You donated `{arg} bytes` :keyboard: to {user.name}")
            cursor.close()
            db.close()




def setup(client):
    client.add_cog(Currency(client))