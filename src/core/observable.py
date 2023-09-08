class Observable:
    def __init__(self):
        self.observers = []

    def register(self, observer) -> None:
        if observer not in self.observers:
            self.observers.append(observer)

    def unregister(self, observer) -> None:
        if observer in self.observers:
            self.observers.remove(observer)

    def unregister_all(self) -> None:
        if self.observers:
            del self.observers[:]

    def update_observers(self) -> None:
        for observer in self.observers:
            observer.update()
