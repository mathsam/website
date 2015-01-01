def plot_time_multilines(t, y, div_id, xlabel='', ylabel=None):
    """
    return a string which renders plot using time t as x axis and multiple lines
    for web brower use
    
    INPUTS:
        t: list of Timestamp objects
        y: list of list/numpy array
        div_id: string, unique
        xlabel: string for the name of data in x-axis
        ylabel: a list of strings for each list of data in y
    """
    if ylabel is None:
        ylabel = [''] * len(y)

    google_chart = u"""
    <script type="text/javascript" src="https://www.google.com/jsapi?autoload={'modules':[{'name':'visualization','version':'1','packages':['annotationchart']}]}"></script>
    <script type='text/javascript'>
    google.load('visualization', '1', {'packages':['annotationchart']});
    google.setOnLoadCallback(drawChart);
    function drawChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('date', '%s');""" %xlabel

    for column_name in ylabel:
        google_chart += u"""data.addColumn('number', '%s');""" %column_name

    google_chart += u"""
    data.addRows([""" 

    for (i, ti) in enumerate(t): 
        google_chart += u"""[ new Date(%d, %d, %d)""" %(ti.year, ti.month-1, ti.day)
        for yi in y:
            google_chart += ", %s" %str(yi[i])
        google_chart += u"""], 
    """

    google_chart += u"""
    ]);

    var chart = new google.visualization.AnnotationChart(document.getElementById('%s'));

    var options = {
      displayAnnotations: true,
    };

    chart.draw(data, options);
    }
    </script>
    """ %div_id

    google_chart += u"""
    <div class="container-fluid">
    <div id="%s"></div>
    </div>""" %div_id

    return google_chart


def plot_time_line(t, y, div_id, xlabel='', ylabel=''):
    """
    return a string which renders time line plot for web broser
    
    INPUTS:
        t: list of Timestamp objects
        y: list/numpy array of numbers
    """
    google_chart = u"""
    <script type="text/javascript" src="https://www.google.com/jsapi?autoload={'modules':[{'name':'visualization','version':'1','packages':['annotationchart']}]}"></script>
    <script type='text/javascript'>
    google.load('visualization', '1', {'packages':['annotationchart']});
    google.setOnLoadCallback(drawChart);
    function drawChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('date', '%s');
    data.addColumn('number', '%s');

    data.addRows([
    """ %(xlabel, ylabel)

    #NOTICE: in javascript, Jan is 0, Feb is 1, ...
    # so need to do month-1
    for ti, yi in zip(t, y):
        google_chart += u"""
          [ new Date(%d, %d, %d), %s],""" %(ti.year, ti.month-1, ti.day, str(yi))

    google_chart += u"""
    ]);

    var chart = new google.visualization.AnnotationChart(document.getElementById('%s'));

    var options = {
      displayAnnotations: true,
    };

    chart.draw(data, options);
    }
    </script>
    """ %div_id

    google_chart += u"""
    <div class="container-fluid">
    <div id="%s"></div>
    </div>""" %div_id

    return google_chart
    

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

    google_chart = u"""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
    google.load('visualization', '1', {'packages':['corechart']});
    google.setOnLoadCallback(drawChart);

    function drawChart() {
         var data = google.visualization.arrayToDataTable(["""
          

    google_chart += u"""['%s', '%s'],""" %(xlabel, ylabel)

    for xi, yi in zip(x,y):
        google_chart += """[%s, %s],""" %(str(xi), str(yi))

    google_chart += u"""]);

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

    google_chart += u"""
    <div class="container-fluid">
    <div id="%s"></div>
    </div>
    """ %div_id

    return google_chart
