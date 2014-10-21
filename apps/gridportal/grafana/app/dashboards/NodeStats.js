var filter = "nid = " + ARGS.nid + " and gid = " + ARGS.gid;

return {
  "title": "Grafana",
  "tags": [],
  "style": "light",
  "timezone": "browser",
  "editable": false,
  "rows": [
    {
      "title": "CPU Information",
      "height": "250px",
      "editable": false,
      "collapse": false,
      "collapsable": true,
      "panels": [
        {
          "span": 6,
          "editable": false,
          "type": "graph",
          "x-axis": true,
          "y-axis": true,
          "scale": 1,
          "y_formats": [
            "short",
            "short"
          ],
          "grid": {
            "max": null,
            "min": null,
            "leftMax": null,
            "rightMax": null,
            "leftMin": null,
            "rightMin": null,
            "threshold1": null,
            "threshold2": null,
            "threshold1Color": "rgba(216, 200, 27, 0.27)",
            "threshold2Color": "rgba(234, 112, 112, 0.22)"
          },
          "resolution": 100,
          "lines": true,
          "fill": 1,
          "linewidth": 2,
          "points": false,
          "pointradius": 5,
          "bars": false,
          "stack": true,
          "spyable": true,
          "options": false,
          "legend": {
            "show": true,
            "values": false,
            "min": false,
            "max": false,
            "current": false,
            "total": false,
            "avg": false
          },
          "interactive": true,
          "legend_counts": true,
          "timezone": "browser",
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
              "column": "cpu.percent",
              "series": "system",
              "query": "",
              "alias": "CPU",
              "condition_filter": true,
              "condition_key": "nid",
              "condition_op": "=",
              "condition_value": ARGS.nid + " and gid = " + ARGS.gid
            }
          ],
          "aliasColors": {},
          "aliasYAxis": {},
          "title": "CPU Percent",
          "datasource": null,
          "renderer": "flot",
          "annotate": {
            "enable": false
          }
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
            "none",
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
            "threshold2Color": "rgba(234, 112, 112, 0.22)",
            "thresholdLine": false
          },
          "annotate": {
            "enable": false
          },
          "resolution": 100,
          "lines": false,
          "fill": 2,
          "linewidth": 1,
          "points": false,
          "pointradius": 5,
          "bars": true,
          "stack": true,
          "legend": {
            "show": true,
            "values": false,
            "min": false,
            "max": false,
            "current": false,
            "total": false,
            "avg": false,
            "alignAsTable": false
          },
          "percentage": true,
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
              "column": "cpu.time.system",
              "series": "system",
              "query": filter,
              "alias": "System",
              "interval": "5m"
            },
            {
              "function": "mean",
              "column": "cpu.time.user",
              "series": "system",
              "query": filter,
              "alias": "User",
              "interval": "5m"
            },
            {
              "function": "mean",
              "column": "cpu.time.idle",
              "series": "system",
              "query": filter,
              "alias": "Idle",
              "interval": "5m"
            },
            {
              "function": "mean",
              "column": "cpu.time.iowait",
              "series": "system",
              "query": filter,
              "alias": "IO Wait",
              "interval": "5m"
            }
          ],
          "aliasColors": {},
          "aliasYAxis": {},
          "title": "CPU Time"
        }
      ],
      "notice": false
    },
    {
      "title": "Memory Information",
      "height": "250px",
      "editable": false,
      "collapse": false,
      "panels": [
        {
          "span": 12,
          "editable": false,
          "type": "graph",
          "datasource": null,
          "renderer": "flot",
          "x-axis": true,
          "y-axis": true,
          "scale": 1,
          "y_formats": [
            "bytes",
            "short"
          ],
          "grid": {
            "leftMax": null,
            "rightMax": null,
            "leftMin": 0,
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
          "linewidth": 2,
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
              "column": "memory.free * 1024 * 1024",
              "series": "system",
              "query": filter,
              "alias": "Free",
              "hide": false,
              "interval": "1m"
            },
            {
              "function": "mean",
              "column": "memory.used * 1024 * 1024",
              "series": "system",
              "query": filter,
              "alias": "Used",
              "interval": "1m"
            }
          ],
          "aliasColors": {},
          "aliasYAxis": {},
          "title": "Memory",
          "leftYAxisLabel": ""
        }
      ]
    },
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
              "column": "network.kbytes.recv * 1024",
              "series": "system",
              "query": filter,
              "interval": "1m",
              "alias": "Received"
            },
            {
              "function": "difference",
              "column": "network.kbytes.send * 1024",
              "series": "system",
              "query": filter,
              "interval": "1m",
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
              "column": "network.error.in",
              "series": "system",
              "query": filter,
              "interval": "1m",
              "alias": "In"
            },
            {
              "function": "mean",
              "column": "network.error.out",
              "series": "system",
              "query": filter,
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

