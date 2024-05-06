import os  # Import the OS library to access environment variables
import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

# Define intents
intents = discord.Intents.default()

# Retrieve the bot token from the environment variable
bot_token = os.getenv("secrets.LAYCHPA_BOT_TOKEN")

# Ensure the bot token is available
if not bot_token:
    raise ValueError("Bot token is not set in environment variables.")

# Create the bot with the command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

def test_example_function():
    assert True  # This is a simple test

def scrape_quest_guide(quest_name):
    # Format quest name to match URL format
    formatted_quest_name = quest_name.lower().replace(' ', '-').replace('’', '').replace('é', 'e').replace('à', 'a')
    website_url = f'https://papycha.fr/quete-{formatted_quest_name}/'
    response = requests.get(website_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the relevant content from the website
    quest_guide_content = soup.find('div', class_='entry-content')
    if quest_guide_content:
        # Extract text content and image URLs
        text_content = quest_guide_content.text.strip()
        image_tags = quest_guide_content.find_all('img')
        image_urls = [tag['src'] for tag in image_tags]

        return text_content, image_urls
    else:
        return None, None

def scrape_chemin_guide(chemin_name):
    # Format chemin name to match URL format
    formatted_chemin_name = chemin_name.lower().replace(' ', '-').replace('’', '').replace('é', 'e').replace('à', 'a')
    website_url = f'https://papycha.fr/chemin-{formatted_chemin_name}/'
    response = requests.get(website_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the relevant content from the website
    chemin_guide_content = soup.find('div', class_='entry-content')
    if chemin_guide_content:
        # Extract text content and image URLs
        text_content = chemin_guide_content.text.strip()
        image_tags = chemin_guide_content.find_all('img')
        image_urls = [tag['src'] for tag in image tags]

        return text_content, image_urls
    else:
        return None, None

@bot.command()
async def quest(ctx, *, quest_name):
    text_content, image_urls = scrape_quest_guide(quest_name)
    if text_content:
        # Send text content first
        chunks = [text_content[i:i+1900] for i in range(0, len(text_content), 1900)]
        for chunk in chunks:
            await ctx.send(chunk)

        # Send images afterward
        for image_url in image_urls:
            await ctx.send(image_url)
    else:
        await ctx.send(f"Quest guide for '{quest_name}' not found on the Papycha website.")

@bot.command()
async def chemin(ctx, *, chemin_name):
    text_content, image_urls = scrape_chemin_guide(chemin_name)
    if text_content:
        # Send text content first
        chunks = [text_content[i:i+1900) for i in range(0, len(text_content), 1900)]
        for chunk in chunks:
            await ctx.send(chunk)

        # Send images afterward
        for image_url in image_urls:
            await ctx.send(image_url)
    else:
        await ctx.send(f"Chemin guide for '{chemin_name}' not found on the Papycha website.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Start the bot using the token from the environment variable
bot.run(bot_token)
