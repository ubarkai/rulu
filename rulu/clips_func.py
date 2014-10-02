from typedefs import Integer, Number, String, Symbol, FactIndexType

def clips_func(funcname, return_type):
    from expr import ClipsFuncExpr
    def func(*args):
        return ClipsFuncExpr(funcname.replace('_', '-'), return_type, *args)
    func.__name__ = funcname
    return func

# TODO: Add more functions
min_ = clips_func('min', Number)
max_ = clips_func('max', Number)
fact_index = clips_func('fact-index', FactIndexType)
gensym = clips_func('gensym', Symbol)
