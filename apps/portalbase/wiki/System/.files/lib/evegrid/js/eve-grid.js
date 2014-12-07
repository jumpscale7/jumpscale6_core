var eveModule = angular.module('eveModule', []);
eveModule.directive('eveGrid', function($http, $filter) {
    return {
        restrict: 'EA',
        scope: true,
        template:'<table class="table table-striped" cellspacing="0" width="100%"><tfoot><tr><td><button class="delete btn btn-danger" style="padding: 2px 12px;">Delete</button><button class="search btn btn-primary" style="padding: 2px 12px; margin-left: 3px;">Search</button></td></tr></tfoot></table>',
        link: function (scope, element, attrs, ctrl) {
            var selected = [];
            var checkedRows = [];
            $http({
                url: 'http://' + attrs['eveUrl'] + attrs['eveSpecPath'],
                method: 'GET',
            }).then(function(data) {
                scope.schema = data.data;
                var columns = [{
                    data: null, 
                    orderable: false, 
                    defaultContent: '<input class="rowCheck" type="checkbox"></input>', 
                    'title': '<input class="allCheck" type="checkbox"></input>'
                }];
                var showFields = [];
                var eveFields = scope.schema.domains[attrs["eveEntity"]]['/' + attrs["eveEntity"]].POST.params;

                for (var i = 0; i < JSON.parse( attrs['columns'] ).length; i++) {
                    var field = _.findWhere(eveFields, {name: JSON.parse( attrs['columns'] )[i].data});
                    if(field){
                        field.header = JSON.parse( attrs['columns'] )[i].header;
                        field.format = JSON.parse( attrs['columns'] )[i].format;
                        showFields.push(field);
                    }
                };
                columns = columns.concat(showFields
                    .filter(function(p) { return p.name.indexOf('.') == -1; })
                    .map(function(param, mapIndex) {
                        var column = {};
                        column.data = param.name;
                        column.title = param.header;
                        column.class = "details-control";
                        column.defaultContent = '';
                        column.type = param.type;
                        column.render = function(data, type, row) {
                            var columnText = data;
                            
                            var datetimeFields = attrs["datetimeFields"].split(',');
                            if( datetimeFields.indexOf(column.data) > -1 ){
                                column.type = "datetime";
                                columnText = moment(data * 1000).format('DD/MM/YYYY hh:mm:ss');
                            }

                            if(param.format){
                                columnText = param.format.replace(RegExp('{' + column.data + '}', 'g'), columnText);
                                for (var i = 0; i < scope.columns.length; i++) {
                                    columnText = columnText.replace(RegExp('{' + scope.columns[i].data + '}', 'g'), row[scope.columns[i].data]);
                                };
                            }
                            return columnText;
                        },
                        column.getFilter = function(val, val2) {
                            if (val && val.length > 0 && column.type == 'string')
                                return '"' + column.data + '":{"$regex":"' + val + '", "$options": "i"}';
                            else if (column.type == 'date' || column.type == 'datetime') {
                                var predicate = [];
                                if (val && val.length > 0) {
                                    val = moment(val, 'DD/MM/YYYY hh:mm:ss').format('X');
                                    predicate.push('"$gte":' + val);
                                }
                                if (val2 && val2.length > 0) {
                                    val2 = moment(val2, 'DD/MM/YYYY hh:mm:ss').format('X');
                                    predicate.push('"$lte":' + val2);
                                }

                                if (predicate.length == 0)
                                    return '';
                                return '"' + column.data + '":' + '{' + predicate.join(', ') + '}';
                            }
                            else if (column.type == 'integer' || column.type == 'float'){
                                var predicate = [];
                                if (val && val.length > 0)
                                    predicate.push('"$gte":' + val);
                                if (val2 && val2.length > 0)
                                    predicate.push('"$lte":' + val2);

                                if (predicate.length == 0)
                                    return '';
                                return '"' + column.data + '":' + '{' + predicate.join(', ') + '}';
                            }
                            else
                                return '';

                        }
                        return column;
                    }));
                scope.columns = columns;
                scope.dataTable = angular.element('#' + attrs["eveEntity"] + '-container table').DataTable( {
                    processing: true,
                    serverSide: true,
                    "columnDefs": [
                        { className: "center", "targets": [ 0 ] }
                    ],
                    "rowCallback": function(row, data) {
                        if ($.inArray(data._id, selected) !== -1) {
                            $(row).addClass('selected');
                            $(row).find('.rowCheck').prop('checked', true);
                        }
                    },
                    "columns": scope.columns,
                    ajax: function (requestData, callback, settings) {
                        requestData.page = requestData.start / requestData.length + 1;
                        requestData.max_results = requestData.length;
                        var where = [];

                        angular.element('#' + attrs["eveEntity"] + '-container table .search').click(function() {
                            where.length = 0;
                            for (var i = 1; i < scope.columns.length; i++){
                                var val = angular.element( '#' + attrs["eveEntity"] + '-container table tfoot td:eq(' + i + ') input:first' ).val();
                                var val2 = angular.element( '#' + attrs["eveEntity"] + '-container table tfoot td:eq(' + i + ') input:nth(1)' ).val();
                                where.push(scope.columns[i].getFilter(val, val2));
                            };
                            if (where.length > 0){
                                requestData.where = "{" + where.filter(function(s) {return s.length > 0; }).join(', ') + "}";
                                $http({
                                    url: 'http://' + attrs['eveUrl'] + '/' + attrs["eveEntity"],
                                    method: 'GET',
                                    cache: false,
                                    params: requestData
                                }).then(function(data) {
                                    data = data.data;
                                    if (data['_meta']) {
                                        data['recordsTotal'] = data['_meta']['total'];
                                        data['iTotalRecords'] = data['_meta']['total'];
                                        data['iTotalDisplayRecords'] = data['_meta']['total'];
                                    } else {
                                        data['recordsTotal'] = 0;
                                        data['iTotalRecords'] = 0;
                                        data['iTotalDisplayRecords'] = 0;
                                    }
                                    data['data'] = data['_items'];
                                    callback(data);
                                });
                            }
                        });

                        if (requestData.order && requestData.order.length > 0) {
                            sort_field = scope.columns[requestData.order[0].column].data;
                            sort_dir = requestData.order[0].dir == 'desc' ? -1 : 1
                            requestData.sort = '[("' + sort_field + '",' + sort_dir + ')]';
                        }

                        if(requestData.draw == 1){

                            $http({
                                url: 'http://' + attrs['eveUrl'] + '/' + attrs["eveEntity"],
                                method: 'GET',
                                cache: false,
                                params: requestData
                            }).then(function(data) {
                                data = data.data;
                                if (data['_meta']) {
                                    data['recordsTotal'] = data['_meta']['total'];
                                    data['iTotalRecords'] = data['_meta']['total'];
                                    data['iTotalDisplayRecords'] = data['_meta']['total'];
                                } else {
                                    data['recordsTotal'] = 0;
                                    data['iTotalRecords'] = 0;
                                    data['iTotalDisplayRecords'] = 0;
                                }
                                data['data'] = data['_items'];
                                callback(data);
                            });

                        }
                    },
                } );
                
                

                for (var i = 1; i < scope.columns.length; i++) {
                    var datetimeFields = attrs["datetimeFields"].split(',');
                    if(scope.columns[i].sType == "integer" || scope.columns[i].sType == "float"){
                        if( datetimeFields.indexOf(scope.columns[i].data) > -1 ){
                            angular.element('<td style="padding-left: 0;">' +
                                '<input type="text" class="searchInput datetimeInput" placeholder=">=" data-date-format="DD/MM/YYYY hh:mm:ss"/>' +
                                '<input type="text" class="searchInput datetimeInput" placeholder="<=" data-date-format="DD/MM/YYYY hh:mm:ss"/>' +
                                '</td>')
                                .appendTo('#' + attrs["eveEntity"] + '-container table tfoot tr')
                                .on( 'keyup change', function () {
                                    scope.dataTable
                                        .column( i )
                                        // .search( angular.element(this).find('input').val() )
                                        .draw();
                                } );
                        }else{
                            angular.element('<td style="padding-left: 0;">' +
                                '<input type="text" class="searchInput" placeholder=">=" />' +
                                '<input type="text" class="searchInput" placeholder="<=" />' +
                                '</td>')
                                .appendTo('#' + attrs["eveEntity"] + '-container table tfoot tr')
                                .on( 'keyup change', function () {
                                    scope.dataTable
                                        .column( i )
                                        // .search( angular.element(this).find('input').val() )
                                        .draw();
                                } );
                        }
                    }
                    else{
                        angular.element('<td style="padding-left: 0;"><input type="text" class="searchInput" /></td>')
                            .appendTo('#' + attrs["eveEntity"] + '-container table tfoot tr')
                            .on( 'keyup change', function () {
                                scope.dataTable
                                    .column( i )
                                    .search( angular.element(this).find('input').val() )
                                    .draw();
                            } );
                    }     
                };

                $('.datetimeInput').datetimepicker();

                angular.element('.eve-grid-container .rowCheck').live('click' , function() {
                    var currentRow = $(this).parents('tr');
                    var id = scope.dataTable.row(currentRow).data()._id;
                    var index = $.inArray(id, selected);
                    if (index === -1) {
                        selected.push(id);
                    } else {
                        selected.splice(index, 1);
                    }
                    $(currentRow).toggleClass('selected');

                    var checkedBoxes = angular.element('#' + attrs["eveEntity"] + '-container table').find('tbody tr .rowCheck:checked').length;
                    var totalRowsOnPage = angular.element('#' + attrs["eveEntity"] + '-container table').find('tbody tr .rowCheck').length;
                    if(totalRowsOnPage == checkedBoxes){
                        angular.element('#' + attrs["eveEntity"] + '-container table').find('.allCheck').prop('checked', true);
                    }else{
                        angular.element('#' + attrs["eveEntity"] + '-container table').find('.allCheck').prop('checked', false);
                    }
                });
            });

            angular.element('#' + attrs["eveEntity"] + '-container table').on('click', '.allCheck', function() {
                var allCheck = this;
                angular.element(this).parents('table').find('.rowCheck').each(function() {
                    var currentRow = angular.element(this).parents('tr');
                    var id = scope.dataTable.row(currentRow).data()._id;
                    var index = $.inArray(id, selected);
                    if (index === -1) {
                        selected.push(id);
                    } else {
                        selected.splice(index, 1);
                    }
                    this.checked = allCheck.checked;
                    if (this.checked)
                        angular.element(this).parents('tr').addClass('selected');
                    else
                        angular.element(this).parents('tr').removeClass('selected');
                });
            });

            angular.element('.searchInput').live('focus', function() {
                $(this).animate({ width: 116 }, 'medium');
            }).live('blur', function() {
                $(this).animate({ width: 60 }, 'medium');
            });
            
            angular.element('#' + attrs["eveEntity"] + '-container table .delete').on('click', function() {
                var trs = angular.element('#' + attrs["eveEntity"] + '-container table input[type=checkbox]:checked').parents('tr');
                var finishedRequests = 0;
                trs.each(function(i, tr) {
                    var data = scope.dataTable.row(tr).data();
                    if(data){
                        $http({
                            url: 'http://' + attrs['eveUrl'] + '/' + attrs["eveEntity"] + '/'+ data._id,
                            type: 'POST',
                            headers: {
                                'X-HTTP-Method-Override': 'DELETE',
                                'If-Match': data._etag
                            }
                        }).then(function() {
                            finishedRequests++;
                            if (finishedRequests == trs.length) {
                                scope.dataTable.draw();
                            }
                        });
                    }
                });
            });
            
            angular.element('#' + attrs["eveEntity"] + '-container table').on( 'processing.dt', function (e, settings, processing ) {
                var checkedBoxes = angular.element('#' + attrs["eveEntity"] + '-container table').find('tbody tr .rowCheck:checked').length;
                var totalRowsOnPage = angular.element('#' + attrs["eveEntity"] + '-container table').find('tbody tr .rowCheck').length;
                if(checkedBoxes == totalRowsOnPage && checkedBoxes > 0 && processing == false){
                    angular.element('#' + attrs["eveEntity"] + '-container table').find('.allCheck').prop('checked', true);
                }else{
                    angular.element('#' + attrs["eveEntity"] + '-container table').find('.allCheck').prop('checked', false);
                }

            } );

        }
    }
});