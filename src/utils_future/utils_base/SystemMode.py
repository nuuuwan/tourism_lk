import os
import platform

from utils import Log

log = Log('SystemMode')


class SystemMode:
    def __init__(self, id, emoji, logger):
        self.id = id
        self.emoji = emoji
        self.logger = logger

    def log(self):
        self.logger(
            '💻System is running in'
            + f' {self.emoji} {self.id.upper()} mode '
            + f'(platform={platform.platform()}, os.name={os.name})'
        )

    @staticmethod
    def get() -> 'SystemMode':
        os_name = os.name
        if os_name == 'nt':
            mode = SystemMode('test', '🚸', log.warn)
        else:
            mode = SystemMode('prod', '💪🏽', log.info)
        return mode

    @staticmethod
    def get_if(**kwargs):
        mode = SystemMode.get()
        mode_id = mode.id
        if mode_id not in kwargs:
            raise Exception(f'Unknown mode: {mode_id}')
        mode.log()
        v = kwargs[mode_id]
        mode.logger(f'{kwargs=} -> {v}')
        return v
