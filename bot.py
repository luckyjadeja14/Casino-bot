import discord
from discord.ext import commands
import random
import os
# import dotenv # Not strictly needed if token is only in Replit Secrets
# from dotenv import load_dotenv # Not strictly needed

# For Replit Uptime with UptimeRobot
from flask import Flask
from threading import Thread

# --- Configuration ---
# load_dotenv() # Only if you were testing locally with a .env file
BOT_TOKEN = os.getenv("DISCORD_TOKEN") # Reads from Replit Secrets
COMMAND_PREFIX = "!"
INITIAL_COINS = 1000
SHELL_PAYOUT_MULTIPLIER = 2.8

SHELL_EMOJI = "🏺"
PRIZE_EMOJI = "🪙"
EMPTY_EMOJI = "💨"

# --- Flask App for Uptime ---
# This small web server will be pinged by UptimeRobot to keep the Repl alive.
uptime_app = Flask('')

@uptime_app.route('/')
def home():
    return "Bot is alive!" # Simple response for UptimeRobot

def run_web_server():
  # Runs the Flask app on host 0.0.0.0 (accessible from outside) and port 8080 (common Replit port)
  uptime_app.run(host='0.0.0.0', port=8080)

def keep_alive_server(): # Renamed to avoid conflict if you have another 'keep_alive'
    """Starts the Flask web server in a separate thread."""
    web_thread = Thread(target=run_web_server)
    web_thread.start()
# --- End Flask App Section ---


# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # If you plan to use member join events, etc.

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# --- Data Storage (In-Memory - For production, use a database!) ---
user_balances = {}
active_shell_games = {}

# --- Helper Functions ---
async def get_balance(user_id: int) -> int:
    if user_id not in user_balances:
        user_balances[user_id] = INITIAL_COINS
    return user_balances[user_id]

async def update_balance(user_id: int, amount: int):
    current_balance = await get_balance(user_id)
    user_balances[user_id] = current_balance + amount
    return user_balances[user_id]

# --- Bot Events ---
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print(f"Command Prefix: {COMMAND_PREFIX}")
    if not BOT_TOKEN:
        print("CRITICAL ERROR: DISCORD_TOKEN is not set in Replit Secrets!")
        print("Please go to Tools > Secrets and add your DISCORD_TOKEN.")
        # Optionally, you could stop the bot here if the token is critical
        # await bot.close() # Uncomment if you want the bot to stop if token is missing
    else:
        print("DISCORD_TOKEN found.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Oops! You missed an argument. Usage: `{COMMAND_PREFIX}{ctx.command.name} {ctx.command.signature}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Oops! Invalid argument type. Please check the command usage.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You don't have permission to use this command or a check failed.")
    else:
        print(f"Unhandled error in command {ctx.command}: {error}")
        await ctx.send("An unexpected error occurred. Please try again later.")

# --- Game Commands (Identical to before) ---
@bot.command(name="balance", aliases=["bal", "coins"])
async def balance(ctx):
    user_id = ctx.author.id
    balance = await get_balance(user_id)
    await ctx.send(f"{ctx.author.mention}, you have {balance} {PRIZE_EMOJI} coins.")

@bot.command(name="shellgame", aliases=["sg"])
async def shell_game(ctx, bet: int):
    user_id = ctx.author.id
    if user_id in active_shell_games:
        await ctx.send("You already have an active Shell Game! Finish it first using `!choose <1, 2, or 3>`.")
        return
    if bet <= 0:
        await ctx.send("Please enter a positive bet amount.")
        return
    current_balance = await get_balance(user_id)
    if bet > current_balance:
        await ctx.send(f"You don't have enough coins! Your balance is {current_balance} {PRIZE_EMOJI}.")
        return
    await update_balance(user_id, -bet)
    winning_shell = random.randint(1, 3)
    active_shell_games[user_id] = {"bet": bet, "winning_shell": winning_shell}
    embed = discord.Embed(
        title="🐚 Shell Game Started! 🐚",
        description=f"{ctx.author.mention} has placed a bet of **{bet} {PRIZE_EMOJI}**.",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="Which shell hides the prize?",
        value=f"{SHELL_EMOJI} (1)   {SHELL_EMOJI} (2)   {SHELL_EMOJI} (3)\n\n"
              f"Use `{COMMAND_PREFIX}choose <1, 2, or 3>` to make your guess!",
        inline=False
    )
    embed.set_footer(text="Good luck!")
    await ctx.send(embed=embed)

