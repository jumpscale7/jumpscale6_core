angular.module('jumpscale')
    .directive('chart', function ($timeout, $http) {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {

            var timeoutId;
            var selectedStatistic = attrs.ngStat;
            scope.statisticsData = [];


            var updateChart = function(data){
                if (scope.plot){scope.plot.destroy();}
                element.empty();
                if (!data) {return;};
                scope.plot = $.jqplot(attrs.id,[ data ],{
                    axesDefaults: {
                        tickRenderer: $.jqplot.CanvasAxisTickRenderer ,
                        tickOptions: {
                            fontSize: '10pt'
                        }
                    },
                axes:{
                    xaxis:
                        {
                            renderer:$.jqplot.DateAxisRenderer,
                            tickOptions: {
                                formatString: '%T',
                                angle: -30
                            }
                        },
                    yaxis:
                        {
                        tickOptions:{
                            formatString:'%.2f'
                        }
                    }
                },
                rendererOptions: {
                    smooth: true
                },
                cursor: {
                            show: true,
                            zoom:true
                        }
                }
            );
            }
  
            function scheduleUpdate() {
                $http.get(attrs.ngUrl).
                    then(
                        function(result){ 

                            var now = new Date().getTime();
                            scope.statisticsData.push([now,result.data[selectedStatistic]]);
                            while (scope.statisticsData.length > 90){
                                scope.statisticsData.shift();
                            }
                            updateChart(scope.statisticsData); // update DOM
                        }); 

                // save the timeoutId for canceling
                timeoutId = $timeout(function() {
                    scheduleUpdate(); // schedule the next update
                    }, 5000);
            }
 
            element.on('$destroy', function() {
                $timeout.cancel(timeoutId);
            });
 
            // start the UI update process.
            scheduleUpdate();

        },
        scope:{}
        }
    }
        )
;
  