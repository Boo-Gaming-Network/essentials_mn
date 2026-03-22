import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_essentials import EssentialsPlugin


class ScriptLoader:
    """Loads and executes Python scripts from the plugin's scripts directory.

    Place any ``*.py`` file inside ``<data_folder>/scripts/`` and define an
    ``on_load(plugin)`` function at the module level.  The function will be
    called with the :class:`EssentialsPlugin` instance when the plugin enables,
    giving scripts full access to the server API without requiring a plugin
    rebuild.
    """

    def __init__(self, plugin: "EssentialsPlugin") -> None:
        self._plugin = plugin

    def load_scripts(self) -> None:
        scripts_dir = Path(self._plugin.data_folder) / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_files = sorted(scripts_dir.glob("*.py"))
        if not script_files:
            return

        self._plugin.logger.info(f"Loading {len(script_files)} script(s) from {scripts_dir}")

        for script_path in script_files:
            self._load_script(script_path)

    def _load_script(self, path: Path) -> None:
        module_name = f"essentials_script_{path.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                self._plugin.logger.warning(f"Could not load spec for script {path.name}, skipping.")
                return
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            on_load = getattr(module, "on_load", None)
            if callable(on_load):
                self._plugin.logger.info(f"Loading script: {path.name}")
                on_load(self._plugin)
            else:
                self._plugin.logger.warning(
                    f"Script {path.name} has no on_load(plugin) function — skipping execution."
                )
        except Exception as e:
            self._plugin.logger.error(f"Failed to load script {path.name}: {e}")
