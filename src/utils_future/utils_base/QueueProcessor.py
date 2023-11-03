from utils import Log

from utils_future.utils_base.List import List

log = Log('QueueProcessor')


class QueueProcessor:
    @staticmethod
    def run(initial_items, func_process, func_end):
        q = initial_items

        results = []
        visited_items = set()
        while len(q) > 0 and not func_end(results):
            current_item = q.pop(0)
            if current_item in visited_items:
                continue
            visited_items.add(current_item)
            log.debug(f'Visiting {current_item}...')
            new_items, new_results = func_process(current_item)
            q.extend(new_items)
            results += new_results
            results = List(results).unique()
            log.debug(f'len(results)={len(results)}, len(q)={len(q)}.')

        log.debug(f'len(results)={len(results)} final.')
        return results
