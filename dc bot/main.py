import os
import platform
import psutil
import time
import discord
from discord import app_commands
import random

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

start_time = time.time()

@client.event
async def on_ready():
    await tree.sync()
    print(f"logged in as {client.user}")
    synced = await tree.sync()
    print(f"synced {len(synced)} commands globally")



class TicTacToe(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.board = [" "] * 9
        self.game_over = False

        for i in range(9):
            self.add_item(self.make_button(i))

    def check_win(self, p):
        wins = [
            (0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)
        ]
        return any(self.board[a] == self.board[b] == self.board[c] == p for a,b,c in wins)

    def check_draw(self):
        return " " not in self.board

    def end_game(self):
        self.game_over = True
        for item in self.children:
            item.disabled = True

    def make_button(self, i):
        btn = discord.ui.Button(
            label="⬜",
            style=discord.ButtonStyle.secondary,
            row=i // 3
        )

        async def callback(interaction: discord.Interaction):
            if self.game_over:
                return

            if self.board[i] != " ":
                return

            # user move
            self.board[i] = "X"
            btn.label = "❌"
            btn.disabled = True

            await interaction.response.defer()

            if self.check_win("X"):
                self.end_game()
                await interaction.edit_original_response(content="you win", view=self)
                return

            if self.check_draw():
                self.end_game()
                await interaction.edit_original_response(content="draw", view=self)
                return

            # bot move
            empty = [x for x, v in enumerate(self.board) if v == " "]
            if empty:
                m = random.choice(empty)
                self.board[m] = "O"
                self.children[m].label = "🟢"
                self.children[m].disabled = True

            if self.check_win("O"):
                self.end_game()
                await interaction.edit_original_response(content="bot wins", view=self)
                return

            if self.check_draw():
                self.end_game()
                await interaction.edit_original_response(content="draw", view=self)
                return

            await interaction.edit_original_response(content="your turn", view=self)

        btn.callback = callback
        return btn


@tree.command(name="tictactoe", description="play vs bot")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ttt(interaction: discord.Interaction):
    await interaction.response.send_message(
        "your turn",
        view=TicTacToe()
    )



@tree.command(name="pc", description="shows pc stats")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def pc(interaction: discord.Interaction):
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    uptime = int(time.time() - start_time)

    msg = (
        f"cpu: {cpu}%\n"
        f"ram: {ram.percent}% ({ram.used // 1024 // 1024} mb)\n"
        f"disk: {disk.percent}%\n"
        f"uptime: {uptime}s\n"
        f"hostname: {platform.node()}\n"
        f"os: {platform.system()} {platform.release()}\n"
        f"arch: {platform.machine()}"
    )

    await interaction.response.send_message(f"```{msg}```")

client.run(TOKEN)