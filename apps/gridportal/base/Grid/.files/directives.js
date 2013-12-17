angular.module('jsmonitor')
    .directive('chart', function () {
    return {
        restrict: 'A',
        link: function (scope, elem, attrs) {
                var updateChart = function(data){
                    elem.empty();
            if (!data) {return;};
                    $.jqplot(attrs.id,[ data ],{
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
                      }
                    ,
                            yaxis:{
                                    tickOptions:{
                                        formatString:'%.2f'
                                    }
                                }
                            },
                            cursor: {
                                    show: true,
                                    zoom:true
                                }
                            }
                            );
                }
        
                scope.$watch(attrs.ngModel, function(newValue, oldValue) {
                    updateChart(newValue);
                }, true);
            }
        }
    }
        )
;
  