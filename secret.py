import discord
from discord.ext import commands, tasks

TOKEN = "YourToken"
CHANNEL_ID = "YourChannelID"
FILE_NAME = "messages.txt"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_file_for_messages.start()


@tasks.loop(seconds=5)
async def check_file_for_messages():
    with open(FILE_NAME, 'r') as f:
        message = f.read()

    if message.strip():
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(message.strip())

        # Clear the file after sending the message
        with open(FILE_NAME, 'w') as f:
            f.write("")



bot.run(TOKEN)
