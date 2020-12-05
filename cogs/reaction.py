import discord
from discord.ext import commands


class Reaction(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 615127789355663361 or message.channel.id == 757568021072969788:
            try:
                await message.add_reaction("✅")
                await message.add_reaction("❎")
            except:
                print("Error while adding reaction")

def setup(client):
    client.add_cog(Reaction(client))