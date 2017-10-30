from functools import wraps, partial
def do_function_on(mode='single', type_filter=[], get_selection=True):
    def do_single():
        for arg in args:
            func(arg,**kwargs)
    def do_last():
        if len(args)>2:
            for arg in args[:-1]:
                func(arg,args[-1])
    def decorator(func):
        """wrap a function to operate on select object or object name string according to mode
                mode: single, double, set, singlelast, last, doubleType"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            modedict = {'single':do_single,'last':do_last}
            return modedict[mode]()
        return wrapper
    return decorator
@do_function_on(mode='last')
def do(*args, **kwargs):
    print args
    print kwargs
print do(1,2,3)
