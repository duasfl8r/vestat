#!/usr/bin/python
# -*- encoding: utf-8 -*-
from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

### HACK PRO PICKLE ###

def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

def _pickle_function(function):
    func_name = function.func_name
    return _unpickle_function, (func_name,)

def _unpickle_function(func_name):
    return globals()[func_name]

import copy_reg
import types
copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
copy_reg.pickle(types.FunctionType, _pickle_function, _unpickle_function)

### FIM DO HACK PRO PICKLE ###

if __name__ == "__main__":
    execute_manager(settings)
