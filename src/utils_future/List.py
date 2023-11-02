class List:
    def __init__(self, *arr):
        if len(arr) == 1:
            arr = arr[0]
        self.arr = arr

    def map(self, func):
        return list(map(func, self.arr))

    def filter(self, func):
        return list(filter(func, self.arr))

    def unique(self):
        return sorted(list(set(self.arr)))

    def unique_for_key(self, key):
        idx = dict(self.map(lambda x: (x[key], x)))
        return sorted(list(idx.values()), key=lambda x: x[key])
