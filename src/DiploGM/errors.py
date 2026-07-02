from discord.ext import commands


class CommandPermissionError(commands.CheckFailure):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class NoGameError(RuntimeError):
    """Raised when a command requires a game but none exists in the server."""


class MapRenderError(RuntimeError):
    """Raised when rendering a map fails for any reason in the drawing pipeline."""
