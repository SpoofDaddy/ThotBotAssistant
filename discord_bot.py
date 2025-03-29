import os
import discord
from discord.ext import commands
import asyncio
import random
import logging
from dotenv import load_dotenv

# Import local modules
from config import PREFIX, COLORS, STATUS_MESSAGES, CURRENT_PERSONALITY, ENABLE_MEMORY, ENABLE_USER_RECOGNITION, ENABLE_WELCOME_MESSAGES
from responses import PERSONALITY_RESPONSES, PERSONALITY_TYPES, DEFAULT_PERSONALITY
from simp_tracker import SimpTracker
from memory_system import memory_system

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
# Enable privileged intents for welcome messages
intents.message_content = True
intents.members = True  # Required for the on_member_join event

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

async def simulate_typing(ctx, min_time=1.0, max_time=3.0):
    """Simulates typing to make the bot feel more realistic."""
    typing_time = random.uniform(min_time, max_time)
    async with ctx.typing():
        await asyncio.sleep(typing_time)

@bot.command(name="flirt")
async def flirt(ctx):
    """Cherry sends a flirty message to the user based on current personality."""
    await simulate_typing(ctx)
    
    # Track the user's flirt interaction
    simp_tracker.increment_score(str(ctx.author.id))
    
    # Record this interaction in Cherry's memory if enabled
    if ENABLE_MEMORY:
        memory_system.record_command(str(ctx.author.id), "flirt")
        memory_system.record_interaction(str(ctx.author.id), "flirt")
    
    # Get response based on current personality
    personality = CURRENT_PERSONALITY
    if personality not in PERSONALITY_RESPONSES:
        personality = "flirty"  # Default fallback
    
    flirt_response = random.choice(PERSONALITY_RESPONSES[personality]["flirt"])
    personality_color = PERSONALITY_TYPES[personality]["color"]
    
    # If memory is enabled, maybe include a memory reference (30% chance)
    if ENABLE_MEMORY and random.random() < 0.3:
        memory_reference = memory_system.generate_memory_reference(str(ctx.author.id), personality)
        if memory_reference:
            flirt_response = f"{memory_reference}\n\n{flirt_response}"
    
    # Convert hex color to RGB tuple
    color_hex = personality_color.lstrip('#')
    color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    
    embed = discord.Embed(
        description=flirt_response,
        color=discord.Color.from_rgb(*color_rgb if len(color_rgb) == 3 else COLORS['pink'])
    )
    
    # Add personality indicator to the author name
    personality_emoji = "🍒"
    if personality == "tsundere":
        personality_emoji = "😤"
    elif personality == "wholesome":
        personality_emoji = "💖"
    elif personality == "spicy":
        personality_emoji = "🔥"
    elif personality == "gamer":
        personality_emoji = "🎮"
    
    embed.set_author(
        name=f"Cherry {personality_emoji} [{PERSONALITY_TYPES[personality]['name']}]", 
        icon_url=bot.user.avatar.url if bot.user.avatar else None
    )
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
    
    # Record this interaction in Cherry's memory if enabled
    if ENABLE_MEMORY:
        memory_system.record_command(str(ctx.author.id), "compliment", 
                                   {"target_id": str(target_user.id)} if user else None)
        memory_system.record_interaction(str(ctx.author.id), "compliment", 
                                       str(target_user.id) if user else None)
    
    # Get response based on current personality
    personality = CURRENT_PERSONALITY
    if personality not in PERSONALITY_RESPONSES:
        personality = "flirty"  # Default fallback
    
    compliment = random.choice(PERSONALITY_RESPONSES[personality]["compliment"])
    personality_color = PERSONALITY_TYPES[personality]["color"]
    
    # If memory is enabled and targeting self, maybe include a memory reference (20% chance)
    if ENABLE_MEMORY and target_user.id == ctx.author.id and random.random() < 0.2:
        memory_reference = memory_system.generate_memory_reference(str(ctx.author.id), personality)
        if memory_reference:
            compliment = f"{memory_reference}\n\n{compliment}"
    
    # Convert hex color to RGB tuple
    color_hex = personality_color.lstrip('#')
    color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    
    embed = discord.Embed(
        description=f"{target_user.mention}, {compliment}",
        color=discord.Color.from_rgb(*color_rgb if len(color_rgb) == 3 else COLORS['purple'])
    )
    
    # Add personality indicator to the author name
    personality_emoji = "🍒"
    if personality == "tsundere":
        personality_emoji = "😤"
    elif personality == "wholesome":
        personality_emoji = "💖"
    elif personality == "spicy":
        personality_emoji = "🔥"
    elif personality == "gamer":
        personality_emoji = "🎮"
    
    embed.set_author(
        name=f"Cherry {personality_emoji} [{PERSONALITY_TYPES[personality]['name']}]", 
        icon_url=bot.user.avatar.url if bot.user.avatar else None
    )
    
    await ctx.send(embed=embed)

