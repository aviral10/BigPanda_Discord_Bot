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

class tags(commands.Cog):

    def __init__(self, client):
        self.client = client
    @commands.command()
    @commands.has_any_role("Admin", "masterPanda", "Active Coder")
    async def add_tag(self, ctx, *,arg):
        """: Add a custom tag for the bot: /add_tag <tagname>"""
        author = ctx.author
        db = psycopg2.connect(creds)
        cursor = db.cursor()
        sql = (f"SELECT user_id FROM tags WHERE guild_id = %s and name = %s")
        val = (str(ctx.guild.id), str(arg).lower())
        cursor.execute(sql, val)
        rr = cursor.fetchone()
        if rr is None:
            def check(m):
                return m.author == author
            try:
                await ctx.send("Enter tag contents or prefix the message with NO to cancel: ")
                a = await self.client.wait_for('message', check=check, timeout=60)
                content = str(a.content)
                if content[:2] != "NO":
                    sql = ("INSERT INTO tags(data,guild_id,user_id,name) VALUES (%s,%s,%s,%s)")
                    val = (str(a.content),str(ctx.guild.id), str(ctx.author.id), str(arg))
                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                    await ctx.send("Tag successfully created!")
                else:
                    await ctx.send('Tag Cancelled', delete_after=3.0)
                    cursor.close()
                    db.close()
                    return
            except asyncio.TimeoutError:
                cursor.close()
                db.close()
                return await ctx.send('Sorry, you took too long')
        else:
            cursor.close()
            db.close()
            await ctx.send("Tag already exists Use update instead")



    @commands.command()
    @commands.has_any_role("Admin", "masterPanda", "Active Coder")
    async def update_tag(self, ctx, *, arg):
        """: Update an existing tag: /update_tag <tagname>"""
        author = ctx.author
        name = str(arg)

        db = psycopg2.connect(creds)
        cursor = db.cursor()
        sql = (f"SELECT name,user_id,data FROM tags WHERE guild_id = %s and name = %s")
        val = (str(ctx.guild.id), str(arg).lower())
        cursor.execute(sql, val)
        result = cursor.fetchone()
        if result is None:
            await ctx.send("Tag does not exist", delete_after=3.0)
        else:
            def check(m):
                return m.author == author
            try:
                await ctx.send("Enter new data or prefix the message with NO to cancel: ")
                a = await self.client.wait_for('message', check=check, timeout=60)
                content = str(a.content)
                if content[:2] != "NO":
                    db = psycopg2.connect(creds)
                    cursor = db.cursor()
                    sql = (f"UPDATE tags SET data = %s WHERE guild_id = %s and name = %s")
                    val = (content, str(ctx.guild.id), name)
                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                    await ctx.send("Tag successfully updated!")
                else:
                    await ctx.send('Tag Cancelled', delete_after=3.0)
                    return
            except asyncio.TimeoutError:
                return await ctx.send('Sorry, you took too long')

    @commands.command()
    @commands.has_any_role("Admin", "masterPanda")
    async def del_tag(self, ctx, *, arg):
        """: Delete an existing tag: /del_tag <tagname>"""
        db = psycopg2.connect(creds)
        cursor = db.cursor()
        sql = (f"SELECT user_id,data FROM tags WHERE guild_id = %s and name = %s")
        val = (str(ctx.guild.id), str(arg).lower())
        cursor.execute(sql, val)
        result = cursor.fetchone()
        if result is not None:
            sql = (f"DELETE FROM tags WHERE data = %s and guild_id = %s")
            val = (str(result[1]),str(ctx.guild.id))
            cursor.execute(sql, val)
            await ctx.send("Tag successfully deleted!")
            db.commit()
        else:
            await ctx.send("No tags found")
        cursor.close()
        db.close()

    @commands.command()
    async def tag(self, ctx, *, arg):
        """: Call a tag: /tag <tagname>"""
        db = psycopg2.connect(creds)
        cursor = db.cursor()
        sql = (f"SELECT name,data FROM tags WHERE guild_id = %s and name = %s")
        val = (str(ctx.guild.id), str(arg).lower())
        cursor.execute(sql, val)
        result = cursor.fetchone()
        if result is not None:
            await ctx.send(f"{result[1]}")
        else:
            await ctx.send("No tags found")
        cursor.close()
        db.close()

    @commands.command()
    async def list_tags(self, ctx):
        """: Display the list of tags: /list_tags"""
        db = psycopg2.connect(creds)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tags")
        items = cursor.fetchall()
        mess = ""
        i = 1
        for ele in items:
            mess+= f"{i}: {ele[1]}\n"
            i+=1

        await ctx.send(f"```py\nCall as:\n/tag <name>\n{mess}```")
        cursor.close()
        db.close()


def setup(client):
    client.add_cog(tags(client))