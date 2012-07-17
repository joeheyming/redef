# Redef

To install, just run:

```bash
python setup.py build
python setup.py install
```

See [`test_redef.py`](/joeheyming/redef/blob/master/test_redef.py) under your install path for examples.

Redef is intended to create lexically scoped variables, that when destroyed, undo mock behavior.
It was inspired by a Perl module, [Test::Resub](http://search.cpan.org/~airwave/Test-Resub-1.02/lib/Test/Resub.pm)

The best examples use `unittest`, but it should work with any testing framework.

```python
import unittest
from redef import redef

class MyClass:
    def lame_function(self):
        return "something I don't want"

class MyTest(unittest.TestCase):
    def test1(self):
        myobj = MyClass()
        self.assertEqual(myobj.lame_function(), "something I don't want")
        want = 'something I want'
        rd_lf = redef(MyClass, 'lame_function', lambda s: want)
        self.assertEqual(myobj.lame_function(), want)

        # after test1, rd_lf gets deleted and resets

    def test2(self):        
        myobj = MyClass()
        # test2 is uneffected by test1
        self.assertEqual(myobj.lame_function(), "something I don't want")
```

This doesn't have to be a function, you can also redefine attributes directly on an object.

```python
class MyClass:
      unpredictable = 'random string'

my_global_object = MyClass()

class MyTest(unittest.TestCase):
     def test3(self):
         rd_u = redef(my_global_object, 'unpredictable', 'unit testable string')
         # ... test something awesome!
         self.assertEqual(my_global_object.unpredictable, 'unit testable string')

     def test4(self):
         # hey, my_global_object is back to being unpredictable
         self.assertEqual(my_global_object.unpredictable, 'unpredictable')
```
         
There are other useful functions provided on the redef object itself:

* Class Redef:
    * `__init__`:
        * takes an object and a key.  The rest of the arguments are kwargs:
        * if the key doesn't exist in the object, an exception will be raised unless you provide kwargs must_exist
        * value: if provided, this value will redefine the key in the object, otherwise you 'wiretap' the object
        * must_call: if provided, when the Redef object is destroyed, it warns if this constraint is violated.

    * `called()`:
        Stores how many times a redef'd function was called.
    * `method_args()`:
        Stores the most recent `*args` to the redef'd function.
    * `named_method_args()`:
        Stores the most recent `**kwargs` to the redef'd function.
    * `reset()`:
        Sets `called`, `method_args`, and `named_method_args` back to the default state of `0, None, None`

`Redef` also provides a freebie static function:

* `redef(obj, key, value)`:
    Static constructor of a `Redef` object

Where
  * `obj`: is a Class, Module, or Object you want to temporariliy change
  * `key`: The string name of the attribute you want to change
  * `value`: The new value.  If the value is None, you only capture called, method_args, and named_method_args
   * The None case won't redefine the key on the obj

These static functions were provided to show the usefulness of redef: 
For example, you could capture stdout of a function call, and after capturing it,
`sys.stdout` goes back to normal:

* Class CapturedOutput:
    * Has 2 variables you want: `output`, `returned`

* Static Functions that return a CapturedOutput:
    * `stdout_of(func, *args, **kwargs)`:
        Call a function and capture the stdout.
        Returns a `CapturedOutput` object that has the stdout and the return value of calling func.

    * `stderr_of(func, *args, **kwargs)`:
        Call a function and capture the stderr.
        Returns a `CapturedOutput` object that has the stderr and the return value of calling func.
        
* `wiretap`:
    * A static function that creates a Redef object only for the purpose of capturing the method_args and called values.
          * The original functionality should remain the same.

Please ask any questions on github: http://github.com/joeheyming/redef/issues
