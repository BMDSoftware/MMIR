# Plugin loader.
# the code in https://github.com/ArjanCodes/2021-plugin-architecture has been taken as a basis
import importlib

class PluginInterface:

    @staticmethod
    def initialize() -> None:
        """Register the algorithmsPlugin as plugins """


def import_module(name: str) -> PluginInterface:
    """Imports a module given a name."""
    full_path ="main.plugins." + name
    #full_path ="plugins." + name
    return importlib.import_module(full_path)  # type: ignore


def load_plugins(plugins) -> None:
    """Loads the plugins defined in the plugins list."""
    for plugin_file in plugins:
        plugin = import_module(plugin_file)
        plugin.initialize()

