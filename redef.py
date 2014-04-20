'''
redef.py
@author joeheyming@gmail.com
Test module that redefines attributes of a module or class
When the test goes out of scope, your redefined attribute goes back to normal behavior.
'''

import inspect
import sys
import types
from cStringIO import StringIO
class CallableWrapper:
    '''Captures information on a redefined function'''
    never_called = True
    def _capture(self, args, kwargs):
        '''Store the input to the captured function'''
        self.called = self.called + 1
        self.method_args.append(args)
        self.named_method_args.append(kwargs)
        self.never_called = False

    def reset(self):
        '''Set the wrapper to a base state where the function was never called'''
        self.called = 0
        self.method_args = []
        self.named_method_args = []

    def __init__(self, rd):
        '''Take a Redef object and wrap the function you want to redefine'''
        # don't keep any references to the Redef object around
        # or else the __del__ function will not work correctly
        is_class_method = not inspect.ismethod(rd.old_value)
        func = rd.value
	self.reset()

        def tocall(*args, **kwargs):
            self._capture(args, kwargs)

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

    def __init__(self, obj, key, **kwargs):
        '''Make sure you keep the returned Redef object in a variable so that the __del__ function is not called immediately

Good: >>> rd_somefunc = Redef(SomeClass, "attr", lambda s, x: "something else")
Bad: >>> Redef(SomeClass, "attr", lambda s, x: "something else")

        kwargs can contain the resub\'d value as well as constraints like "must_call", "must_exist"
        '''
        stack = inspect.stack()[2]

        if stack is not None:
            file_name = stack[1]
            line_num = stack[2]
            code = ""
            if stack[4] is not None:
                code = stack[4][0].lstrip()
            self.stack = '\t%s:%s: %s' % (file_name, line_num, code)
        self.obj = obj
        self.key = key
        self.must_exist = kwargs.get('must_exist', True)
        if self.must_exist and not hasattr(self.obj, self.key):
            raise Exception('object: %s does not have any attribute: %s' % (repr(self.obj), self.key))

        self.old_value = getattr(self.obj, self.key)
        self.value = kwargs.get('value', self.old_value)
        self.must_call = kwargs.get('must_call', True)

        self.wrapper = CallableWrapper(self)
        if callable(self.value):
            setattr(self.obj, self.key, self.wrapper.wrapped)
        else:
            setattr(self.obj, self.key, self.value)

    def __del__(self):
        """Can be called explicitally, but it's encouraged to use a 'with' statement to redefine a function"""
        self.close()        

    def __exit__(self, type, value, callback):
        self.close()

    def called(self):
        '''ask the wrapper how many times the redef has been called'''
        return self.wrapper.called

    def method_args(self):
        '''ask the wrapper for the list of non-named args'''
        return self.wrapper.method_args

    def named_method_args(self):
        '''ask the wrapper for the list of named args'''
        return self.wrapper.named_method_args

    def was_called(self):
        '''Helper function to know if any calls were made. Note: reset doesn\'t change never_called'''
        return not self.wrapper.never_called

    def not_called(self):
        '''Helper function to determine a function wasn\'t called.  Note: reset doesn\'t change never_called'''
        return self.wrapper.never_called

    def reset(self):
        '''ask the wrapper to forget all wrapped information'''
        self.wrapper.reset()

    def __enter__(self):
        self.wrapper.reset()

    def close(self):
        if callable(self.value):
            what_happened = ''
            if self.not_called() and self.must_call:
                what_happened = 'was not called and should have been called'
            if self.was_called() and not self.must_call:
                what_happened = 'was called and should not have been called'

            if what_happened != '':
                sys.stderr.write('redef\'d function \'%s\' %s.\n\tMis-called redefs could be due to test crashes unless explicitly tested using Redef kwargs: must_call\n' % (self.key, what_happened))
                if self.stack:
                    sys.stderr.write(str(self.stack))
        setattr(self.obj, self.key, self.old_value)

def redef(obj, key, value, **kwargs):
    '''A static constructor helper function'''
    return Redef(obj, key, value=value, **kwargs)

def wiretap(obj, key, **kwargs):
    '''Use redef for the capture capabilities, but don\'t redefine the function'''
    return Redef(obj, key, **kwargs)

class CapturedOutput:
    def __init__(self, output, returned):
        self.output = output
        self.returned = returned

def capture_output_(output_type, func, *args, **kwargs):
    import sys
    io = StringIO()
    rd_write = redef(sys, output_type, io)
    returned = func(*args, **kwargs)
    captured = CapturedOutput(io.getvalue(), returned)
    io.close()
    return captured

def stdout_of(func, *args, **kwargs):
    return capture_output_('stdout', func, *args, **kwargs)

def stderr_of(func, *args, **kwargs):
    return capture_output_('stderr', func, *args, **kwargs)
