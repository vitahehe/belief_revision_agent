""" NOT USED RIGHT NOW, MAY NOT BE NEEDED"""

class LiteralStats:
    true_count: int = 0
    false_count: int = 0

class LiteralStore:
    def __init__(self):
        self.data = {}

    def add(self, letter: str, is_true: bool):
        if letter not in self.data:
            self.data[letter] = LiteralStats()

        if is_true:
            self.data[letter].true_count += 1
        else:
            self.data[letter].false_count += 1

    def remove(self, letter: str, is_true: bool):
        if letter not in self.data:
            return

        if is_true:
            self.data[letter].true_count -= 1
        else:
            self.data[letter].false_count -= 1

        if self.data[letter].true_count <= 0 and self.data[letter].false_count <= 0:
            del self.data[letter]

    def get(self, letter: str):
        return self.data.get(letter, LiteralStats())

    def iter_pairs(self):
        for letter, stats in self.data.items():
            pair_count = min(stats.true_count, stats.false_count)
            for _ in range(pair_count):
                yield letter

    def __repr__(self):
        return str(self.data)