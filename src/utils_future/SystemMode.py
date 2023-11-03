import os
import platform

from utils import Log

log = Log('SystemMode')


class SystemMode:
    @staticmethod
    def is_test() -> bool:
        os_name = os.name
        _is_test = os_name == 'nt'
        if _is_test:
            log.warn(
                f'💻System is running in 👶test mode. os.name={os_name}. {platform.platform()}'
            )
        return _is_test
