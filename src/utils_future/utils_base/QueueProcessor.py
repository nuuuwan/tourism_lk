import queue

from utils import Log

from utils_future.utils_base.List import List

log = Log('QueueProcessor')


class QueueProcessor:
    @staticmethod
    def run(initial_items, func_process, func_end):
        q = queue.Queue()
        for item in initial_items:
            q.put(item)

        results = []
        visited_items = set()
        while q.not_empty and not func_end(results):
            current_item = q.get()
            if current_item in visited_items:
                continue
            visited_items.add(current_item)

            log.debug(f'Visiting {item}...')
            new_items, new_results = func_process(current_item)
            for item in new_items:
                q.put(item)
            results += new_results
            results = List(results).unique()
            log.debug(f'len(results)={len(results)}')

        return results
