#!/usr/bin/python
#
# pills.py > pills.html

import random

def gen(total):
    t = half = 0
    while total:
        yield t, half, total
        if random.randrange(total) < half:
            total -= 1
            half -= 1
        else:
            half += 1
        t += 1

def main():
    data = list(gen(1000))

    print """<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var areadata = google.visualization.arrayToDataTable([
          ['Time', 'Halves', 'Wholes'],"""

    for t, half, total in data:
        print "          ['%d', %d, %d]," % (t, half, total - half)

    print """        ]);
        var linedata = google.visualization.arrayToDataTable([
          ['Time', '% Halves'],"""

    for t, half, total in data:
        print "          ['%d', %f]," % (t, float(half) / total)

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