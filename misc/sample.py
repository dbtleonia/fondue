#!/usr/bin/python

import random

class Sample(object):
  def __init__(self, k):
    self._k = k
    self._n = 0
    self._values = []

  def Add(self, x):
    self._n += 1
    if self._n <= self._k:
      self._values.append(x)
    else:
      i = random.randrange(self._n)
      if i < self._k:
        self._values[i] = x

  def Values(self):
    return self._values


def main():
  domain = 10
  size = 3
  dist = [0] * domain
  for _ in range(10000):
    sample = Sample(size)
    for i in range(domain):
      sample.Add(i)
    for v in sample.Values():
      dist[v] += 1
  print dist


if __name__ == '__main__':
  main()
