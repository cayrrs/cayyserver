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
        self.board = [" "]*9
        self.current = "X"

    def check_win(self, p):
        wins = [
            (0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)
        ]
        return any(self.board[a]==self.board[b]==self.board[c]==p for a,b,c in wins)

    def check_draw(self):
        return " " not in self.board

    async def bot_move(self, interaction):
        empty = [i for i,v in enumerate(self.board) if v==" "]
        if not empty:
            return
        move = random.choice(empty)
        self.board[move] = "O"
        self.children[move].label = "O"
        self.children[move].disabled = True

    async def update(self, interaction):
        if self.check_win("X"):
            self.disable_all_items()
            await interaction.response.edit_message(content="you win", view=self)
            return
        if self.check_win("O"):
            self.disable_all_items()
            await interaction.response.edit_message(content="bot wins", view=self)
            return
        if self.check_draw():
            self.disable_all_items()
            await interaction.response.edit_message(content="draw", view=self)
            return

        await self.bot_move(interaction)

        if self.check_win("O"):
            self.disable_all_items()
            await interaction.response.edit_message(content="bot wins", view=self)
            return
        if self.check_draw():
            self.disable_all_items()
            await interaction.response.edit_message(content="draw", view=self)
            return

        await interaction.response.edit_message(content="your turn", view=self)


for i in range(9):
    async def callback(interaction, i=i):
        view: TicTacToe = interaction.message.components[0].view

    def make_button(i):
        async def cb(interaction: discord.Interaction):
            view: TicTacToe = interaction.message._view
            if view.board[i] != " ":
                return
            view.board[i] = "X"
            btn = view.children[i]
            btn.label = "X"
            btn.disabled = True
            await view.update(interaction)
        return cb

    btn = discord.ui.Button(label=" ", style=discord.ButtonStyle.secondary)
    btn.callback = make_button(i)
    TicTacToe.add_item(btn)


@tree.command(name="tictactoe", description="play tic tac toe vs bot")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def tictactoe(interaction: discord.Interaction):
    view = TicTacToe()
    await interaction.response.send_message("your turn", view=view)



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