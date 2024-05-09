import pytest
from discord.ext import commands
from main import bot  # Import your bot instance

# Example test to check if the command works
@pytest.mark.asyncio
async def test_chemin_command():
    # Simulate a command message
    from discord.ext.test import backend, test as dpytest
    await dpytest.empty_cache()  # Clear previous cache

    test_message = "!chemin Dark Vlad"  # Command you want to test
    await bot.process_commands(test_message)

    # Check if the expected response is returned
    expected_response = "Your expected response text or image URLs here"
    await dpytest.verify_message(expected_response)  # Check if this message was sent
