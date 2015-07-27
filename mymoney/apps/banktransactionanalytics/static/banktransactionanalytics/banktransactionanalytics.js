if (typeof chart_data !== 'undefined') {

    (function (chart_data) {
        var data = chart_data.data
        var options = chart_data.options || {}

        window.onload = function(){
            var ctx = document.getElementById("chart-area").getContext("2d");

            switch (chart_data.type) {

                case 'doughtnut':
                    options['tooltipTemplate'] = "<%=label %>: <%=value + '%' %>";
                    var chart = new Chart(ctx).Doughnut(data, options);
                    break;

                case 'polar':
                    options['tooltipTemplate'] = "<%=label %>: <%=value + '%' %>";
                    var chart = new Chart(ctx).PolarArea(data, options);
                    break;

                case 'pie':
                    options['tooltipTemplate'] = "<%=label %>: <%=value + '%' %>";
                    var chart = new Chart(ctx).Pie(data, options);
                    break;

                case 'bar':
                    var chart = new Chart(ctx).Bar(data, options);
                    break;

                case 'line':
                    var chart = new Chart(ctx).Line(data, options);
                    break;

                case 'radar':
                    var chart = new Chart(ctx).Radar(data, options);
                    break;
            }
        }
    })(chart_data);
}
