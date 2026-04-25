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



wins = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]

class TicTacToePvP(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=120)
        self.board = [" "] * 9
        self.p1 = p1
        self.p2 = p2
        self.turn = p1.id  # p1 starts as X
        self.game_over = False

        for i in range(9):
            self.add_item(self.make_button(i))

    def check_win(self, mark):
        return any(
            self.board[a] == self.board[b] == self.board[c] == mark
            for a, b, c in wins
        )

    def check_draw(self):
        return " " not in self.board

    def make_button(self, i):
        btn = discord.ui.Button(
            label="⬜",
            style=discord.ButtonStyle.secondary,
            row=i // 3
        )

        async def callback(interaction: discord.Interaction):
            if self.game_over:
                return

            if interaction.user.id != self.turn:
                await interaction.response.send_message("not your turn", ephemeral=True)
                return

            if self.board[i] != " ":
                return

            mark = "❌" if interaction.user.id == self.p1.id else "🟢"
            self.board[i] = mark

            btn.label = mark
            btn.disabled = True

            await interaction.response.defer()

            # win check
            if self.check_win(mark):
                self.game_over = True
                for item in self.children:
                    item.disabled = True

                winner = interaction.user.mention
                await interaction.edit_original_response(
                    content=f"{winner} wins",
                    view=self
                )
                return

            # draw check
            if self.check_draw():
                self.game_over = True
                for item in self.children:
                    item.disabled = True

                await interaction.edit_original_response(
                    content="draw",
                    view=self
                )
                return

            # swap turns
            self.turn = self.p2.id if self.turn == self.p1.id else self.p1.id

            await interaction.edit_original_response(
                content=f"{self.p1.mention} vs {self.p2.mention} | turn: <@{self.turn}>",
                view=self
            )

        btn.callback = callback
        return btn


@tree.command(name="tictactoe", description="play vs another player")
@app_commands.describe(user="who you want to fight")
@discord.app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
async def ttt(interaction: discord.Interaction, user: discord.User):
    if user.id == interaction.user.id:
        await interaction.response.send_message("you can't fight yourself lil bro", ephemeral=True)
        return

    view = TicTacToePvP(interaction.user, user)

    await interaction.response.send_message(
        f"tictactoe: {interaction.user.mention} vs {user.mention} | {interaction.user.mention} starts",
        view=view
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