@bot.command(name="simp")
async def simp_score(ctx, user: discord.Member = None):
    """Displays the simp score for a user."""
    await simulate_typing(ctx, min_time=0.5, max_time=1.5)
    
    # If no user is mentioned, show the command user's score
    target_user = user if user else ctx.author
    user_id = str(target_user.id)
    
    # Record this command in Cherry's memory if enabled
    if ENABLE_MEMORY:
        memory_system.record_command(str(ctx.author.id), "simp", 
                                   {"target_id": str(target_user.id)} if user else None)
    
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

# Roleplay commands
@bot.command(name="hug")
async def hug(ctx, user: discord.Member = None):
    """Cherry hugs the mentioned user or the command user if no one is mentioned."""
    await simulate_typing(ctx)
    
    # If no user is mentioned, hug the command user
    target_user = user if user else ctx.author
    
    # Track the interaction if self-requested
    if target_user.id == ctx.author.id:
        simp_tracker.increment_score(str(ctx.author.id))
    
    # Record this interaction in Cherry's memory if enabled
    if ENABLE_MEMORY:
        memory_system.record_command(str(ctx.author.id), "hug", 
                                   {"target_id": str(target_user.id)} if user else None)
        memory_system.record_interaction(str(ctx.author.id), "hug", 
                                       str(target_user.id) if user else None)
    
    # Get response based on current personality
    personality = CURRENT_PERSONALITY
    if personality not in PERSONALITY_RESPONSES:
        personality = "flirty"  # Default fallback
    
    hug_response = random.choice(PERSONALITY_RESPONSES[personality]["hug"])
    personality_color = PERSONALITY_TYPES[personality]["color"]
    
    # If memory is enabled and this is a self-hug, maybe include a memory reference (15% chance)
    if ENABLE_MEMORY and target_user.id == ctx.author.id and random.random() < 0.15:
        memory_reference = memory_system.generate_memory_reference(str(ctx.author.id), personality)
        if memory_reference:
            hug_response = f"{memory_reference}\n\n{hug_response}"
    
    # Convert hex color to RGB tuple
    color_hex = personality_color.lstrip('#')
    color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    
    embed = discord.Embed(
        description=f"{target_user.mention}, {hug_response}",
        color=discord.Color.from_rgb(*color_rgb if len(color_rgb) == 3 else COLORS['pink'])
    )
    
    # Add personality indicator to the author name
    personality_emoji = "🍒"
    if personality == "tsundere":
        personality_emoji = "😤"
    elif personality == "wholesome":
        personality_emoji = "💖"
    elif personality == "spicy":
        personality_emoji = "🔥"
    elif personality == "gamer":
        personality_emoji = "🎮"
    
    embed.set_author(
        name=f"Cherry {personality_emoji} [{PERSONALITY_TYPES[personality]['name']}]", 
        icon_url=bot.user.avatar.url if bot.user.avatar else None
    )
    
    await ctx.send(embed=embed)

