import sys
from typing import Final
import os
import discord
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response
from discord import FFmpegPCMAudio, VoiceChannel
import asyncio
import datetime

#Step #0: Load token from somewhere safe
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

#Step #1: Bot Setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

#Step #2: Message Functionality
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private == True else await message.channel.send(response)
    except Exception as e:
        print(e)

#Step #3: Handling Startup
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running')

# Step #4: Handling Incoming Messages
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content.lower()  # Lowercase for easier comparison
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')

    if message.content.lower() == "!reload" and message.author.id == 472916051802324992:
        await message.channel.send("Bot is restarting...")
        await client.close()  # Disconnects the bot from Discord
        sys.exit(0)
    
    # Check if the user typed "spirit" and join the voice channel to play one bell chime
    if user_message == 'spirit':
        guild = message.guild
        voice_channel = message.author.voice.channel if message.author.voice else None
        
        if voice_channel is not None:
            await message.channel.send('Showing the American Spirit! o7')
            await join_and_play_bells(voice_channel, 2)  # Play 1 bell chime
        else:
            await message.channel.send('You need to be in a voice channel to display your alligance to the flag.')
    else:
        await send_message(message, user_message)




#Join VC Logic
# Path to your bell sound effect (adjust based on where you store it)
BELL_SOUND = 'bell.mp3'
ANTHEM_SOUND = 'anthem.mp3'

async def join_and_play_bells(channel: VoiceChannel, num_chimes: int):
    try:
        # Connect to the voice channel
        voice_client = await channel.connect()

        # Start playing the British National Anthem
        anthem_audio = FFmpegPCMAudio(ANTHEM_SOUND)
        voice_client.play(anthem_audio)

        # Wait a bit to let the anthem play before bells start (adjust as needed)
        await asyncio.sleep(2)

        # Now play the bell chimes sequentially
        for _ in range(num_chimes):
            # Check if the anthem is still playing
            while voice_client.is_playing():
                await asyncio.sleep(1)

            # Play the bell chime sound
            bell_audio = FFmpegPCMAudio(BELL_SOUND)
            voice_client.play(bell_audio)

            # Wait for the bell sound to finish
            while voice_client.is_playing():
                await asyncio.sleep(1)

            # Short pause between chimes
            await asyncio.sleep(1)

        # Stop the anthem (if still playing) and disconnect
        voice_client.stop()
        await voice_client.disconnect()

    except Exception as e:
        print(f'Error playing chimes: {e}')






async def hourly_chimes(channel: VoiceChannel):
    while True:
        now = datetime.datetime.now()
        # Calculate how many chimes based on the hour (e.g., 8 PM -> 8 chimes)
        current_hour = now.hour if now.hour <= 12 else now.hour - 12
        
        # If it's the top of the hour (minute 0), play the chimes
        if now.minute == 0:
            await join_and_play_bells(channel, current_hour)
        
        # Wait until the next minute before checking again
        await asyncio.sleep(60)

@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running')

    # Get the specific voice channel you want the bot to join (by name or ID)
    guild = client.guilds[0]  # Assuming it's the first server the bot is in
    channel = discord.utils.get(guild.voice_channels, name='General')  # Change 'General' to your voice channel

    if channel:
        # Start the hourly chimes task
        client.loop.create_task(hourly_chimes(channel))


#Step #5: Main entry point
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()