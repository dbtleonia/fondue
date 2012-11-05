#!/usr/bin/python
#
# pills.py exact 100 > pills.html
# pills.py rand 200 1000 > pills.html
#
# Common variables below:
#   n - Number of pills to start with
#   t - Total pills remaining (wholes + halves)
#   w - Whole pills remaining
#
# We track w & t when simulating or computing probabilities.
# From state (w, t):
#   choose a whole with prob w/t and move to state (w-1, t)
#   choose a half with prob 1-w/t and move to state (w, t-1)

import random
import sys

def gen_rand(t):
    w = t
    while t:
        yield w, t
        if random.randrange(t) < w:
            w -= 1
        else:
            t -= 1

def run_rand(n, trials):
    wholes = [0] * 2*n
    totals = [0] * 2*n
    for _ in range(trials):
        for i, (w, t) in enumerate(gen_rand(n)):
            wholes[i] += w
            totals[i] += t
    for i in xrange(2*n):
        wholes[i] /= float(trials)
        totals[i] /= float(trials)
    return zip(wholes, totals)

def sum_cache(cache):
    return (sum(w*p for (w, _), p in cache.iteritems()),
            sum(t*p for (_, t), p in cache.iteritems()))

def next_cache(cache, w, t, n):
    next = {}
    while w >= 0 and t <= n:
        p = 0
        if (w+1, t) in cache:
            p += cache[(w+1, t)] * float(w+1)/t
        if (w, t+1) in cache:
            p += cache[(w, t+1)] * (1 - w/float(t+1))
        next[(w, t)] = p
        w -= 1
        t += 1
    return next

def gen_exact(n):
    cache = {(n, n): 1.0}
    yield sum_cache(cache)
    for i in xrange(2*n-1, 0, -1):
        w = i / 2
        t = i - w
        cache = next_cache(cache, w, t, n)
        yield sum_cache(cache)

def run_exact(n):
    return list(gen_exact(n))

def usage():
    print """usage:
  %s exact <n>
  %s rand <n> <trials>
""" % (sys.argv[0], sys.argv[0])    
    sys.exit(1)

def main():
    if sys.argv < 1:
        usage()
    if sys.argv[1] == 'exact':
        if len(sys.argv) != 3:
            usage()
        try:
            data = run_exact(int(sys.argv[2]))
        except ValueError as e:
            print e
            usage()
    elif sys.argv[1] == 'rand':
        if len(sys.argv) != 4:
            usage()
        try:
            data = run_rand(int(sys.argv[2]), int(sys.argv[3]))
        except ValueError as e:
            print e
            usage()
    else:
        usage()

    print """<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var areadata = google.visualization.arrayToDataTable([
          ['Time', 'Halves', 'Wholes'],"""

    for i, (w, t) in enumerate(data):
        print "          ['%d', %f, %f]," % (i, t - w, w)

    print """        ]);
        var linedata = google.visualization.arrayToDataTable([
          ['Time', '% Wholes'],"""

    for i, (w, t) in enumerate(data):
        print "          ['%d', %f]," % (i, float(w) / t)

    print """        ]);
        new google.visualization.AreaChart(document.getElementById('areachart')).draw(areadata, {isStacked: true})
        new google.visualization.LineChart(document.getElementById('linechart')).draw(linedata, {})
      }
    </script>
  </head>
  <body>
    <div id="areachart" style="width: 900px; height: 500px;"></div>
    <div id="linechart" style="width: 900px; height: 500px;"></div>
  </body>
</html>"""

if __name__ == '__main__':
    main()