@bot.command(name="kiss")
async def kiss(ctx, user: discord.Member = None):
    """Cherry kisses the mentioned user or the command user if no one is mentioned."""
    await simulate_typing(ctx)
    
    # If no user is mentioned, kiss the command user
    target_user = user if user else ctx.author
    
    # Track the interaction if self-requested
    if target_user.id == ctx.author.id:
        simp_tracker.increment_score(str(ctx.author.id))
    
    # Record this interaction in Cherry's memory if enabled
    if ENABLE_MEMORY:
        memory_system.record_command(str(ctx.author.id), "kiss", 
                                   {"target_id": str(target_user.id)} if user else None)
        memory_system.record_interaction(str(ctx.author.id), "kiss", 
                                       str(target_user.id) if user else None)
    
    # Get response based on current personality
    personality = CURRENT_PERSONALITY
    if personality not in PERSONALITY_RESPONSES:
        personality = "flirty"  # Default fallback
    
    kiss_response = random.choice(PERSONALITY_RESPONSES[personality]["kiss"])
    personality_color = PERSONALITY_TYPES[personality]["color"]
    
    # If memory is enabled and this is a self-kiss, maybe include a memory reference (20% chance)
    if ENABLE_MEMORY and target_user.id == ctx.author.id and random.random() < 0.2:
        memory_reference = memory_system.generate_memory_reference(str(ctx.author.id), personality)
        if memory_reference:
            kiss_response = f"{memory_reference}\n\n{kiss_response}"
    
    # Convert hex color to RGB tuple
    color_hex = personality_color.lstrip('#')
    color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    
    embed = discord.Embed(
        description=f"{target_user.mention}, {kiss_response}",
        color=discord.Color.from_rgb(*color_rgb if len(color_rgb) == 3 else COLORS['purple'])
    )
    
    # Add personality indicator to the author name
    personality_emoji = "🍒"
    if personality == "tsundere":
        personality_emoji = "😤"
    elif personality == "wholesome":
        personality_emoji = "💖"
    elif personality == "spicy":
        personality_emoji = "🔥"
    elif personality == "gamer":
        personality_emoji = "🎮"
    
    embed.set_author(
        name=f"Cherry {personality_emoji} [{PERSONALITY_TYPES[personality]['name']}]", 
        icon_url=bot.user.avatar.url if bot.user.avatar else None
    )
    
    await ctx.send(embed=embed)

@bot.command(name="pat")
async def pat(ctx, user: discord.Member = None):
    """Cherry pats the mentioned user or the command user if no one is mentioned."""
    await simulate_typing(ctx)
    
    # If no user is mentioned, pat the command user
    target_user = user if user else ctx.author
    
    # Track the interaction if self-requested
    if target_user.id == ctx.author.id:
        simp_tracker.increment_score(str(ctx.author.id))
    
    # Record this interaction in Cherry's memory if enabled
    if ENABLE_MEMORY:
        memory_system.record_command(str(ctx.author.id), "pat", 
                                   {"target_id": str(target_user.id)} if user else None)
        memory_system.record_interaction(str(ctx.author.id), "pat", 
                                       str(target_user.id) if user else None)
    
    # Get response based on current personality
    personality = CURRENT_PERSONALITY
    if personality not in PERSONALITY_RESPONSES:
        personality = "flirty"  # Default fallback
    
    pat_response = random.choice(PERSONALITY_RESPONSES[personality]["pat"])
    personality_color = PERSONALITY_TYPES[personality]["color"]
    
    # If memory is enabled and this is a self-pat, maybe include a memory reference (10% chance)
    if ENABLE_MEMORY and target_user.id == ctx.author.id and random.random() < 0.1:
        memory_reference = memory_system.generate_memory_reference(str(ctx.author.id), personality)
        if memory_reference:
            pat_response = f"{memory_reference}\n\n{pat_response}"
    
    # Convert hex color to RGB tuple
    color_hex = personality_color.lstrip('#')
    color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    
    embed = discord.Embed(
        description=f"{target_user.mention}, {pat_response}",
        color=discord.Color.from_rgb(*color_rgb if len(color_rgb) == 3 else COLORS['blue'])
    )
    
    # Add personality indicator to the author name
    personality_emoji = "🍒"
    if personality == "tsundere":
        personality_emoji = "😤"
    elif personality == "wholesome":
        personality_emoji = "💖"
    elif personality == "spicy":
        personality_emoji = "🔥"
    elif personality == "gamer":
        personality_emoji = "🎮"
    
    embed.set_author(
        name=f"Cherry {personality_emoji} [{PERSONALITY_TYPES[personality]['name']}]", 
        icon_url=bot.user.avatar.url if bot.user.avatar else None
    )
    
    await ctx.send(embed=embed)

