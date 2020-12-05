import discord
from discord.ext import commands
import math
from datetime import datetime
import random
import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_pass = os.getenv("DB_PASS")
creds = f"dbname='{db_name}' user='{db_user}' host='{db_pass}' password='{db_pass}'"

starts_symbols = "`!@#$%^&*()_+{}|::><?'\"\\"

class Level(commands.Cog):

    def __init__(self, client):
        self.client = client

    def cooldown_check(self,curr, prev):
        hrc,mnc = [int(x) for x in curr.split(":")]
        hrp,mnp = [int(x) for x in prev.split(":")]
        if hrc == hrp:
            if abs(mnp - mnc) >= 2:
                return True
            else:
                return False
        else:
            return True

    @commands.Cog.listener()
    async def on_message(self, message):
        # print(f"Listening in level cog, aut: {message.author.name}")
        if len(str(message.content)) < 1:
            return
        elif str(message.content)[0] in starts_symbols:
            return
        if message.author != self.client.user:
            guild = self.client.get_guild(614871520275333120)
            try:
                bots = discord.utils.get(guild.roles, name="bot buddies")
                panda = discord.utils.get(guild.roles, name="Panda")
                tle = discord.utils.get(guild.roles, name="TLE")
                if bots in message.author.roles or panda in message.author.roles or tle in message.author.roles:
                    # print("Yeah breaking")
                    return
                else:
                    pass
                    # print("Nope")
            except:
                print("Couldn't find bot")
            # tle = discord.utils.get(guild.roles, name="TLE")
            # if tle in message.author.roles:
            #     return
            # if bots in message.author.roles:
            #     return
            valid_channels = [701848853653225552, 614877136402120744, 735523127802593291, 708195686130253844, 615064884022870043, 746388415255281835, 615459768290508830]

            if message.channel.id not in valid_channels:
                return
            # if message.channel.id != 701848853653225552 and message.channel.id != 614877136402120744 and message.channel.id!= 735523127802593291 and message.channel.id != 708195686130253844:
            #     return
            db = psycopg2.connect(creds)
            cursor = db.cursor()
            sql = ("SELECT user_id FROM levels WHERE guild_id = %s and user_id = %s")
            val = (str(message.guild.id),str(message.author.id))
            cursor.execute(sql, val)
            result = cursor.fetchone()
            if result is None:
                curr = str(datetime.now())[10:16]
                sql = ("INSERT INTO levels(guild_id, user_id, xp,lvl,last_mess) VALUES(%s,%s,%s,%s,%s)")
                val = (message.guild.id, message.author.id, 2, 1, curr)
                cursor.execute(sql, val)
                db.commit()
            else:
                sql = ("SELECT user_id,xp,lvl,last_mess FROM levels WHERE guild_id = %s and user_id = %s")
                val = (str(message.guild.id),str(message.author.id))
                cursor.execute(sql, val)
                result1 = cursor.fetchone()
                exp = int(result1[1])
                curr = str(datetime.now())[10:16]
                prev = result1[3]
                if self.cooldown_check(curr,prev):
                    sql = ("UPDATE levels SET xp = %s, last_mess = %s WHERE guild_id = %s and user_id = %s")
                    val = (exp + 2 + random.randint(10,30) + math.floor(len(str(message.content))*0.03), curr,str(message.guild.id), str(message.author.id))
                    cursor.execute(sql, val)
                    db.commit()

                    sql = ("SELECT user_id,xp,lvl,last_mess FROM levels WHERE guild_id = %s and user_id = %s")
                    val = (str(message.guild.id), str(message.author.id))
                    cursor.execute(sql, val)
                    result2 = cursor.fetchone()
                    xp_start = int(result2[1])
                    lvl_start = int(result2[2])
                    #xp_end = math.floor(5 * (lvl_start)**0.5 + 50*lvl_start +100)
                    xp_end = math.floor(200*lvl_start)
                    if xp_end < xp_start:
                        await message.channel.send(f"{str(message.author.mention)} has leveled up to level {str(lvl_start+1)}!")
                        db = psycopg2.connect(creds)
                        cursor = db.cursor()
                        sql = ("SELECT user_id,inbank,inhand FROM currency WHERE guild_id = %s and user_id = %s")
                        val = (str(message.guild.id), str(message.author.id))
                        cursor.execute(sql, val)
                        result = cursor.fetchone()

                        if result is None:
                            sql = ("INSERT INTO currency(guild_id,user_id,inhand,inbank) VALUES(%s,%s,%s,%s)")
                            val = (str(message.guild.id), str(message.author.id), str((lvl_start + 1) + 10), str(0))
                            cursor.execute(sql, val)
                            db.commit()
                        else:
                            prev_value = int(result[2])
                            sql = ("UPDATE currency SET inhand = %s WHERE guild_id = %s and user_id = %s")
                            val = (str(prev_value + lvl_start + 1 + 10), str(message.guild.id), str(message.author.id))
                            cursor.execute(sql, val)
                            db.commit()
                        await message.channel.send(f"> And here are your level up bytes: ₿ {(lvl_start+1)+10}\n> Don't forget to deposit them.")

                        if lvl_start+1 == 5:
                            await message.channel.send(f"> :desktop:  Congratulations! You're hence pronounced an `Active Member` :desktop: ")
                            active_member = discord.utils.get(message.author.guild.roles, name="[lvl 5] Active Coder")
                            if active_member not in message.author.roles:
                                await message.author.add_roles(active_member)
                        if lvl_start+1 == 10:
                            await message.channel.send(f"> :keyboard: Congratulations! You're hence pronounced `Server Sensei` :keyboard: ")
                            active_member = discord.utils.get(message.author.guild.roles, name="[lvl 10] Server Sensei")
                            if active_member not in message.author.roles:
                                await message.author.add_roles(active_member)
                        if lvl_start+1 == 20:
                            await message.channel.send(f"> :crossed_swords:  All hail the Orz! :crossed_swords:")
                            active_member = discord.utils.get(message.author.guild.roles, name="[lvl 20] Orz")
                            if active_member not in message.author.roles:
                                await message.author.add_roles(active_member)


                        sql = ("UPDATE levels SET lvl = %s, xp = %s WHERE guild_id = %s and user_id = %s")
                        val = (int(lvl_start+1), str(0) ,str(message.guild.id), str(message.author.id))

                        # cursor.execute(sql, val)
                        # db.commit()
                        # sql = ("UPDATE levels SET xp = %s WHERE guild_id = %s and user_id = %s")
                        # val = (0, str(message.guild.id), str(message.author.id))
                        cursor.execute(sql, val)
                        db.commit()
                        cursor.close()
                        db.close()

    @commands.command()
    async def rank(self, ctx, user:discord.User=None):
        """: Display your rank in the server
        """
        if user is not None:
            db = psycopg2.connect(creds)
            cursor = db.cursor()
            sql = ("SELECT user_id, xp, lvl FROM levels WHERE guild_id = %s and user_id = %s")
            val = (str(ctx.guild.id), str(user.id))
            cursor.execute(sql, val)
            result = cursor.fetchone()
            if result is None:
                await ctx.send("That user is not yet ranked")
            else:
                embed = discord.Embed(
                    description=f"```py\n{user.name} is currently on level {str(result[2])} and has {str(result[1])} XP\nXP needed for next level: {int(result[2])*200 - int(result[1])}```")
                await ctx.send(embed=embed)
            cursor.close()
            db.close()
        elif user is None:
            db = psycopg2.connect(creds)
            cursor = db.cursor()
            sql = "SELECT user_id, xp, lvl FROM levels WHERE guild_id = %s and user_id = %s"
            val = (str(ctx.message.guild.id),str(ctx.message.author.id))
            cursor.execute(sql,val)
            result = cursor.fetchone()
            if result is None:
                await ctx.send("That user is not yet ranked")
            else:
                embed = discord.Embed(
                    description=f"```py\n{ctx.author.name} is currently on level {str(result[2])} and has {str(result[1])} XP\nXP needed for next level: {int(result[2])*200 - int(result[1])}```")
                await ctx.send(embed=embed)
    @commands.command()
    async def rank_help(self, ctx):
        """: Rank help
        """
        embed = discord.Embed(description=f"""  :keyboard:  Be active in the server to gain XP. :keyboard: \n```py\nLevel 1: Just Typed Hello World!\nLevel 5: Active Coder(You get a new role)\nLevel 10: Server Sensei(You get a new role)\nLevel 20: Orz```""")
        await ctx.send(embed=embed)

    @commands.command()
    async def rank_list(self, ctx):
        """: Displays top 10 Active Members in the server
        """
        db = psycopg2.connect(creds)
        cursor = db.cursor()

        sql = "SELECT lvl,xp,user_id FROM levels WHERE guild_id = %s"
        val = (str(ctx.guild.id),)
        cursor.execute(sql, val)
        res = cursor.fetchall()

        mess = "Top 10 members:\n"
        mess += "{: <5} {: <8} {: <8} {: <10}\n".format("Rank", "Level", "Exp", "User")
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
            mess += "{: <5} {: <8} {: <8} {: <10}\n".format(x, ele[0], ele[1], name_user)
            x += 1
        await ctx.send(f"```py\n{mess}```")

def setup(client):
    client.add_cog(Level(client))