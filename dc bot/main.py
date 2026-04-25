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
        self.turn = p1.id
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

            # turn check
            if interaction.user.id != self.turn:
                await interaction.response.send_message("not your turn", ephemeral=True)
                return

            if self.board[i] != " ":
                return

            # mark
            mark = "❌" if interaction.user.id == self.p1.id else "🟢"
            self.board[i] = mark
            btn.label = mark
            btn.disabled = True

            # MUST defer button interactions (prevents 10062)
            try:
                await interaction.response.defer()
            except:
                return

            # win check
            if self.check_win(mark):
                self.game_over = True
                for item in self.children:
                    item.disabled = True

                try:
                    await interaction.edit_original_response(
                        content=f"{interaction.user.mention} wins",
                        view=self
                    )
                except:
                    pass
                return

            # draw check
            if self.check_draw():
                self.game_over = True
                for item in self.children:
                    item.disabled = True

                try:
                    await interaction.edit_original_response(
                        content="draw",
                        view=self
                    )
                except:
                    pass
                return

            # swap turn
            self.turn = self.p2.id if self.turn == self.p1.id else self.p1.id

            try:
                await interaction.edit_original_response(
                    content=f"{self.p1.mention} vs {self.p2.mention} | turn: <@{self.turn}>",
                    view=self
                )
            except:
                pass

        btn.callback = callback
        return btn


# ---------------- COMMAND ----------------

@tree.command(name="tictactoe", description="play vs another player")
@app_commands.describe(user="who you want to fight")
@discord.app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
async def ttt(interaction: discord.Interaction, user: discord.User):

    if user.id == interaction.user.id:
        await interaction.response.send_message("you can't fight yourself", ephemeral=True)
        return

    view = TicTacToePvP(interaction.user, user)

    # IMPORTANT: respond immediately (no defer)
    await interaction.response.send_message(
        f"tictactoe: {interaction.user.mention} vs {user.mention}\n{interaction.user.mention} starts",
        view=view
    )


wins = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock"
}


class RPSView(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=120)
        self.p1 = p1
        self.p2 = p2
        self.picks = {}
        self.done = False

    def resolve(self):
        a = self.picks[self.p1.id]
        b = self.picks[self.p2.id]

        if a == b:
            return "draw"

        if wins[a] == b:
            return f"{self.p1.mention} wins"
        return f"{self.p2.mention} wins"

    async def finish(self, interaction: discord.Interaction, result: str):
        self.done = True

        for item in self.children:
            item.disabled = True

        try:
            await interaction.edit_original_response(
                content=f"rps finished: {result}",
                view=self
            )
            return
        except:
            pass

        try:
            await interaction.followup.send(
                f"rps finished: {result}"
            )
        except:
            pass

    async def handle_pick(self, interaction: discord.Interaction, pick: str):
        if self.done:
            return

        if interaction.user.id not in (self.p1.id, self.p2.id):
            await interaction.response.send_message("not your game", ephemeral=True)
            return

        if interaction.user.id in self.picks:
            await interaction.response.send_message("already picked", ephemeral=True)
            return

        self.picks[interaction.user.id] = pick

        await interaction.response.send_message(f"you picked {pick}", ephemeral=True)

        if len(self.picks) < 2:
            return

        result = self.resolve()
        await self.finish(interaction, result)

    @discord.ui.button(label="rock", style=discord.ButtonStyle.secondary)
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_pick(interaction, "rock")

    @discord.ui.button(label="paper", style=discord.ButtonStyle.secondary)
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_pick(interaction, "paper")

    @discord.ui.button(label="scissors", style=discord.ButtonStyle.secondary)
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_pick(interaction, "scissors")


# ---------------- COMMAND ----------------

@tree.command(name="rps", description="1v1 rock paper scissors")
@app_commands.describe(user="who you want to fight")
@discord.app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
async def rps(interaction: discord.Interaction, user: discord.User):

    if user.id == interaction.user.id:
        await interaction.response.send_message("you can't fight yourself", ephemeral=True)
        return

    view = RPSView(interaction.user, user)

    await interaction.response.send_message(
        f"rps match: {interaction.user.mention} vs {user.mention}\nboth pick your move",
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