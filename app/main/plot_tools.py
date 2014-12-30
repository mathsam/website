def plot_line(x, y, div_id, title='', xlabel='', ylabel=''):
    """
    return a string which renders x-y line plot for web browser
    
    INPUTS:
        x, y: list of numbers
        div_id: string, a unique id for the chart
            Note: should be UNIQUE to avoid name collision
        title, xlabel, ylabel: string
    
    Usage:
        example_chart = plot_line([1,2,3],[4,5,6],'chart1',
                                  'example', 'x','y')
        #in Jinja template
        # notice safe is needed for correct parsing <>
        {{ example_chart | safe }}
    """

    google_plot = u"""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
    google.load('visualization', '1', {'packages':['corechart']});
    google.setOnLoadCallback(drawChart);

    function drawChart() {
         var data = google.visualization.arrayToDataTable(["""
          

    google_plot += u"""['%s', '%s'],""" %(xlabel, ylabel)

    for xi, yi in zip(x,y):
        google_plot += """[%s, %s],""" %(str(xi), str(yi))

    google_plot += u"""]);

      var options = {
        title: "%s", 
        curveType: 'function',
        vAxis: { title: '%s', 
             viewWindow:{min:0}
             },
        hAxis: { title: '%s'}
      };

      var chart = new google.visualization.LineChart(
                    document.getElementById('%s'));
      chart.draw(data, options);
    }
    </script>""" %(title, ylabel, xlabel, div_id)

    google_plot += u"""
    <div class="container-fluid">
    <div id="%s"></div></div>
    </div>""" %div_id

    return google_plot
