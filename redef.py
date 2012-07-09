'''
redef.py
@author joeheyming@gmail.com
Test module that redefines attributes of a module or class
When the test goes out of scope, your redefined attribute goes back to normal behavior.
'''

import types
import inspect

class CallableWrapper:
    '''Captures information on a redefined function'''
    called = 0
    method_args = None
    named_method_args = None

    def capture(self, args, kwargs):
        '''Store the input to the captured function'''
        self.called = self.called + 1
        self.method_args = args
        self.named_method_args = kwargs

    def reset(self):
        '''Set the wrapper to a base state where the function was never called'''
        self.called = 0
        self.method_args = None
        self.named_method_args = None

    def __init__(self, rd):
        '''Take a Redef object and wrap the function you want to redefine'''
        # don't keep any references to the Redef object around
        # or else the __del__ function will not work correctly
        is_class_method = not inspect.ismethod(rd.old_value)
        func = rd.value

        def tocall(*args, **kwargs):
            self.capture(args, kwargs)

            # pop off the redef class variable to keep the
            # faked out function signature the same
            if is_class_method:
                args = args[1:]

            return func(*args, **kwargs)

        # @staticmethods need to return a function bound
        #  to the class
        if is_class_method:
            tocall = types.MethodType(tocall, rd.obj)
        self.wrapped = tocall

class Redef(object):
    '''An object that when deleted puts the redefined object back to normal'''

    def __init__(self, obj, key, value):
        '''Make sure you keep the returned Redef object in a variable so that the __del__ function is not called immediately

Good: >>> rd_somefunc = Redef(SomeClass, "attr", lambda s, x: "something else")
Bad: >>> Redef(SomeClass, "attr", lambda s, x: "something else")

        '''
        self.key = key
        self.obj = obj
        self.old_value = getattr(self.obj, self.key)
        self.value = value

        if value is None:
            self.value = self.old_value
        self.wrapper = CallableWrapper(self)
        if callable(self.value):
            setattr(self.obj, self.key, self.wrapper.wrapped)
        else:
            setattr(self.obj, self.key, self.value)

    def __del__(self):
        '''Can be called explicitly or implied when gone out of scope'''
        setattr(self.obj, self.key, self.old_value)

    def called(self):
        '''ask the wrapper how many times the redef has been called'''
        return self.wrapper.called

    def method_args(self):
        '''ask the wrapper for the most recent non-named args'''
        return self.wrapper.method_args

    def named_method_args(self):
        '''ask the wrapper for the most recent named args'''
        return self.wrapper.named_method_args

    def reset(self):
        '''ask the wrapper to forget all wrapped information'''
        self.wrapper.reset()

def redef(obj, key, value):
    '''A static constructor helper function'''
    return Redef(obj, key, value)

class WriteCapturer:
    def __init__(self, func, *args, **kwargs):
        self.output = ''
        self.func = func
        self.args = args
        self.kwargs = kwargs
    def capture(self):
        self.returned = self.func(*self.args, **self.kwargs)
    def write(self, *args):
        self.output = self.output + ' '.join([str(x) for x in args])

def capture_output_(output_type, func, *args, **kwargs):
    import sys
    writer = WriteCapturer(func, *args, **kwargs)
    rd_write = redef(sys, output_type, writer)
    writer.capture()
    return writer

def stdout_of(func, *args, **kwargs):
    return capture_output_('stdout', func, *args, **kwargs)

def stderr_of(func, *args, **kwargs):
    return capture_output_('stderr', func, *args, **kwargs)
