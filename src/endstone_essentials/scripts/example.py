# Example Essentials script
#
# Drop this file (or any *.py file) into the plugin's scripts/ folder and the
# plugin will execute it on startup without requiring a rebuild.
#
# Every script MUST define an on_load(plugin) function.  The plugin instance
# gives you access to the full Endstone server API:
#
#   plugin.server      – the Server object
#   plugin.logger      – the plugin logger
#   plugin.data_folder – path to the plugin's data folder
#   plugin.config      – the loaded plugin config
#
# You can also register event listeners:
#
#   import sys
#   from endstone.event import PlayerJoinEvent, event_handler
#
#   @event_handler()
#   def on_player_join(event: PlayerJoinEvent):
#       event.player.send_message("Hello from a custom script!")
#
#   def on_load(plugin):
#       plugin.register_events(sys.modules[__name__])


def on_load(plugin) -> None:
    plugin.logger.info("Example script loaded successfully!")
