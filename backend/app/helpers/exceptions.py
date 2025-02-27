class LogicException(Exception):
    def __init__(self, message, code=500):
        super().__init__(message)

        self.message = message
        self.code = code
