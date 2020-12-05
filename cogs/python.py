import discord
from discord.ext import commands
import asyncio
import os
import subprocess
import psutil
import time


class python(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.done = False

    def psolve(self, pen):
        ex = """except Exception as e:\n\ttraceback.print_exc(file=log)\n"""
        with open("cogs/p_util/t1.py", "w+") as file:

            # print(text)
            # file.write("""import traceback\nlog = open("cogs/p_util/plog.txt", "w")\n""")
            # file.write("try:\n\t")
            file.writelines(pen)
            # file.write('\n')
            # file.write(ex)
            # file.write("log.close()")

    def kill(self,proc_pid):
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()

    def code(self):
        # print("Running Python file")
        # os.system('python cogs/p_util/t1.py < cogs/p_util/pin.txt > cogs/p_util/pout.txt')
        # proc = subprocess.Popen(['python', 'cogs/p_util/t1.py', '<cogs/p_util/pin.txt', '>cogs/p_util/pout.txt'],
        #                         shell=True)
        args = ['python', 'cogs/p_util/t1.py']
        proc = subprocess.Popen(args=args, stdout=open('cogs/p_util/pout.txt', 'w'), stdin=open('cogs/p_util/pin.txt', "r"),stderr=open('cogs/p_util/plog.txt', 'w'),shell=False)
        try:
            #print("pid: ", proc.pid)
            time.sleep(1)
            poll = proc.poll()
            #print("Process still running")
            if poll == None:
                proc.wait(timeout=3)
                #print("Second dip worked")
            else:
                #print("Itt was a success")
                return 1
        except subprocess.TimeoutExpired:
            print("Killed")
            self.kill(proc.pid)
            return 0

    @commands.command()
    async def python(self, ctx, *, arg):
        """: Run Simple python codes use: /python xyz
        """
        author = ctx.author

        sarr = ["import os", "import sys", "import glob", "pathlib", "__import__", "import pip", "psutil", "shutil",
                "from os", "from sys", "from glob", "open"]

        arg = str(arg).strip()
        res = str(arg).strip()
        if res.startswith('```'):
            res = res[3:-3]
            arg = arg[3:-3]

        safe = True
        for ele in sarr:
            if ele in res:
                safe = False
                break

        if "database" in str(arg):
            me = self.client.get_user(528182299821473802)
            if ctx.author == me:
                safe = True
            else:
                safe = False

        if safe:
            if "input" in str(arg):
                await ctx.send("Provide Valid Input contents: ")

                def check(m):
                    return m.author == author

                try:
                    a = await self.client.wait_for('message', check=check, timeout=30)
                    with open("cogs/p_util/pin.txt", 'w') as inp:
                        inp.writelines(str(a.content))
                except asyncio.TimeoutError:
                    return await ctx.send('Sorry, you took too long')
            pen = str(arg)
            self.psolve(pen)


            # print("Worked till here")
            ret_code = self.code()
            if ret_code == 0:
                await ctx.send(f"`Request timed out`")
                return

            mess = """"""
            file_path_out = 'cogs/p_util/pout.txt'
            file_path_log = 'cogs/p_util/plog.txt'
            # check if size of file is 0
            if os.path.getsize(file_path_out) == 0:
                if os.path.getsize(file_path_log) == 0:
                    mess = "There is some Error in your code"
                else:
                    with open("cogs/p_util/plog.txt", "r") as f:
                        for line in f:
                            mess += line
            else:
                with open("cogs/p_util/pout.txt", "r") as f:
                    for line in f:
                        mess += line
            if len(mess) >=2000:
                mess=mess[:2000]
            if ("bot.py" in mess) or ("NzIyNjk5MzY0NjM" in mess):
                await ctx.send("Nice try!")
            else:
                embed = discord.Embed(description=f"Your Output: ```py\n{mess}```")
                embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
                # embed.set_footer(text=f'#ID: {ctx.author.id}')
                await ctx.send(embed=embed)

            file = open("cogs/p_util/pout.txt", "w")
            file.close()
            file = open("cogs/p_util/plog.txt", "w")
            file.close()
            file = open("cogs/p_util/pin.txt", "w")
            file.close()
        else:
            await ctx.send("Forbidden Commands")


def setup(client):
    client.add_cog(python(client))
