#!/usr/bin/env python
# vim: fileencoding=utf-8 et ts=4 sts=4 sw=4 tw=0 fdm=marker fmr=#{,#}

from collections import deque
from itertools   import islice, tee, izip_longest, chain, repeat, groupby
from heapq       import heapify, heappop, heapreplace

_disabled = object()

def first(iterable, default=None):  #{
    """ Returns the first item of an iterable or default value if it's empty

        >>> print first([1,2,3])
        1
        >>> print first(xrange(5), default='')
        0
        >>> print first((), 15)
        15
    """
    return next(iter(iterable), default)
#}
def second(iterable):  #{
    """ Returns the second item of an iterable or None if there is no second item

        >>> print second([1,2,3])
        2
        >>> print second([1])
        None
        >>> print second(())
        None
    """
    it = iter(iterable)
    next(it, None)
    return next(it, None)
#}
def last(iterable, default=None):  #{
    """ Returns the last element of an iterable or None if it's empty

        >>> print last([1,2,3])
        3
        >>> print last(xrange(5), default='')
        4
        >>> print last((), 15)
        15
    """
    if hasattr(iterable,'__reversed__'):
        last = next(reversed(iterable), default)
    else:
        last = default
        for last in iterable:
             pass
    return last
#}

def take(n, iterable):  #{
    "Returns the first n items of an iterable"
    return islice( iterable, n )
#}
def skip(n, iterable):  #{
    """ Advances an iterator n-steps ahead. If n is None, consumes entirely
    """
    it = iter(iterable)

    if n is None:
        # feed the entire iterator into a zero-length deque
        deque(it, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(it, n, n), None)

    return it
#}
def all_but_last(iterable, n=1):  #{
    """ Returns an iterator over all values but the last n (skips the last n values)
    """
    it   = iter(iterable)
    ring = list(take(n, it))
    idx  = 0

    for val in it:
        yield ring[idx]
        ring[idx] = val
        idx = (idx + 1) % n
#}

def flatten(iter_of_iters):  #{
    "Flattens one level of nesting"
    return chain.from_iterable(iter_of_iters)
#}
def gen_chunks(iterable, n, pad=None):  #{
    """ Generates non-overlapping chunks of n elements.
        The last chunk is padded with a value.
    """
    return izip_longest(*[iter(iterable)]*n, fillvalue=pad)
#}
def partition(iterable, n, step=None, pad=_disabled):  #{
    """ Generates chunks of n elements with a specified step (default is n).
        The last chunk may be padded with a value (if set).

        >>> for part in partition(xrange(10), 4): print list(part)
        [0, 1, 2, 3]
        [4, 5, 6, 7]
        [8, 9]
        >>> for part in partition(xrange(10), 4, step=2): print list(part)
        [0, 1, 2, 3]
        [2, 3, 4, 5]
        [4, 5, 6, 7]
        [6, 7, 8, 9]
        >>> for part in partition(xrange(5), 3, step=1): print list(part)
        [0, 1, 2]
        [1, 2, 3]
        [2, 3, 4]
        >>> for part in partition(xrange(10), 4, step=7): print list(part)
        [0, 1, 2, 3]
        [7, 8, 9]
        >>> for part in partition(xrange(10), 4, pad=0): print list(part)
        [0, 1, 2, 3]
        [4, 5, 6, 7]
        [8, 9, 0, 0]
        >>> for part in partition(xrange(5), 4, step=1, pad=0): print list(part)
        [0, 1, 2, 3]
        [1, 2, 3, 4]
    """
    step = step or n
    pos  = iter(iterable)
    none = ()

    if pad is _disabled:
        get_slice = islice
    else:
        get_slice = lambda it,n: islice(chain(it, repeat(pad)), n)

    while True:
        test, feed, pos = tee(pos, 3)

        if next(test, none) is none:
            break

        yield get_slice(feed, n)

        if n >= 1 and next(islice(test, n-1, n), none) is none:
            break

        next(islice(pos, step, step), None)  # step
#}

def unique(iterable, key=None):  #{
    """ Generates unique elements, preserving order.
        Remembers all elements ever seen.

        >>> ' '.join(unique('AAAABBBCCDAABBB')) == 'A B C D'
        True
        >>> data = ('one', 'two', 'three')
        >>> ' '.join(unique(data)) == 'one two three'
        True
        >>> ' '.join(unique(data, key=lambda x: 'o' in x)) == 'one three'
        True
    """
    seen = set()
    add  = seen.add
    if not key:
        key = lambda x: x

    for elem in iterable:
        elem_key = key(elem)
        if elem_key not in seen:
            add(elem_key)
            yield elem
#}
def unique_sorted(iterable, key=None):  #{
    return (v for v,_ in groupby(iterable, key=key))
#}
def duplicates(iterable, key=None):  #{
    """ Generates duplicates

    >>> list(duplicates([1, 2, 3, 2, 1])) == [1, 2]
    True
    """
    for key, group in groupby(sorted(iterable, key=key), key):
        for item in islice(group, 1, None):
            yield item
#}

def merge(*iterables, **kwargs):  #{
    """ A generator that merges multiple sorted inputs into a single
        sorted output.

        [a standard python version of heapq.merge with added key=...]

        Similar to sorted(itertools.chain(*iterables)) but returns a generator,
        does not pull the data into memory all at once, and assumes that each of
        the input streams is already sorted (smallest to largest).

        Optionally accepts a keyword argument key=<key-func>

        >>> list(merge([1,3,5,7], [0,2,4,8], [5,10,15,20], [], [25]))
        [0, 1, 2, 3, 4, 5, 5, 7, 8, 10, 15, 20, 25]

        >>> i1 = [{'id':1}, {'id':4}, {'id':8}]
        >>> i2 = [{'id':0}, {'id':2}, {'id':8}, {'id':15}]
        >>> i3 = []
        >>> i4 = [{'id':1}]
        >>> list( merge( i1, i2, i3, i4, key=lambda x: x['id'] ) )
        [{'id': 0}, {'id': 1}, {'id': 1}, {'id': 2}, {'id': 4}, {'id': 8}, {'id': 8}, {'id': 15}]
    """
    key = kwargs.pop('key', lambda x: x)
    assert not kwargs, 'unknown keyword parameter(s): %r' % kwargs
    _heappop, _heapreplace, _StopIteration = heappop, heapreplace, StopIteration

    h = []
    h_append = h.append
    for itnum, it in enumerate(map(iter, iterables)):
        try:
            next = it.next
            val  = next()
            h_append([key( val ), val, itnum, next])
        except _StopIteration:
            pass
    heapify(h)

    while 1:
        try:
            while 1:
                k, v, itnum, next = s = h[0]   # raises IndexError when h is empty
                yield v
                v = next()
                s[0:2] = key( v ), v        # raises StopIteration when exhausted
                _heapreplace(h, s)          # restore heap condition
        except _StopIteration:
            _heappop(h)                     # remove empty iterator
        except IndexError:
            return
#}

#{  perform self-tests
if __name__ == '__main__':
    print 'Running self-tests...'

    from doctest import testmod
    failed, total = testmod()

    if not failed:
        print 'OK, %d test(s) passed' % total
#}
