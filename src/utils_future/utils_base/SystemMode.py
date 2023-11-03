import os
import platform

from utils import Log

log = Log('SystemMode')


class SystemMode:
    def __init__(self, name, emoji, logger):
        self.name = name
        self.emoji = emoji
        self.logger = logger

    @staticmethod
    def get() -> str:
        os_name = os.name
        if os_name == 'nt':
            return SystemMode('test', '🚸', log.warn)
        return SystemMode('prod', '🏍️', log.info)

    @staticmethod
    def log_mode():
        mode = SystemMode.get()
        mode.logger(
            '💻System is running in'
            + f' {mode.emoji} {mode.name.upper()} mode '
            + f'({platform.platform()}, {os.name})'
        )

    @staticmethod
    def is_test() -> bool:
        mode = SystemMode.get()
        SystemMode.log_mode()
        return mode.name == 'test'
