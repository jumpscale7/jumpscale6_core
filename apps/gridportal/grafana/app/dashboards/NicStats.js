var filter = ARGS.nid + " and gid = " + ARGS.gid + " and nic_id = '" + ARGS.name + "' ";
return {
  "title": "Grafana",
  "tags": [],
  "style": "light",
  "timezone": "browser",
  "editable": false,
  "rows": [
    {
      "title": "Network Information",
      "height": "250px",
      "editable": false,
      "collapse": false,
      "panels": [
        {
          "span": 6,
          "editable": false,
          "type": "graph",
          "datasource": null,
          "renderer": "flot",
          "x-axis": true,
          "y-axis": true,
          "scale": 1,
          "y_formats": [
            "bytes",
            "bytes"
          ],
          "grid": {
            "leftMax": null,
            "rightMax": null,
            "leftMin": null,
            "rightMin": null,
            "threshold1": null,
            "threshold2": null,
            "threshold1Color": "rgba(216, 200, 27, 0.27)",
            "threshold2Color": "rgba(234, 112, 112, 0.22)"
          },
          "annotate": {
            "enable": false
          },
          "resolution": 100,
          "lines": true,
          "fill": 0,
          "linewidth": 1,
          "points": false,
          "pointradius": 5,
          "bars": false,
          "stack": false,
          "legend": {
            "show": true,
            "values": false,
            "min": false,
            "max": false,
            "current": false,
            "total": false,
            "avg": false
          },
          "percentage": false,
          "zerofill": true,
          "nullPointMode": "connected",
          "steppedLine": false,
          "tooltip": {
            "value_type": "cumulative",
            "query_as_alias": true
          },
          "targets": [
            {
              "function": "difference",
              "column": "kbytes_recv * 1024",
              "series": "nic",
              "query": "",
              "condition_filter": true,
              "condition_key": "nid",
              "condition_op": "=",
              "condition_value": filter,
              "interval": "10m",
              "alias": "Received"
            },
            {
              "function": "difference",
              "column": "kbytes_sent * 1024",
              "series": "nic",
              "condition_filter": true,
              "condition_key": "nid",
              "condition_op": "=",
              "condition_value": filter,
              "query": "",
              "interval": "10m",
              "alias": "Sent"
            }
          ],
          "aliasColors": {},
          "aliasYAxis": {},
          "title": "Network Bandwith"
        },
        {
          "span": 6,
          "editable": false,
          "type": "graph",
          "datasource": null,
          "renderer": "flot",
          "x-axis": true,
          "y-axis": true,
          "scale": 1,
          "y_formats": [
            "short",
            "short"
          ],
          "grid": {
            "leftMax": null,
            "rightMax": null,
            "leftMin": null,
            "rightMin": null,
            "threshold1": null,
            "threshold2": null,
            "threshold1Color": "rgba(216, 200, 27, 0.27)",
            "threshold2Color": "rgba(234, 112, 112, 0.22)"
          },
          "annotate": {
            "enable": false
          },
          "resolution": 100,
          "lines": true,
          "fill": 0,
          "linewidth": 1,
          "points": false,
          "pointradius": 5,
          "bars": false,
          "stack": false,
          "legend": {
            "show": true,
            "values": false,
            "min": false,
            "max": false,
            "current": false,
            "total": false,
            "avg": false
          },
          "percentage": false,
          "zerofill": true,
          "nullPointMode": "connected",
          "steppedLine": false,
          "tooltip": {
            "value_type": "cumulative",
            "query_as_alias": true
          },
          "targets": [
            {
              "function": "mean",
              "column": "errin",
              "series": "nic",
              "query": "",
              "condition_filter": true,
              "condition_key": "nid",
              "condition_op": "=",
              "condition_value": filter,
              "interval": "1m",
              "alias": "In"
            },
            {
              "function": "mean",
              "column": "errout",
              "series": "nic",
              "query": "",
              "condition_filter": true,
              "condition_key": "nid",
              "condition_op": "=",
              "condition_value": filter,
              "interval": "1m",
              "alias": "Out"
            }
          ],
          "aliasColors": {},
          "aliasYAxis": {},
          "title": "Network Error"
        }
      ]
    }
  ],
  "pulldowns": [
    {
      "type": "filtering",
      "collapse": false,
      "notice": false,
      "enable": false
    },
    {
      "type": "annotations",
      "enable": false
    }
  ],
  "nav": [
    {
      "type": "timepicker",
      "collapse": false,
      "notice": false,
      "enable": true,
      "status": "Stable",
      "time_options": [
        "5m",
        "15m",
        "1h",
        "6h",
        "12h",
        "24h",
        "2d",
        "7d",
        "30d"
      ],
      "refresh_intervals": [
        "5s",
        "10s",
        "30s",
        "1m",
        "5m",
        "15m",
        "30m",
        "1h",
        "2h",
        "1d"
      ],
      "now": true
    }
  ],
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "templating": {
    "list": []
  },
  "version": 2
}

