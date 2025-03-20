import json
from pathlib import Path
from typing import TYPE_CHECKING

from endstone import ColorFormat, Player
from endstone.command import Command, CommandSender
from endstone.form import ModalForm, ActionForm, Dropdown, TextInput

from endstone_essentials.commands.command_executor_base import CommandExecutorBase

if TYPE_CHECKING:
    from endstone_essentials import EssentialsPlugin


class EconomyCommandExecutors(CommandExecutorBase):

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if not isinstance(sender, Player):
            sender.send_error_message("This command can only be executed by a player")
            return False

        match command.name:
            case "economy":
                player_economy = self.plugin.economy[sender.name]
                function_list = ["pay", "top"]

                def on_submit(player: Player, json_str: str):
                    index = json.loads(json_str)[0]
                    match function_list[index]:
                        case "pay":
                            self.economy_pay(player)

                        case "top":
                            self.economy_top(player)

                sender.send_form(
                    ModalForm(
                        title="Economy system",
                        controls=[
                            Dropdown(label="Your economy: " + ColorFormat.GREEN + f"{player_economy}\n\n" +
                                           ColorFormat.RESET + "Select a function", options=function_list)
                        ],
                        submit_button=ColorFormat.GREEN + ColorFormat.BOLD + "OK",
                        on_submit=on_submit
                    )
                )

            case "economyadmin":
                player_name_list = [player_name for player_name in self.plugin.economy.keys()]

                def on_submit(player: Player, json_str: str):
                    index = json.loads(json_str)[0]
                    target_player_name = player_name_list[index]
                    target_player_economy = self.plugin.economy[target_player_name]
                    form = ActionForm(
                        title=f"{target_player_name}'s economy",
                        content="Economy: " + ColorFormat.GREEN + f"{target_player_economy}",
                        on_close=None
                    )
                    form.add_button("reset", on_click=self.economy_admin_reset(target_player_name, target_player_economy))
                    form.add_button("change", on_click=self.economy_admin_change(target_player_name, target_player_economy))
                    player.send_form(form)

                sender.send_form(
                    ModalForm(
                        title="Economy admin",
                        controls=[
                            Dropdown(label="Select a player", options=player_name_list)
                        ],
                        submit_button=ColorFormat.GREEN + ColorFormat.BOLD + "query",
                        on_submit=on_submit
                    )
                )

        return True

    def economy_pay(self, player: Player):
        player_name_list = []
        for player_name in self.plugin.economy.keys():
            if player_name != player.name:
                player_name_list.append(player_name)
        if len(player_name_list) == 0:
            player.send_message(ColorFormat.RED + "There are no players available for economy pay")
            return

        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)
            target_player_name = player_name_list[data[0]]
            try:
                money_to_pay = int(data[1])
            except ValueError:
                player.send_message(ColorFormat.RED + "Invalid input type")
                return
            if money_to_pay <= 0:
                player.send_message(ColorFormat.RED + "Invalid input type")
                return
            if self.plugin.economy[player.name] < money_to_pay:
                player.send_message(ColorFormat.RED + "Your economy is insufficient")
                return
            self.plugin.economy[player.name] -= money_to_pay
            self.plugin.economy[target_player_name] += money_to_pay
            self.plugin.save_economy()
            player.send_message(
                ColorFormat.GREEN + f"You have successfully paid {money_to_pay} to {target_player_name}\n" + ColorFormat.RESET +
                "Economy change: " + ColorFormat.RED + f"-{money_to_pay}\n" + ColorFormat.RESET +
                "Your economy: " + ColorFormat.GREEN + f"{self.plugin.economy[player.name]}"
            )
            if self.plugin.server.get_player(target_player_name) is not None:
                target_player = self.plugin.server.get_player(target_player_name)
                target_player.send_message(
                    ColorFormat.GREEN + f"{player.name} has paid {money_to_pay} to you" + ColorFormat.RESET +
                    "Economy change: " + ColorFormat.RED + f"+{money_to_pay}\n" + ColorFormat.RESET +
                    "Your economy: " + ColorFormat.GREEN + f"{self.plugin.economy[target_player_name]}"
                )

        player.send_form(
            ModalForm(
                title="Economy pay",
                controls=[
                    Dropdown(label="Select a online player", options=player_name_list),
                    TextInput(label="Input money to pay", placeholder="Must be a positive integer")
                ],
                submit_button=ColorFormat.GREEN + ColorFormat.BOLD + "Pay",
                on_submit=on_submit
            )
        )

    def economy_top(self, player: Player):
        temple_list = list(self.plugin.economy.items())
        temple_list.sort(key=lambda x:x[1], reverse=True)
        display_num = self.plugin.config["economy"]["display_num"]
        if len(temple_list) < display_num:
            index = len(temple_list)
        else:
            index = display_num
        content = ""
        for i in range(index):
            content += f"{temple_list[i][0]}: " + ColorFormat.GREEN + f"{temple_list[i][1]}\n" + ColorFormat.RESET
        player.send_form(
            ActionForm(
                title="Economy top",
                content=content,
                on_close=None
            )
        )

    def economy_admin_reset(self, target_player_name: str, target_player_economy: int):
        def on_click(player: Player):

            def on_submit(player: Player, json_str: str):
                data = json.loads(json_str)
                try:
                    money_to_set = int(data[0])
                except ValueError:
                    player.send_message(ColorFormat.RED + "Invalid input type")
                    return
                if money_to_set < 0:
                    player.send_message(ColorFormat.RED + "Invalid input type")
                    return
                self.plugin.economy[target_player_name] = money_to_set
                self.plugin.save_economy()
                player.send_message(ColorFormat.GREEN + f"{target_player_name}'s economy has been successfully reset")
                if self.plugin.server.get_player(target_player_name) is not None:
                    target_player = self.plugin.server.get_player(target_player_name)
                    target_player.send_message(ColorFormat.GREEN + f"Your economy has been reset to {money_to_set}")

            player.send_form(
                ModalForm(
                    title="Economy admin - reset",
                    controls=[
                        TextInput(label=f"{target_player_name}'s economy: " + ColorFormat.GREEN + f"{target_player_economy}\n\n",
                                  placeholder="Must be a positive integer or zero")
                    ],
                    submit_button=ColorFormat.GREEN + "reset",
                    on_submit=on_submit
                )
            )

        return on_click

    def economy_admin_change(self, target_player_name: str, target_player_economy: int):

        def on_click(player: Player):

            def on_submit(player: Player, json_str: str):
                data = json.loads(json_str)
                try:
                    money_to_change = int(data[0])
                except ValueError:
                    player.send_message(ColorFormat.RED + "Invalid input type")
                    return
                if money_to_change == 0:
                    player.send_message(ColorFormat.RED + "Invalid input type")
                    return
                self.plugin.economy[target_player_name] += money_to_change
                self.plugin.save_economy()
                player.send_message(ColorFormat.GREEN + f"{target_player_name}'s economy has been successfully changed")
                if self.plugin.server.get_player(target_player_name) is not None:
                    target_player = self.plugin.server.get_player(target_player_name)
                    if money_to_change < 0:
                        target_player.send_message(
                            "Economy change: " + ColorFormat.RED + f"-{abs(money_to_change)}\n" + ColorFormat.RESET +
                            "Your economy: " + ColorFormat.GREEN + f"{self.plugin.economy[target_player_name]}"
                        )
                    else:
                        target_player.send_message(
                            "Economy change: " + ColorFormat.GREEN + f"+{money_to_change}\n" + ColorFormat.RESET +
                            "Your economy: " + ColorFormat.GREEN + f"{self.plugin.economy[target_player_name]}"
                        )

            player.send_form(
                ModalForm(
                    title="Economy admin - change",
                    controls=[
                        TextInput(
                            label=f"{target_player_name}'s economy: " + ColorFormat.GREEN + f"{target_player_economy}\n\n",
                            placeholder="Must be a positive or negative integer")
                    ],
                    submit_button=ColorFormat.GREEN + "change",
                    on_submit=on_submit
                )
            )

        return on_click