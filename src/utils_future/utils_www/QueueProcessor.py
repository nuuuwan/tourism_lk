import queue
from utils import Log
log = Log('QueueProcessor')

class QueueProcessor:
    @staticmethod
    def run(initial_items, func_process, func_end):
        queue = queue.Queue()
        for item in initial_items:
            queue.put(item)

        results = []
        visited_items = set()
        while queue.not_empty and not func_end(results):
            current_item = queue.get()
            if current_item in visited_items:
                continue
            visited_items.add(current_item)

            log.debug(f'Visiting {item}...')
            new_items, new_results = func_process(current_item)
            for item in new_items:
                queue.put(item)
            results += new_results
            log.debug(f'len(results)={len(results)}')

        return results