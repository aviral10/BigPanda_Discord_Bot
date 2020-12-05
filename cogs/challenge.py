import discord
from discord.ext import commands
import asyncio
import os
import subprocess
import psutil
import time

class Challenge(commands.Cog):
    def __init__(self, client):
        self.client = client

    def solve(self, pen):
        ex = """except Exception as e:\n\ttraceback.print_exc(file=log)\n"""
        with open("challenge/t2.py", "w+") as file:
            text = "\n\t".join(pen)
            # print(text)
            file.write("""import traceback\nlog = open("challenge/log.txt", "w")\n""")
            file.write("try:\n\t")
            file.writelines(text)
            file.write('\n')
            file.write(ex)
            file.write("log.close()")

    def kill(self,proc_pid):
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()

    def ccode(self):
        # print("Running Python file")
        # os.system('python cogs/p_util/t1.py < cogs/p_util/pin.txt > cogs/p_util/pout.txt')
        # proc = subprocess.Popen(['python', 'cogs/p_util/t1.py', '<cogs/p_util/pin.txt', '>cogs/p_util/pout.txt'],
        #                         shell=True)
        args = ['python', 'challenge/t2.py']
        proc = subprocess.Popen(args=args, stdout=open('challenge/out.txt', 'w'), stdin=open('challenge/in.txt', "r"),shell=False)
        try:
            #print("pid: ", proc.pid)
            time.sleep(1)
            poll = proc.poll()
            #print("Process still running")
            if poll == None:
                proc.wait(timeout=3)
                print("No timeout")
                return 0
                #print("Second dip worked")
            else:
                #print("Itt was a success")
                return 1
        except subprocess.TimeoutExpired:
            print("Killed from challenge cog")
            self.kill(proc.pid)
            return 0

    @commands.Cog.listener()
    async def on_message(self, message):
        submission_channel = self.client.get_channel(736224083317882961)
        wrong_answer = self.client.get_channel(736233660008890499)
        is_only_ans = False
        if str(message.content)[0:4] == "DONT":
            return
        elif str(message.content)[0:3] == "ANS":
            is_only_ans = True

        if message.channel.id == 736223917169049630:

            response = message.content
            res = str(response)
            await message.delete()
            if res[0:3] == "```":
                response = response[3:-3]
            sarr = ["import os", "import sys", "import glob", "pathlib", "__import__", "import pip", "psutil", "shutil",
                    "from os", "from sys", "from glob"]

            safe = True
            for ele in sarr:
                if ele in res:
                    safe = False
            if safe:
                if message.author.bot:
                    return
                else:
                    mess = """"""
                    error = False
                    if is_only_ans:
                        with open("challenge/out.txt", "w") as f:
                            f.write(response[4:])
                    else:
                        pen = response.split('\n')
                        self.solve(pen)
                        # os.system('python challenge/t2.py < challenge/in.txt > challenge/out.txt')
                        ret_code = self.ccode()
                        if ret_code == 0:
                            await wrong_answer.send(f"`TLE: Request timed out`")
                            return

                        file_path_out = 'challenge/out.txt'
                        file_path_log = 'challenge/log.txt'

                        mess = """"""
                        # check if size of file is 0
                        error = False
                        if os.path.getsize(file_path_out) == 0:
                            if os.path.getsize(file_path_log) == 0:
                                mess = "TLE or probable syntax error (Couldn't generate any output)"
                            else:
                                with open("challenge/log.txt", "r") as f:
                                    word = ", line "
                                    for line in f:
                                        found = line.find(word)
                                        if found == -1:
                                            mess += line
                                        else:
                                            final = f"{line[:found + 7]} {int(line[found + 7]) - 3}{line[found + 8:]}"
                                            mess += final
                            error = True

                    cans = ""
                    cout = ""
                    with open("challenge/answers.txt", "r") as f:
                        for line in f:
                            cans += str(line).rstrip()
                    with open("challenge/out.txt", "r") as f:
                        for line in f:
                            cout += str(line).rstrip()
                    cans = cans.rstrip()
                    cout = cout.rstrip()
                    print(cout)

                    val = cans == cout
                    answer = False
                    if val:
                        mess = f"ACCEPTED"
                        answer = True
                    elif error == False:
                        mess = f"WRONG ANSWER"
                        answer = False

                    if answer:
                        if is_only_ans:
                            embed = discord.Embed(
                                description=f"```py\n{response[4:]}```\nYour Output: ```py\n{mess}```")
                        else:
                            embed = discord.Embed(
                                description=f"```py\n{message.content}```\nYour Output: ```py\n{mess}```")
                        embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
                        embed.set_footer(text=f'#ID: {message.author.id}')
                        await submission_channel.send(embed=embed)

                        participant = discord.utils.get(message.author.guild.roles, name="Participant")
                        challenge_winner = discord.utils.get(message.author.guild.roles, name="AC")

                        if challenge_winner not in message.author.roles:
                            await message.author.add_roles(challenge_winner)
                            await message.author.remove_roles(participant)

                    else:
                        embed = discord.Embed(description=f"\nYour Output: ```py\n{mess}```")
                        embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
                        embed.set_footer(text=f'#ID: {message.author.id}')
                        await wrong_answer.send(embed=embed)
                    file = open("challenge/out.txt", "w")
                    file.close()
                    file = open("challenge/log.txt", "w")
                    file.close()
            else:
                await wrong_answer.send(f"Forbidden Commands used by: {message.author}")


    @commands.command()
    # @commands.has_permissions(administrator=True)
    @commands.has_any_role("Admin", "masterPanda")
    async def addquestion(self, ctx):
        """: Admin command to add a question
        """
        def check(m):
            return m.author == ctx.author
        try:
            await ctx.send("Provide Valid Input contents: ")
            a = await self.client.wait_for('message', check=check, timeout=60)
            with open("challenge/in.txt", 'w') as inp:
                inp.writelines(str(a.content))
            await ctx.channel.purge(limit=2)
            await ctx.send("Provide valid answer to the input file: ")
            a = await self.client.wait_for('message', check=check, timeout=60)
            with open("challenge/answers.txt", 'w') as ans:
                ans.writelines(str(a.content))
            await ctx.channel.purge(limit=3)
        except asyncio.TimeoutError:
            return await ctx.send('Sorry, you took too long')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):  # Participant role.
        if payload.emoji != discord.PartialEmoji(name="🖐️"):
            return
        if payload.channel_id == 736223459809558569:
            participant = discord.utils.get(payload.member.guild.roles, name="Participant")
            challenge_winner = discord.utils.get(payload.member.guild.roles, name="AC")
            if challenge_winner in payload.member.roles:
                return
            if participant in payload.member.roles:
                await payload.member.remove_roles(participant)
            await payload.member.add_roles(participant)

def setup(client):
    client.add_cog(Challenge(client))