import discord
from discord import utils
from discord.ext import commands
import os

talkHere = {}
my_secret = os.environ['TOKEN']
bot = commands.Bot(os.environ['PREFIX'])
prefix = os.environ['PREFIX']

@bot.command()
async def talk(ctx):
    if ctx.channel not in talkHere:
        talkHere[ctx.channel] = True
    elif talkHere[ctx.channel]:
        talkHere[ctx.channel] = False
    elif not talkHere[ctx.channel]:
        talkHere[ctx.channel] = True

@bot.command()
async def first(ctx):
    await ctx.send("put the first command here")

@bot.command()
async def second(ctx):
    await ctx.send("this is where the second one goes")

@bot.command()
async def third(ctx):
    await ctx.send("and finally the third command")

@bot.event
async def on_message(message):
    if not message.author == bot.user:
        if message.content.startswith(prefix):
            await bot.process_commands(message)
        else:
            try:
                if talkHere[message.channel]:
                    await message.channel.send("we received a message that isnt a command, just a regular message. Check it:\n"+message.content)
            except KeyError:
                print("talk command first")


@bot.event
async def on_ready():
    print("{} locked n loaded".format(bot))


def main():
    pass


if __name__ == '__main__':
    main()

bot.run(my_secret)
