import os
import discord
from discord.ext import commands
import asyncio
import random
import logging
from dotenv import load_dotenv

# Import local modules
from config import PREFIX, COLORS, STATUS_MESSAGES
from responses import FLIRT_RESPONSES, COMPLIMENT_RESPONSES
from simp_tracker import SimpTracker

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cherry')

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error("No Discord token found. Please add your token to the .env file.")
    exit(1)

# Setup bot with command prefix
intents = discord.Intents.default()
# Disable privileged intents if they're not enabled in the Developer Portal
# intents.message_content = True
# intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
simp_tracker = SimpTracker()

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    logger.info(f'🍒 Cherry is online! Connected as {bot.user.name}')
    
    # Set initial status
    activity = discord.Game(name=random.choice(STATUS_MESSAGES))
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    # Rotate status messages every 30 minutes
    bot.loop.create_task(rotate_status())

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors gracefully."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Hmm, I don't know that command, cutie~ Try `{PREFIX}helpme` to see what I can do 💖")
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(f"Oopsie! Something went wrong 😳 {error}")

async def rotate_status():
    """Rotates the bot's status message periodically."""
    while True:
        await asyncio.sleep(1800)  # 30 minutes
        activity = discord.Game(name=random.choice(STATUS_MESSAGES))
        await bot.change_presence(status=discord.Status.online, activity=activity)

async def simulate_typing(ctx, min_time=1, max_time=3):
    """Simulates typing to make the bot feel more realistic."""
    typing_time = random.uniform(min_time, max_time)
    async with ctx.typing():
        await asyncio.sleep(typing_time)

@bot.command(name="flirt")
async def flirt(ctx):
    """Cherry sends a flirty message to the user."""
    await simulate_typing(ctx)
    
    # Track the user's flirt interaction
    simp_tracker.increment_score(str(ctx.author.id))
    
    embed = discord.Embed(
        description=random.choice(FLIRT_RESPONSES),
        color=discord.Color.from_rgb(*COLORS['pink'])
    )
    embed.set_author(name="Cherry 🍒", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text=f"Use {PREFIX}simp to see your simp score")
    
    await ctx.send(embed=embed)

@bot.command(name="compliment")
async def compliment(ctx, user: discord.Member = None):
    """Cherry compliments the mentioned user or the command user if no one is mentioned."""
    await simulate_typing(ctx)
    
    # If no user is mentioned, compliment the command user
    target_user = user if user else ctx.author
    
    # Track the interaction if self-requested
    if target_user.id == ctx.author.id:
        simp_tracker.increment_score(str(ctx.author.id))
    
    compliment = random.choice(COMPLIMENT_RESPONSES)
    
    embed = discord.Embed(
        description=f"{target_user.mention}, {compliment}",
        color=discord.Color.from_rgb(*COLORS['purple'])
    )
    embed.set_author(name="Cherry 🍒", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    
    await ctx.send(embed=embed)

@bot.command(name="simp")
async def simp_score(ctx, user: discord.Member = None):
    """Displays the simp score for a user."""
    await simulate_typing(ctx, min_time=0.5, max_time=1.5)
    
    # If no user is mentioned, show the command user's score
    target_user = user if user else ctx.author
    user_id = str(target_user.id)
    
    score = simp_tracker.get_score(user_id)
    
    # Determine the title based on the score
    if score == 0:
        title = "Not simping yet!"
        color = COLORS['blue']
    elif score < 5:
        title = "Casual Admirer"
        color = COLORS['blue']
    elif score < 15:
        title = "Devoted Fan"
        color = COLORS['purple']
    elif score < 30:
        title = "Cherry's Favorite"
        color = COLORS['pink']
    else:
        title = "Ultimate Simp Lord"
        color = COLORS['red']
    
    embed = discord.Embed(
        title=title,
        description=f"{target_user.mention} has a simp score of **{score}**",
        color=discord.Color.from_rgb(*color)
    )
    embed.set_author(name="Cherry's Simp Tracker 📊", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    
    if target_user.id == ctx.author.id and score > 0:
        embed.set_footer(text="Keep flirting to increase your score! 💕")
    
    await ctx.send(embed=embed)

@bot.command(name="helpme")
async def help_command(ctx):
    """Displays all available commands."""
    await simulate_typing(ctx, min_time=0.5, max_time=1.5)
    
    embed = discord.Embed(
        title="Cherry's Commands 💝",
        description=f"Here's how you can interact with me, cutie:",
        color=discord.Color.from_rgb(*COLORS['pink'])
    )
    embed.set_author(name="Cherry 🍒", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    
    commands = [
        (f"{PREFIX}flirt", "I'll send you a flirty message 💋"),
        (f"{PREFIX}compliment [@user]", "I'll compliment you or someone you mention 💖"),
        (f"{PREFIX}simp [@user]", "Check how much you or someone else has been simping for me 😘"),
        (f"{PREFIX}helpme", "Shows this help message 💌")
    ]
    
    for cmd, desc in commands:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="More commands coming soon... Stay tuned! 💕")
    
    await ctx.send(embed=embed)

def run_bot():
    """Start the bot"""
    bot.run(TOKEN)

if __name__ == "__main__":
    run_bot()