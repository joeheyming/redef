#!/usr/bin/env python

import unittest
from redef import redef, stdout_of, stderr_of, wiretap, Redef
from oktest import ok, test

class Somewhere:
    def show(self, message):
        return self.__class__.__name__ + ', ' + message

class RedefTest(unittest.TestCase):
    @test("Test1: redef del test")
    def _(self):
        somewhere = Somewhere()
        ok(somewhere.show('beyond the sea')) == 'Somewhere, beyond the sea'
        rd_show = redef(Somewhere, 'show', lambda self, message: 'hi')
        ok(somewhere.show('over the rainbow')) == 'hi'
        ok(rd_show.method_args()) == (somewhere, 'over the rainbow')
        ok(rd_show.named_method_args()) == {}
        ok(rd_show.called()) == 1
        rd_show.reset()
        ok(rd_show.method_args()) == None
        ok(rd_show.named_method_args()) == None
        ok(rd_show.called()) == 0
        ok(somewhere.show('beyond the stars')) == 'hi'
        del rd_show
        ok(somewhere.show('beyond the stars')) == 'Somewhere, beyond the stars'

    @test("Test2: test 3 won't have bye after test 2")
    def _(self):
        somewhere = Somewhere()
        ok(somewhere.show('beyond the stars')) == 'Somewhere, beyond the stars'
        rd_show = redef(Somewhere, 'show', lambda self, message: 'bye')
        ok(somewhere.show('over the rainbow')) == 'bye'
    @test("Test3: redef doesn't effect this block")
    def _(self):
        somewhere = Somewhere()
        ok(somewhere.show('beyond the stars')) == 'Somewhere, beyond the stars'

    @test('Test4: redef class variable')
    def _(self):
        class Math:
            pi = 3.14
        m = Math()
        ok(m.pi) == 3.14
        rd_p = redef(m, 'pi', 3)
        ok(m.pi) == 3
        ok(rd_p.not_called()) == True
        ok(rd_p.method_args()) == None
        ok(rd_p.named_method_args()) == None
        del rd_p
        ok(m.pi) == 3.14

    @test('Test5: redef static method')
    def _(self):
        class Hello:
            @staticmethod
            def world(x):
                return 'Hello %s!' % x
        ok(Hello.world('joe')) == 'Hello joe!'
        rd_w = redef(Hello, 'world', lambda x: 'Goodbye %s' % x)

        ok(Hello.world('joe')) == 'Goodbye joe'
        ok(rd_w.method_args()) == (Hello, 'joe')

    @test('Test6: class inheritance')
    def _(self):
        class A:
            '''Base class'''
            def a(self, x):
                return x * 2
        class B(A):
            def a(self, x):
                ret = A.a(self, x)
                return 'b' + ret
        bee = B()
        ok(bee.a('z')) == 'bzz'

        want = 'baa baa'
        rd_b = redef(B, 'a', lambda s,x: want)
        ok(bee.a('z')) == 'baa baa'
        ok(rd_b.called()) == 1
        del rd_b

        want = 'atter batter'
        rd_a = redef(A, 'a', lambda s,x: want)
        ok(bee.a('z')) == 'batter batter'

        ok(rd_a.called()) == 1

    @test('Test7: multiple calls, capture stdout, wiretap')
    def _(self):
        class Pirate:
            drunk = 0
            def attack(self):
                print('arrr!')

            def hoard(self, booty):
                print('yarrr, don\'t touch me %s' % booty)

            def plunder(self, booty):
                self.attack()
                for x in range(1, 10):
                    self.drink()
                self.hoard(booty)
                return 'punch'

            def drink(self):
                print('burp!')
                self.drunk = self.drunk + 1

        blackbeard = Pirate()
        wt_d = wiretap(Pirate, 'drink')
        captured = stdout_of(blackbeard.plunder, 'buried treasure')

        ok(wt_d.was_called()) == True
        ok(wt_d.not_called()) == False
        ok(wt_d.called()) == 9

        talk = 'arrr!\n' + 'burp!\n' * 9 + 'yarrr, don\'t touch me buried treasure\n'
        ok(captured.output) == talk
        ok(captured.returned) == 'punch'

        captured = stdout_of(blackbeard.plunder, 'parrot')
        ok(wt_d.called()) == 18

        wt_d.reset()
        ok(wt_d.not_called()) == False

    @test('Test8: redef an attribute that doesn\'t exist')
    def _(self):
        class Foo:
            pass
        x = Foo()
        self.assertRaises(Exception, redef, (Foo, 'bar',lambda s: 'BAR!'))
        self.assertRaises(Exception, redef, (Foo, 'baz', 'baz!'))
        self.assertRaises(Exception, wiretap, (Foo, 'bar'))
        self.assertRaises(Exception, wiretap, (Foo, 'baz'))

    @test('Test8: redef an attribute, but the function never is called warns error')
    def _(self):
        class Foo:
            def bar(self):
                return 'bar'
        class Delegate:
            def action(self):
                f = Foo()
                return f.bar()

        rd_bar = redef(Foo, 'bar', lambda s: 'baz')
        ok(rd_bar.not_called()) == True
        captured = stderr_of(Redef.__del__, rd_bar)
        ok(captured.output) == 'redef\'d function \'bar\' was not called and should have been called.\n\tMis-called redefs could be due to test crashes unless explicitly tested using Redef kwargs: must_call\n\t./test_redef.py:150: rd_bar = redef(Foo, \'bar\', lambda s: \'baz\')\n'

        wt_bar = wiretap(Foo, 'bar', must_call=False)
        rd_a = redef(Delegate, 'action', lambda s: 'rainbows!')
        Delegate().action()
        ok(wt_bar.not_called()) == True
        captured = stderr_of(Redef.__del__, wt_bar)
        ok(captured.output) == ''

        wt_bar2 = wiretap(Foo, 'bar', must_call=False)
        Foo().bar()
        captured = stderr_of(Redef.__del__, wt_bar2)
        ok(captured.output) == 'redef\'d function \'bar\' was called and should not have been called.\n\tMis-called redefs could be due to test crashes unless explicitly tested using Redef kwargs: must_call\n\t./test_redef.py:162: wt_bar2 = wiretap(Foo, \'bar\', must_call=False)\n'

    @test('Test8: redef a function on a module')
    def _(self):
        import string
        yummy_str = 'yummy apple' 
        rd_replace = redef(string, 'replace', lambda s, x, y: 'orange')
        replaced = string.replace(string, 'apple', 'banana')
        ok(replaced) == 'orange'

if __name__ == '__main__':
    unittest.main()
