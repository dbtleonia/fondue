#!/usr/bin/python

import random

h = 10
n = 20
x = [random.randrange(h) for _ in xrange(n)]
w = [0] * n
a, b = 0, n-1
aa, bb = x[0], x[-1]
while a < b:
  if x[a] < x[b]:
    a += 1
    aa = max(aa, x[a])
    w[a] = aa - x[a]
  else:
    b -= 1
    bb = max(bb, x[b])
    w[b] = bb - x[b]

for r in xrange(h-1, 0, -1):
  for i in xrange(n):
    if x[i] + w[i] >= r:
      if x[i] >= r:
        print '#',
      else:
        print '~',
    else:
      print ' ',
  print
