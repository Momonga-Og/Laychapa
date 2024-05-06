import pytest
import discord
from discord.ext import commands
from discord.ext.test import backend, test as dpytest
from main import bot, scrape_chemin_guide

@pytest.mark.asyncio
async def test_chemin_command():
    # Initialize the Discord test environment
    await dpytest.empty_cache()  # Ensure a clean environment

    # Create a test context with the mock bot
    test_message = "!chemin Dark Vlad"  # Command you want to test
    await bot.process_commands(discord.Message(content=test_message, author=None, channel=None))

    # Check if the response is as expected
    # Assuming scrape_chemin_guide returns text_content and image_urls
    text_content, image_urls = scrape_chemin_guide("Dark Vlad")

    # Check if a message containing text content is sent
    if text_content:
        chunks = [text_content[i:i+1900] for i in range(0, len(text_content), 1900)]
        for chunk in chunks:
            await dpytest.verify_message(chunk)  # Check if the chunk was sent

    # Check if messages with image URLs are sent
    if image_urls:
        for image_url in image_urls:
            await dpytest.verify_message(image_url)  # Check if the image URL was sent
