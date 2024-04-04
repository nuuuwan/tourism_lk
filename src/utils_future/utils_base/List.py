from utils import Parallel


class List:
    def __init__(self, *arr):
        if len(arr) == 1:
            arr = arr[0]
        self.arr = arr

    def map_parallel(self, func, max_threads=3):
        return Parallel.map(func, self.arr, max_threads)

    def map(self, func):
        return list(map(func, self.arr))

    def filter(self, func):
        return list(filter(func, self.arr))

    def unique(self):
        return sorted(list(set(self.arr)))

    def unique_for_key(self, func_key):
        idx = dict(self.map(lambda x: (func_key(x), x)))
        return sorted(list(idx.values()), key=func_key)
