def plot_line(x, y, title='', xlabel='', ylabel=''):
    """
    return a string which renders x-y line plot for web browser
    
    INPUTS:
    x, y: list of numbers
    title, xlabel, ylabel: string
    """

    google_plot = u"""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
    google.load('visualization', '1', {'packages':['corechart']});
    google.setOnLoadCallback(drawChart);

    function drawChart() {
         var data = google.visualization.arrayToDataTable(["""
          

#    google_plot += """['%s', '%s'],""" %(xlabel, ylabel)

    for xi, yi in zip(x,y):
        google_plot += """[%s, %s],""" %(str(xi), str(yi))

    google_plot += """]);

      var options = {
        title: "%s", 
        curveType: 'function',
        vAxis: { title: '%s', 
             viewWindow:{min:0}
             },
        hAxis: { title: '%s'},
      }

      var chart = new google.visualization.LineChart(
                    document.getElementById('chart_div'));
      chart.draw(data, options);
    }
    </script>""" %(title, ylabel, xlabel)

    return google_plot
