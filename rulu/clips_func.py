from expr import ClipsFuncExpr
from typedefs import Integer

class ClipsFuncProxy(object):
    def __getattr__(self, funcname):
        def func(*args):
            return ClipsFuncExpr(funcname.replace('_', '-'), Integer, *args)
        func.__name__ = funcname
        return func

clips_funcs = ClipsFuncProxy()
