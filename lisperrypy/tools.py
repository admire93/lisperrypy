# -*- coding: utf-8 -*-
from re import compile, match
from itertools import chain
from functools import reduce
from string import whitespace

from .types import Operator, Number, LispType


RE = {
    'NUMBERS': r'((-|\+)?[1-9][0-9]*\.?[0-9]*)',
    'EXPRESSION': r'[^\s\d\(\)\[\]][^\s\(\)\[\]]*',
    'BRACES': r'\(|\)|\[|\]',
    'WHITESPACE': r'\s+'
}


def sum_(*args):
    r = reduce(lambda x, y: x + y, args)
    return r


def sub(*args):
    return reduce(lambda x, y: x - y, args)


def div(*args):
    return reduce(lambda x, y: x / float(y), args)


def mult(*args):
    return reduce(lambda x, y: x * y, args)


def def_(sym, val, env):
    env[sym] = val
    return val


ENV = {'+': sum_, '-': sub, '*': mult, '/': div}
numbers = ''.join([str(x) for x in range(0,9)]) + '.'


def tokenize(sources):
    i = 0
    state = False
    b = ''
    while i < len(sources) - 1:
        t = sources[i]
        r = None
        if t == '(' or t == ')' or t == '`':
             r = [t]
        elif t in whitespace:
            i += 1
            continue
        elif t == '"' or t == "'":
            return tokenize_str(sources[i:])
        elif t in numbers:
            return tokenize_number(sources[i:])
        else:
            r = [t]
        if r is not None:
            return r + tokenize(sources[i+1:])
        i += 1
    return [sources]


def tokenize_str(sources):
    b = sources[0]
    i = 1
    while sources[i] != b[0]:
        b += sources[i]
        i += 1
    return [b + sources[i]] + tokenize(sources[i+1:])


def tokenize_number(sources):
    b = ''
    i = 0
    while sources[i] in numbers:
        b += sources[i]
        i += 1
    return [b] + tokenize(sources[i:])


def form(t):
    if t == '(' or isinstance(t, list) or isinstance(t, LispType):
        r = t
    elif match(RE['NUMBERS'], t):
        r = Number(t)
    elif match(RE['EXPRESSION'], t):
        r = Operator(t)
    return r


def parse(tokens):
    tree = []
    start = 0
    for i, token in enumerate(tokens):
        if token == '(':
            start = i
        if token != ')':
            tree.append(form(token))
        else:
            l = list(chain(tree[:start],
                           [tree[start + 1:]],
                           tokens[i + 1:]))
            return parse(l)
    return tree


def apply_(op, args):
    return op(*args)


def evalu(form, env):
    integer = r'(-|\+)?[1-9][0-9]*$'
    if isinstance(form, Number):
        if match(integer, form.exp):
            return int(form.exp)
        else:
            return float(form.exp)
    elif isinstance(form, Operator) and form.exp in env:
        return env[form.exp]
    elif isinstance(form, list):
        r = []
        if form[0].exp == 'def':
            def_(form[1].exp, evalu(form[2], env), env)
        else:
            for x in form:
                r.append(evalu(x, env))
            if callable(r[0]):
                return apply_(r[0], r[1:])
        return r