@bot.command(name="choose")
async def choose_shell(ctx, choice: int):
    user_id = ctx.author.id
    if user_id not in active_shell_games:
        await ctx.send("You don't have an active Shell Game. Start one with `!shellgame <bet>`.")
        return
    if not (1 <= choice <= 3):
        await ctx.send("Invalid choice. Please choose shell 1, 2, or 3.")
        return
    game_data = active_shell_games.pop(user_id)
    bet_amount = game_data["bet"]
    winning_shell_number = game_data["winning_shell"]
    shells_display_list = [EMPTY_EMOJI] * 3
    shells_display_list[winning_shell_number - 1] = PRIZE_EMOJI
    
    final_shells_text_parts = []
    for i in range(3):
        current_shell_num = i + 1
        display_char = shells_display_list[i]
        if current_shell_num == choice:
            if choice == winning_shell_number:
                final_shells_text_parts.append(f"**[{PRIZE_EMOJI}]** ({current_shell_num})")
            else:
                final_shells_text_parts.append(f"**[{EMPTY_EMOJI}]** ({current_shell_num})")
        else:
             final_shells_text_parts.append(f"[{display_char}] ({current_shell_num})")
    final_shells_text = "   ".join(final_shells_text_parts)

    embed = discord.Embed(title="🐚 Shell Game Result! 🐚", color=discord.Color.blue())
    embed.add_field(name="Your Choice & The Outcome", value=final_shells_text, inline=False)

    if choice == winning_shell_number:
        winnings = int(bet_amount * SHELL_PAYOUT_MULTIPLIER)
        await update_balance(user_id, winnings)
        embed.description = f"Congratulations {ctx.author.mention}! You chose shell #{choice} and found the {PRIZE_EMOJI}!"
        embed.add_field(name="You Won!", value=f"**{winnings - bet_amount} {PRIZE_EMOJI}** (Total Payout: {winnings} {PRIZE_EMOJI})", inline=False)
        embed.color = discord.Color.green()
    else:
        embed.description = f"Oh no {ctx.author.mention}! You chose shell #{choice}, but the {PRIZE_EMOJI} was under shell #{winning_shell_number}."
        embed.add_field(name="You Lost!", value=f"**{bet_amount} {PRIZE_EMOJI}**", inline=False)
        embed.color = discord.Color.red()
    current_balance = await get_balance(user_id)
    embed.set_footer(text=f"Your new balance: {current_balance} {PRIZE_EMOJI}")
    await ctx.send(embed=embed)

# --- Admin/Debug Commands (Optional) ---
@bot.command(name="addcoins")
@commands.is_owner()
async def add_coins(ctx, member: discord.Member, amount: int):
    await update_balance(member.id, amount)
    await ctx.send(f"Added {amount} {PRIZE_EMOJI} to {member.mention}. New balance: {await get_balance(member.id)} {PRIZE_EMOJI}.")

@add_coins.error
async def add_coins_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("Sorry, only the bot owner can use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!addcoins @User <amount>`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid user or amount. Usage: `!addcoins @User <amount>`")

# --- Run the Bot and Keep Alive Server ---
if __name__ == "__main__":
    if BOT_TOKEN:
        keep_alive_server() # Start the Flask web server in a separate thread
        bot.run(BOT_TOKEN)  # Start the Discord bot
    else:
        print("CRITICAL ERROR: DISCORD_TOKEN environment variable not found in Replit Secrets.")
        print("The bot will not start. Please go to Tools > Secrets (padlock icon) and add your DISCORD_TOKEN.")