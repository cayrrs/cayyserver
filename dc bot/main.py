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



tree = app_commands.CommandTree(discord.Client(intents=discord.Intents.default()))

choices = ["rock", "paper", "scissors"]

wins = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock"
}

rps_queue = []


# ---------------- QUEUE VIEW ----------------

class QueueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="queue up", style=discord.ButtonStyle.green)
    async def queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user in rps_queue:
            await interaction.response.send_message("already queued", ephemeral=True)
            return

        rps_queue.append(user)
        await interaction.response.send_message("queued", ephemeral=True)

        if len(rps_queue) >= 2:
            p1 = rps_queue.pop(0)
            p2 = rps_queue.pop(0)

            await start_match(interaction.client, p1, p2, interaction.channel)


# ---------------- GAME VIEW ----------------

class RPSView(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=120)
        self.p1 = p1
        self.p2 = p2
        self.picks = {}

    def resolve(self):
        a = self.picks[self.p1.id]
        b = self.picks[self.p2.id]

        if a == b:
            return "draw"

        if wins[a] == b:
            return f"{self.p1.mention} wins"
        return f"{self.p2.mention} wins"

    async def handle_pick(self, interaction, pick):
        if interaction.user.id not in (self.p1.id, self.p2.id):
            await interaction.response.send_message("not your match", ephemeral=True)
            return

        if interaction.user.id in self.picks:
            await interaction.response.send_message("already picked", ephemeral=True)
            return

        self.picks[interaction.user.id] = pick
        await interaction.response.send_message(f"picked {pick}", ephemeral=True)

        if len(self.picks) == 2:
            result = self.resolve()

            for item in self.children:
                item.disabled = True

            await interaction.message.edit(
                content=f"rps finished: {result}",
                view=self
            )

    @discord.ui.button(label="rock", style=discord.ButtonStyle.secondary)
    async def rock(self, interaction, button):
        await self.handle_pick(interaction, "rock")

    @discord.ui.button(label="paper", style=discord.ButtonStyle.secondary)
    async def paper(self, interaction, button):
        await self.handle_pick(interaction, "paper")

    @discord.ui.button(label="scissors", style=discord.ButtonStyle.secondary)
    async def scissors(self, interaction, button):
        await self.handle_pick(interaction, "scissors")


# ---------------- MATCH START ----------------

async def start_match(client, p1, p2, channel):
    view = RPSView(p1, p2)

    await channel.send(
        f"rps match: {p1.mention} vs {p2.mention}",
        view=view
    )


# ---------------- QUEUE COMMAND ----------------

@tree.command(name="rps-queue", description="join rps queue")
@discord.app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
async def rps_queue_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="rps queue",
        description="click to join queue",
        color=0x00ff00
    )

    await interaction.response.send_message(embed=embed, view=QueueView())


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