@bot.command(name="nickname")
async def nickname(ctx, user: discord.Member = None):
    """Cherry gives you or the target user a personality-based nickname."""
    await simulate_typing(ctx)
    
    # If no target is specified, use the command caller
    if user is None:
        user = ctx.author
    
    # Increment simp score if user is requesting a nickname for themselves
    if user.id == ctx.author.id:
        simp_tracker.increment_score(str(ctx.author.id))
    
    # Record this interaction in Cherry's memory if enabled
    if ENABLE_MEMORY:
        memory_system.record_command(str(ctx.author.id), "nickname", 
                                   {"target_id": str(user.id) if user else None})
        
        # If this is a self-nickname, record it as a self-interaction
        if user.id == ctx.author.id:
            memory_system.record_interaction(str(ctx.author.id), "nickname")
    
    # Get the personality and appropriate nickname
    personality = CURRENT_PERSONALITY
    if personality not in PERSONALITY_RESPONSES:
        personality = "flirty"  # Default fallback
    
    nickname = get_random_nickname(str(user.id))
    
    # Store the nickname in memory system if enabled
    if ENABLE_MEMORY:
        memory_system.record_preference(str(user.id), "nickname", nickname)
    
    # Create response message based on who is getting the nickname
    if user.id == ctx.author.id:
        response = f"I think I'll call you **{nickname}** from now on~ 💕"
    else:
        response = f"I'm going to call {user.mention} **{nickname}** from now on~ 💕"
    
    # Get personality-specific color
    personality_color = PERSONALITY_TYPES[personality]["color"]
    
    # Convert hex color to RGB tuple
    color_hex = personality_color.lstrip('#')
    color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    
    embed = discord.Embed(
        description=response,
        color=discord.Color.from_rgb(*color_rgb if len(color_rgb) == 3 else COLORS['pink'])
    )
    
    # Add personality indicator to the author name
    personality_emoji = "🍒"
    if personality == "tsundere":
        personality_emoji = "😤"
    elif personality == "wholesome":
        personality_emoji = "💖"
    elif personality == "spicy":
        personality_emoji = "🔥"
    elif personality == "gamer":
        personality_emoji = "🎮"
    
    embed.set_author(
        name=f"Cherry {personality_emoji} [{PERSONALITY_TYPES[personality]['name']}]", 
        icon_url=bot.user.avatar.url if bot.user.avatar else None
    )
    
    await ctx.send(embed=embed)

