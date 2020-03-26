from __future__ import absolute_import
from discord.ext.commands import Cog

from artbot import Artbot


class BaseCog(Cog):
    def __init__(self, bot):
        self.bot: Artbot = bot
