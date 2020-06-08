import discord
import os
from mcstatus import MinecraftServer
from dotenv import load_dotenv
load_dotenv()
prefix = "mc!"

import redis
r = redis.Redis(host='localhost', port=6379, db=0,  decode_responses=True)
# ⓿❶❷❸❹❺❻❼❽❾❿

SECRET_KEY = os.getenv("DISCORD_TOKEN")
client = discord.Client()

def checkStatus(guildId):
    mcip=r.hget("server:" + str(guildId), "mcip")
    embed = discord.Embed(
        title=str(mcip) + " status",
        description="Server is offline :c",
        color=discord.Color.red()
    )
    if mcip == None:
        embed.title = None
        embed.color = discord.Color.blue()
        embed.description = None
        embed.add_field(name="Set your server ip first using:", value=str(prefix+" setip *YOUR_SERVER_IP*"), inline=False)
        return embed
    server = MinecraftServer.lookup(mcip)

    try:
        status = server.status(retries=1)
        embed.color = discord.Color.green()
        embed.description = "Server online!"
        embed.add_field(name="Players", value=str(status.players.online) + " / " + str(status.players.max))
        embed.add_field(name="Ping", value=str(status.latency).split('.')[0] + " ms")
        embed.add_field(name="Mc version", value=str(status.version.name), inline=False)
        # message = "> **IP:** " + str(mcip) + "\n"
        # message += "> **Players:** " + str(status.players.online) + " / " + str(status.players.max)+ "\n"
        # message += "> **Ping:** " + str(status.latency) + " ms"+ "\n"
        return embed

        # return "{0}  has {1} players and replied in {2} ms".format(mcip, status.players.online, status.latency)
    except:

        return embed



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    game = discord.Game(prefix + " help")
    await client.change_presence(status=discord.Status.idle, activity=game)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # if role in user.roles:
    #     await bot.say("{} is not muted".format(user))
    if message.content.startswith(prefix):
        rawMessage = message.content[len(prefix):].lower()
        words = rawMessage.split()
        if len(words) > 0:
            if words[0] == "setip":
                permissions = message.author.permissions_in(message.channel)
                adminPerm = 0x00000008
                if (permissions.value & adminPerm) != adminPerm:
                    await message.channel.send(message.author.mention + ' You need to be admin to use this command. Ask your admin to set up bot')
                elif len(words) == 1:
                    await message.channel.send(message.author.mention + ' You need to provide ip like: "' + prefix+' setip *IP_OF_YOUR_SERVER*"')
                    await message.channel.send(message.author.mention + ' Type: "' + prefix +' help" for more info' )
                else:
                    ip = words[1]
                    guildId = message.channel.guild.id
                    r.hset('server:' + str(guildId), 'mcip', ip)
                    await message.channel.send(message.author.mention + " Ip was set to: " + "**" + ip + "**")
            elif words[0] == "status":
                await message.channel.send(embed=checkStatus(message.channel.guild.id))
            elif words[0] == "help":
                embed = discord.Embed(
                    title="List of commands",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Start with seting your minecraft server ip using (command only for admins):",
                                value=str(prefix + " setip *YOUR_SERVER_IP*"),
                                inline=False)
                embed.add_field(name="Then, anytime you want to check your Minecraft server status, simply type:",
                                value=str(prefix + " status"),
                                inline=False)
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Command was not recognised",
                    color=discord.Color.blue(),
                    description="Here are all comands that you can use"

                )
                embed.add_field(name="Start with seting your minecraft server ip using (command only for admins):",
                                value=str(prefix + " setip *YOUR_SERVER_IP*"),
                                inline=False)
                embed.add_field(name="Then, anytime you want to check your Minecraft server status, simply type:",
                                value=str(prefix + " status"),
                                inline=False)
                await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Command was not recognised",
                color=discord.Color.blue(),
                description="Here are all comands that you can use"
                )
            embed.add_field(name="Start with seting your minecraft server ip using (command only for admins):",
                                value=str(prefix + " setip *YOUR_SERVER_IP*"),
                                inline=False)
            embed.add_field(name="Then, anytime you want to check your Minecraft server status, simply type:",
                                value=str(prefix + " status"),
                                inline=False)
            await message.channel.send(embed=embed)

client.run(SECRET_KEY)