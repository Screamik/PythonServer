import re

inProgress = set()


def put(dict, key, value):
    dict[key] = value

def get(dict, key):
    global inProgress
    if key in inProgress:
        inProgress.clear()
        return 'Panic!!! Infinite recursion!!!'
    if key in dict:
        out = dict[key]
    else: return ''
    inProgress.add(key)
    for templ in set(re.findall(r'\$\{(\S+)\}', out)):
        part = get(dict, templ)
        if part == 'Panic!!! Infinite recursion!!!':
            return part
        out = out.replace('${' + templ + '}', part)
    inProgress.remove(key)
    return out