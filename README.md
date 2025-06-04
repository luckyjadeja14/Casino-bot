# Discord Casino Bot - Shell Game

A simple Discord bot featuring a Shell Game where users can bet virtual coins.
This bot is designed to be hosted on a platform where the `DISCORD_TOKEN` is set as an environment variable.

## Features

-   **Shell Game (`!shellgame` or `!sg`):** Bet coins and try to find the prize under one of three shells.
-   **Balance Check (`!balance` or `!bal`):** Check your current coin balance.
-   **Coin Economy:** Users start with initial coins. (Data is in-memory and will be lost on bot restart).
-   **(Admin) Add Coins (`!addcoins`):** Bot owner can add coins to users.

## Setup on Hosting Platform (e.g., Replit, Railway, Heroku, VPS)

1.  **Fork/Clone this Repository** to your hosting platform or directly connect your GitHub account.
2.  **Set Environment Variables:**
    *   You **MUST** set the `DISCORD_TOKEN` environment variable on your hosting platform. This is your Discord Bot Token.
3.  **Install Dependencies:** The hosting platform should automatically install dependencies from `requirements.txt` (which mainly includes `discord.py`).
4.  **Run Command:** The platform should be configured to run `python bot.py`.

## Commands

-   `!shellgame <bet_amount>` or `!sg <bet_amount>`: Starts a Shell Game.
    -   Example: `!sg 100`
-   `!choose <1|2|3>`: Makes your choice in an active Shell Game.
    -   Example: `!choose 2`
-   `!balance` or `!bal`: Shows your current coin balance.
-   `!addcoins @User <amount>`: (Bot Owner Only) Adds coins to a user.

## Important Notes

-   **DISCORD_TOKEN:** This bot reads the token from an environment variable named `DISCORD_TOKEN`. **DO NOT hardcode your token in `bot.py` or commit it to GitHub.**
-   **Data Persistence:** This bot uses in-memory storage for user balances and game states. This means **all data will be lost if the bot restarts.** For a production bot, you should integrate a database.
