class Stack:
    def __init__(self):
        self.list = []
        self.current = 0

    def push(self, obj):
        self.list.append(obj)
        self.current = self.current + 1

    def pop(self):
        if self.list == []:
            return None
        else:
            self.current = self.current - 1
            return self.list[self.current]

    def peek(self):
        return self.list[self.current-1]