@bot.command(name="helpme")
async def help_command(ctx):
    """Displays all available commands."""
    await simulate_typing(ctx, min_time=0.5, max_time=1.5)
    
    # Record this command in Cherry's memory if enabled
    if ENABLE_MEMORY:
        memory_system.record_command(str(ctx.author.id), "helpme")
    
    # Get color based on current personality
    personality = CURRENT_PERSONALITY
    if personality not in PERSONALITY_TYPES:
        personality = "flirty"  # Default fallback
    
    personality_color = PERSONALITY_TYPES[personality]["color"]
    
    # Convert hex color to RGB tuple
    color_hex = personality_color.lstrip('#')
    color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    
    # Customize description based on personality
    description = f"Here's how you can interact with me, cutie:"
    if personality == "tsundere":
        description = f"Fine, I'll tell you how to use my commands... Not that I care if you use them!"
    elif personality == "wholesome":
        description = f"I'm so happy to share these wonderful ways we can interact!"
    elif personality == "spicy":
        description = f"Here are the commands you can use with me... Use them wisely, or not so wisely~"
    elif personality == "gamer":
        description = f"Ready Player One! Here are the commands in your control scheme:"
    
    embed = discord.Embed(
        title="Cherry's Commands 💝",
        description=description,
        color=discord.Color.from_rgb(*color_rgb if len(color_rgb) == 3 else COLORS['pink'])
    )
    
    # Add personality indicator to the author name
    personality_emoji = "🍒"
    if personality == "tsundere":
        personality_emoji = "😤"
    elif personality == "wholesome":
        personality_emoji = "💖"
    elif personality == "spicy":
        personality_emoji = "🔥"
    elif personality == "gamer":
        personality_emoji = "🎮"
    
    embed.set_author(
        name=f"Cherry {personality_emoji} [{PERSONALITY_TYPES[personality]['name']}]", 
        icon_url=bot.user.avatar.url if bot.user.avatar else None
    )
    
    commands = [
        (f"{PREFIX}flirt", "I'll send you a flirty message 💋"),
        (f"{PREFIX}compliment [@user]", "I'll compliment you or someone you mention 💖"),
        (f"{PREFIX}hug [@user]", "I'll give you or someone you mention a hug 🤗"),
        (f"{PREFIX}kiss [@user]", "I'll kiss you or someone you mention 😘"),
        (f"{PREFIX}pat [@user]", "I'll pat you or someone you mention 👐"),
        (f"{PREFIX}nickname [@user]", "I'll give you or someone else a cute nickname 💕"),
        (f"{PREFIX}simp [@user]", "Check how much you or someone else has been simping for me 😘"),
        (f"{PREFIX}helpme", "Shows this help message 💌")
    ]
    
    # Add info about personality
    embed.add_field(
        name="Current Personality",
        value=f"I'm currently in **{PERSONALITY_TYPES[personality]['name']}** mode: {PERSONALITY_TYPES[personality]['description']}",
        inline=False
    )
    
    # Categorize commands
    interaction_commands = [(f"{PREFIX}flirt", "I'll send you a flirty message 💋"),
                           (f"{PREFIX}compliment [@user]", "I'll compliment you or someone you mention 💖"),
                           (f"{PREFIX}nickname [@user]", "I'll give you or someone else a cute nickname 💕")]
    
    roleplay_commands = [(f"{PREFIX}hug [@user]", "I'll give you or someone you mention a hug 🤗"),
                        (f"{PREFIX}kiss [@user]", "I'll kiss you or someone you mention 😘"),
                        (f"{PREFIX}pat [@user]", "I'll pat you or someone you mention 👐")]
    
    utility_commands = [(f"{PREFIX}simp [@user]", "Check how much you or someone else has been simping for me 😘"),
                       (f"{PREFIX}helpme", "Shows this help message 💌")]
    
    # Add fields for categorized commands
    embed.add_field(
        name="💬 Basic Commands",
        value="\n".join([f"**{cmd}** - {desc}" for cmd, desc in interaction_commands]), 
        inline=False
    )
    
    embed.add_field(
        name="💕 Roleplay Commands",
        value="\n".join([f"**{cmd}** - {desc}" for cmd, desc in roleplay_commands]), 
        inline=False
    )
    
    embed.add_field(
        name="🔧 Utility Commands",
        value="\n".join([f"**{cmd}** - {desc}" for cmd, desc in utility_commands]), 
        inline=False
    )
    
    # Add memory system info if enabled
    if ENABLE_MEMORY:
        memory_info = "I remember our interactions! Sometimes I might recall things we've done together. 💭"
        
        if personality == "tsundere":
            memory_info = "I-it's not like I'm keeping track of our interactions or anything... but I might remember stuff we did."
        elif personality == "wholesome":
            memory_info = "I treasure the memories of our time together and may recall our lovely moments! 💕"
        elif personality == "spicy":
            memory_info = "I never forget the... interesting things we've done together. I might bring them up when you least expect it~ 😏"
        elif personality == "gamer":
            memory_info = "Achievement unlocked: Memory System! I'm saving our gameplay highlights for future reference!"
        
        user_memory_count = memory_system.get_memory_count(str(ctx.author.id))
        if user_memory_count > 0:
            memory_info += f"\n\nI have **{user_memory_count}** memories of us together so far!"
        
        embed.add_field(
            name="🧠 Memory System",
            value=memory_info,
            inline=False
        )
    
    # Customize footer based on personality
    footer_text = "More commands coming soon... Stay tuned! 💕"
    if personality == "tsundere":
        footer_text = "Not that I'm adding more commands just for you or anything... baka!"
    elif personality == "wholesome":
        footer_text = "More wonderful ways to connect coming soon! You're amazing! 💖"
    elif personality == "spicy":
        footer_text = "I've got some special commands planned just for you... 😏"
    elif personality == "gamer":
        footer_text = "New command DLC dropping soon! No microtransactions required!"
    
    embed.set_footer(text=footer_text)
    
    await ctx.send(embed=embed)

