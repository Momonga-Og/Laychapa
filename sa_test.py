import pytest
from discord.ext import commands
import discord.ext.test as dpytest
from main import bot  # Ensure 'bot' is the Discord bot instance from your main code

@pytest.mark.asyncio
async def test_chemin_command():
    # Initialize the test environment and clear any previous test state
    dpytest.configure(bot)  # This sets up the bot with the test environment
    await dpytest.empty_cache()  # Clears any cache from previous tests

    # Simulate a user sending a command in a Discord text channel
    test_message = "!chemin Dark Vlad"  # Command to test
    await dpytest.message(test_message)  # Simulates sending the message to the bot

    # Define the expected response (customize this with your actual expected output)
    expected_response = "Here's the info about Dark Vlad: <some text or link>"  # Modify to match your bot's response

    # Verify if the bot's response matches the expected response
    await dpytest.verify_message(expected_response)  # Check if the bot sent the expected message
