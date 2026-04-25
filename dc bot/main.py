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

        for i in range(9):
            self.add_item(self.make_button(i))

    def make_button(self, i):
        btn = discord.ui.Button(
            label="⬜",   # IMPORTANT: must exist
            style=discord.ButtonStyle.secondary,
            row=i // 3
        )

        async def callback(interaction: discord.Interaction):
            if self.board[i] != " ":
                return

            self.board[i] = "X"
            btn.label = "❌"
            btn.disabled = True

            # bot move
            empty = [x for x, v in enumerate(self.board) if v == " "]
            if empty:
                m = random.choice(empty)
                self.board[m] = "O"
                self.children[m].label = "🟢"
                self.children[m].disabled = True

            await interaction.response.edit_message(view=self)

        btn.callback = callback
        return btn


@tree.command(name="tictactoe", description="play vs bot")
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