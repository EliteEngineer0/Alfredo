import os
import discord
import aiohttp
import random
from discord.ext import commands
from dotenv import load_dotenv
from util import clean_discord_message, split_and_send_messages
from gemini import generate_response_with_image_and_text, generate_response_with_text

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MAX_HISTORY = int(os.getenv("MAX_HISTORY"))
DEVELOPMENT_MODE = str.lower(str(os.getenv("DEVELOPMENT_MODE"))) == "true"
DEVELOPMENT_SERVER_ID = int(os.getenv("DEVELOPMENT_SERVER_ID"))

# Initialize Discord bot with specific intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', description="Alfredo", intents=intents)

# --------------------------------------------- Event Handlers -------------------------------------------------

@bot.event
async def on_ready():
    print(f'Gemini Bot Logged in as {bot.user}. Development mode: {DEVELOPMENT_MODE}', flush=True)

@bot.event
async def on_message(message):
    if message.author == bot.user or message.mention_everyone:
        return

    # Handle messages from the bot
    is_dm = isinstance(message.channel, discord.DMChannel)
    contains_name = "alfredo" in str.lower(message.content)
    random_trigger = random.randint(1, 10) == 1

    if bot.user.mentioned_in(message) or is_dm or contains_name or random_trigger:
        cleaned_text = clean_discord_message(message.content)
        await process_message(message, cleaned_text)

# --------------------------------------------- Message Processing -------------------------------------------------

async def process_message(message, cleaned_text):
    """Main handler for processing incoming messages."""
    async with message.channel.typing():
        if message.attachments:
            await handle_image_message(message, cleaned_text)
        else:
            await handle_text_message(message, cleaned_text)

async def handle_image_message(message, cleaned_text):
    """Processes messages that contain images."""
    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status != 200:
                        await message.channel.send('Unable to download the image.')
                        return
                    image_data = await resp.read()
                    await send_response_with_image(message, image_data, cleaned_text)

async def handle_text_message(message, cleaned_text):
    """Processes messages that contain text only."""
    history_text = await get_channel_message_history(message.channel)
    await send_text_response(message, history_text)
        
# --------------------------------------------- Channel History Retrieval -------------------------------------------------

async def get_channel_message_history(channel):
    """Retrieves the most recent messages from the channel."""
    messages = []
    async for msg in channel.history(limit=MAX_HISTORY, oldest_first=False):
        author_name = msg.author.name
        display_name = msg.author.display_name
        content = msg.clean_content if msg.clean_content else "(No Text)"
        messages.append(f"{author_name} ({display_name}): {content}")
    
    return '\n\n'.join(reversed(messages))  # Reverse the order to make the oldest message appear first.

# --------------------------------------------- Sending Responses -------------------------------------------------

async def send_text_response(message, text):
    """Sends the AI-generated text response."""
    response_text = await generate_response_with_text(text)

    if DEVELOPMENT_MODE:
        print(f"Sending to text model: {text}", flush=True)

    # cut the response if its over 100 characters
    if len(response_text) > 100:
        response_text = response_text[:100] + "..."
    await split_and_send_messages(message, response_text, 1700)

async def send_response_with_image(message, image_data, text):
    """Sends the AI-generated response based on both image and text."""
    history_text = await get_channel_message_history(message.channel)

    if DEVELOPMENT_MODE:
        print(f"Sending to image model: {text} with image attached", flush=True)

    response_text = await generate_response_with_image_and_text(image_data, history_text)
    # cut the response if its over 100 characters
    if len(response_text) > 100:
        response_text = response_text[:100] + "..."
    await split_and_send_messages(message, response_text, 1700)

# --------------------------------------------- Run Bot -------------------------------------------------

bot.run(DISCORD_TOKEN)
