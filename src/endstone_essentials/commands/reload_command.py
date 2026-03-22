from endstone import ColorFormat
from endstone.command import Command, CommandSender

from endstone_essentials.commands.command_executor_base import CommandExecutorBase


class ReloadCommandExecutor(CommandExecutorBase):

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if len(args) == 0 or args[0] != "reload":
            return False  # return false to send usage

        sender.send_message(f"{ColorFormat.YELLOW}Reloading Essentials…")

        self.plugin.reload_config()

        if self.plugin.script_loader is not None:
            self.plugin.script_loader.unload_scripts()
            self.plugin.script_loader.load_scripts()

        sender.send_message(f"{ColorFormat.GREEN}Essentials reloaded successfully.")
        return True
