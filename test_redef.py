#!/usr/bin/env python

import unittest
from redef import redef, stdout_of
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
        ok(rd_p.called()) == 0
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

    @test('Test7: multiple calls, capture stdout')
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
        rd_d = redef(Pirate, 'drink', None)
        captured = stdout_of(blackbeard.plunder, 'buried treasure')

        ok(rd_d.called()) == 9

        talk = 'arrr!\n' + 'burp!\n' * 9 + 'yarrr, don\'t touch me buried treasure\n'

        ok(captured.output) == talk
        ok(captured.returned) == 'punch'

        captured = stdout_of(blackbeard.plunder, 'parrot')
        ok(rd_d.called()) == 18

        rd_d.reset()
        ok(rd_d.called()) == 0

if __name__ == '__main__':
    unittest.main()
