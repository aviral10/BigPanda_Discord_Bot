import discord
from discord.ext import commands
import asyncio
import psycopg2

from dotenv import load_dotenv
import os
load_dotenv()
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_pass = os.getenv("DB_PASS")
creds = f"dbname='{db_name}' user='{db_user}' host='{db_pass}' password='{db_pass}'"

class Buy(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def buy_role(self,ctx,col="ffffff",*,role_name):
        """: Buy yourself a custom role(300 bytes), customize it.
            Use:     /buy_role <color_in_hex> <name>
            example: /buy_role 3dffe5 Gay"""
        price = 300
        role_al = discord.utils.get(ctx.guild.roles, name=role_name)
        if role_al:
            if role_al not in ctx.author.roles:
                await ctx.author.add_roles(role_al)
                await ctx.send("> Updated your custom role")
            else:
                await ctx.send("> You already have a custom role")
            return
        db = psycopg2.connect(creds)
        cursor = db.cursor()
        sql = ("SELECT user_id,inbank,inhand FROM currency WHERE guild_id = %s and user_id = %s")
        val = (str(ctx.guild.id), str(ctx.author.id))
        cursor.execute(sql, val)
        result_acc = cursor.fetchone()
        if result_acc is None:
            await ctx.send("> You are not yet registered.")
            cursor.close()
            db.close()
            return
        else:
            if int(result_acc[1]) <= price:
                await ctx.send(f"> You don't have enough bytes to buy a custom role. A custom role costs: `{price} bytes`")
                cursor.close()
                db.close()
                return

        sql = ("SELECT * FROM customrole WHERE guild_id = %s and user_id = %s")
        val = (str(ctx.guild.id), str(ctx.author.id))
        cursor.execute(sql, val)
        result = cursor.fetchone()
        if result is None:

            guild = ctx.guild
            if col.startswith("#"):
                col = col[1:]
            await guild.create_role(name=role_name, colour=discord.Colour(int(col, 16)))
            await ctx.send("> Role Successfully Created")
            role_new = discord.utils.get(ctx.guild.roles, name=role_name)
            await ctx.author.add_roles(role_new)

            sql = ("INSERT INTO customrole(guild_id,user_id,role) VALUES(%s,%s,%s)")
            val = (str(ctx.guild.id), str(ctx.author.id), role_name)
            cursor.execute(sql, val)
            db.commit()

            sql = ("UPDATE currency SET inbank = %s WHERE guild_id = %s and user_id = %s")
            val = (str(int(result_acc[1]) - price), str(ctx.guild.id), str(ctx.author.id))
            cursor.execute(sql, val)
            db.commit()
        else:
            #print("Found")
            await ctx.send("> Seems your role was deleted from the server, i'm reassigning you the role")
            guild = ctx.guild
            if col.startswith("#"):
                col = col[1:]
            await guild.create_role(name=str(role_name), colour=discord.Colour(int(col, 16)))
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            await ctx.author.add_roles(role)
        cursor.close()
        db.close()


    @commands.command()
    async def update_role(self, ctx, col, *, new_name=None):
        """: Customize your role name: /update_role <to>
            example: /update_role 3dffe5 Not Gay (if you just want to change the color, leave the name field blank)"""
        if new_name == None:
            db = psycopg2.connect(creds)
            cursor = db.cursor()
            sql = ("SELECT role FROM customrole WHERE guild_id = %s and user_id = %s")
            val = (str(ctx.guild.id), str(ctx.author.id))
            cursor.execute(sql, val)
            result_acc = cursor.fetchone()
            if result_acc is None:
                await ctx.send(f"> You don't have a custom role")
            else:
                role_h = discord.utils.get(ctx.guild.roles, name=result_acc[0])
                await role_h.edit(color=discord.Colour(int(col, 16)), reason="User request")
                await ctx.send(f"Role updated successfully")
            cursor.close()
            db.close()
            return
        role_al = discord.utils.get(ctx.guild.roles, name=new_name)
        if role_al:
            await ctx.send(f"> You cannot rename your role to that")
            return
        if col.startswith("#"):
            col = col[1:]
        db = psycopg2.connect(creds)
        cursor = db.cursor()
        sql = ("SELECT role FROM customrole WHERE guild_id = %s and user_id = %s")
        val = (str(ctx.guild.id), str(ctx.author.id))
        cursor.execute(sql, val)
        result_acc = cursor.fetchone()
        if result_acc is None:
            await ctx.send(f"> You don't have a custom role")
        else:
            role_h = discord.utils.get(ctx.guild.roles, name=result_acc[0])
            if role_h:
                try:
                    role_h = discord.utils.get(ctx.guild.roles, name=result_acc[0])
                    await role_h.edit(color=discord.Colour(int(col, 16)), name=new_name, reason="User request")
                    sql = ("UPDATE customrole SET role = %s WHERE guild_id = %s and user_id = %s")
                    val = (str(new_name), str(ctx.guild.id), str(ctx.author.id))
                    cursor.execute(sql, val)
                    db.commit()
                    await ctx.send("> Successfully updated your role.")
                except discord.Forbidden:
                    await ctx.send("> Missing Permissions Cannot rename your role")
            else:
                await ctx.send("Had some error")
        cursor.close()
        db.close()


def setup(client):
    client.add_cog(Buy(client))