@bot.event
async def on_member_join(member):
    """Send a welcome message when a new member joins the server."""
    # Skip if welcome messages are disabled
    if not ENABLE_WELCOME_MESSAGES:
        return
        
    try:
        logger.info(f"New member joined: {member.name}#{member.discriminator} ({member.id})")
        
        # Get a welcome channel to send the message in
        welcome_channel = None
        
        # Try to find a channel with "welcome" in the name
        for channel in member.guild.text_channels:
            if "welcome" in channel.name.lower():
                welcome_channel = channel
                break
        
        # If no specific welcome channel, use the first text channel or system channel
        if not welcome_channel:
            welcome_channel = member.guild.system_channel or member.guild.text_channels[0]
        
        if welcome_channel:
            # Get response based on current personality
            personality = CURRENT_PERSONALITY
            if personality not in PERSONALITY_RESPONSES:
                personality = "flirty"  # Default fallback
            
            welcome_response = random.choice(PERSONALITY_RESPONSES[personality]["welcome"])
            personality_color = PERSONALITY_TYPES[personality]["color"]
            
            # Convert hex color to RGB tuple
            color_hex = personality_color.lstrip('#')
            color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            
            embed = discord.Embed(
                description=f"{member.mention}, {welcome_response}",
                color=discord.Color.from_rgb(*color_rgb if len(color_rgb) == 3 else COLORS['pink'])
            )
            
            # Add personality indicator to the author name
            personality_emoji = "🍒"
            if personality == "tsundere":
                personality_emoji = "😤"
            elif personality == "wholesome":
                personality_emoji = "💖"
            elif personality == "spicy":
                personality_emoji = "🔥"
            elif personality == "gamer":
                personality_emoji = "🎮"
            
            embed.set_author(
                name=f"Cherry {personality_emoji} [{PERSONALITY_TYPES[personality]['name']}]", 
                icon_url=bot.user.avatar.url if bot.user.avatar else None
            )
            
            # Add a footer with available commands
            embed.set_footer(text=f"Type {PREFIX}helpme to see what I can do!")
            
            # Record this in memory if enabled
            if ENABLE_MEMORY:
                memory_system.record_interaction(str(member.id), "joined_server")
            
            await welcome_channel.send(embed=embed)
            logger.info(f"Sent welcome message to {member.name} in {welcome_channel.name}")
    except Exception as e:
        logger.error(f"Error sending welcome message: {e}")

# Helper functions for nickname system
def get_random_nickname(user_id=None):
    """
    Returns a random nickname for the user based on the current personality.
    
    Args:
        user_id (str, optional): The Discord user ID to potentially retrieve a stored nickname
                                 or generate a consistent nickname for.
                                 
    Returns:
        str: A random nickname from the current personality's nickname list
    """
    personality = get_current_personality()
    
    # If memory system is enabled and user_id is provided, we could check if the user
    # already has a stored nickname
    if ENABLE_MEMORY and user_id and memory_system.has_memory_about(user_id, "nickname"):
        latest_nickname_memory = memory_system.get_latest_memory(user_id, "preference")
        if latest_nickname_memory and "content" in latest_nickname_memory:
            return latest_nickname_memory["content"]
    
    # Get nickname list for the current personality
    nickname_list = PERSONALITY_RESPONSES.get(personality, {}).get("nicknames", [])
    
    # Default to flirty nicknames if the current personality doesn't have nicknames
    if not nickname_list:
        nickname_list = PERSONALITY_RESPONSES.get("flirty", {}).get("nicknames", ["cutie"])
    
    # If user_id is provided, we can use it to seed the random generator
    # for consistent nicknames per user
    if user_id:
        # Create a random generator seeded with the user_id
        # This ensures the same user gets the same nickname within a personality
        rng = random.Random(int(user_id) % 10000 + hash(personality) % 10000)
        return rng.choice(nickname_list)
    
    # Otherwise just return a completely random nickname
    return random.choice(nickname_list)

def get_current_personality():
    """
    Returns the current personality of Cherry.
    This is mainly used to ensure fresh data when checking the personality
    since environment variables are cached.
    """
    # Reload from .env file to ensure we have the latest value
    load_dotenv()
    default_personality = "flirty"  # Fallback in case DEFAULT_PERSONALITY is not available
    return os.environ.get("CURRENT_PERSONALITY", default_personality)

def run_bot():
    """Start the bot"""
    bot.run(TOKEN)

if __name__ == "__main__":
    run_bot()