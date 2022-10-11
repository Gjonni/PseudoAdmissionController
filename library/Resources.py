class Resources(dict):
    def __init__(self, dic):
        for key, val in dic.items():
            self.__dict__[key] = self[key] = (
                Resources(val) if isinstance(val, dict) else val
            )