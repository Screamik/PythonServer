import re


class Substitutor():
    storage = {}
    sleepTime = 0

    def put(self, key, value):
        self.storage[key] = value

    def get(self, key, inProgress=None):
        if not inProgress:
            inProgress = set()
        elif key in inProgress:
            inProgress.clear()
            raise InfiniteRecursionException
        if key in self.storage:
            out = self.storage[key]
        else: return ''
        inProgress.add(key)
        for templ in set(re.findall(r'\$\{(\S+)\}', out)):
            part = self.get(templ, inProgress)
            out = out.replace('${' + templ + '}', part)
        inProgress.remove(key)
        return out

    def getSleepTime(self):
        return self.sleepTime

    def setSleepTime(self, seconds):
        Substitutor.sleepTime = seconds


class InfiniteRecursionException(ValueError): pass