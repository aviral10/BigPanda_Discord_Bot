import discord
from discord.ext import commands
import math
from datetime import datetime
import random
import psycopg2

hellos = ['Howdy!', 'Hey there', 'Aloha', 'Bonjour', 'Hi']
class Welcome(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel = self.client.get_channel(614871520275333122)
        introduce_channel = self.client.get_channel(615225545285697544)
        roles_channel = self.client.get_channel(729985706050584596)
        rules_channel = self.client.get_channel(614876987466711050)
        guild = self.client.get_guild(614871520275333120)
        mems = guild.member_count
        await welcome_channel.send(
            f"""{random.choice(hellos)}! {member.mention} welcome to the server, introduce yourself in the {introduce_channel.mention} channel and later pick up your desired roles from {roles_channel.mention}\n\nRead {rules_channel.mention} and Explore the rest. Welcome aboard!\n\nMember Count: {mems}""")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        welcome_channel = self.client.get_channel(614871520275333122)
        await welcome_channel.send(f"{member.name} has left the server.")


def setup(client):
    client.add_cog(Welcome(client))