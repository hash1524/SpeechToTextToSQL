import subprocess
import sqlite3
import pandas as pd
import sqlalchemy as sq
import os
command="python3 -m ln2sql.main -d database_store/school.sql -l lang_store/english.csv -j output.json -i '{}'"
input_query=input('prompt here please: ')
prompt=command.format(input_query)
returned_text=subprocess.check_output(prompt,shell=True,universal_newlines=True)
#print("the query is {}".format(returned_text))
connections=sqlite3.connect("school.db")
cursor=connections.cursor()
cursor.execute(returned_text)
data=cursor.fetchall()
column_names=list(map(lambda x: x[0],cursor.description))
connections.close()

list_of_elements=[]
for i in data:
    dict_of_elements={}
    for j in column_names:
        dict_of_elements[j.replace(".","")]=i[column_names.index(j)]
    list_of_elements.append(dict_of_elements)
#print(list_of_elements)


dict_keys=list_of_elements[0].keys()
list_keys=[]
for key in dict_keys:
    list_keys.append(key)
for i in list_keys:
    i=i.replace(".","")

JSON_bar_chart="""{
  "$schema": "https://vega.github.io/schema/vega/v5.json",
  "description": "A basic bar chart example, with value labels shown upon mouse hover.",
  "width": 400,
  "height": 200,
  "padding": 5,

  "data": [
    {
      "name": "table",
      "values": """+str(list_of_elements)+"""
    }
  ],

  "signals": [
    {
      "name": "tooltip",
      "value": {},
      "on": [
        {"events": "rect:mouseover", "update": "datum"},
        {"events": "rect:mouseout",  "update": "{}"}
      ]
    }
  ],

  "scales": [
    {
      "name": "xscale",
      "type": "band",
      "domain": {"data": "table", "field": """+'"{}"'.format(list_keys[0])+"""},
      "range": "width",
      "padding": 0.05,
      "round": true
    },
    {
      "name": "yscale",
      "domain": {"data": "table", "field": """+'"{}"'.format(list_keys[1])+"""},
      "nice": true,
      "range": "height"
    }
  ],

  "axes": [
    { "orient": "bottom", "scale": "xscale" },
    { "orient": "left", "scale": "yscale" }
  ],

  "marks": [
    {
      "type": "rect",
      "from": {"data":"table"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": """+'"{}"'.format(list_keys[0])+"""},
          "width": {"scale": "xscale", "band": 1},
          "y": {"scale": "yscale", "field": """+'"{}"'.format(list_keys[1])+"""},
          "y2": {"scale": "yscale", "value": 0}
        },
        "update": {
          "fill": {"value": "steelblue"}
        },
        "hover": {
          "fill": {"value": "red"}
        }
      }
    },
    {
      "type": "text",
      "encode": {
        "enter": {
          "align": {"value": "center"},
          "baseline": {"value": "bottom"},
          "fill": {"value": "#333"}
        },
        "update": {
          "x": {"scale": "xscale", "signal": "tooltip.category", "band": 0.5},
          "y": {"scale": "yscale", "signal": "tooltip.amount", "offset": -2},
          "text": {"signal": "tooltip.amount"},
          "fillOpacity": [
            {"test": "datum === tooltip", "value": 0},
            {"value": 1}
          ]
        }
      }
    }
  ]
}
"""

JSON_pie_chart="""{
  "$schema": "https://vega.github.io/schema/vega/v5.json",
  "description": "A basic pie chart example.",
  "width": 200,
  "height": 200,
  "autosize": "none",

  "signals": [
    {
      "name": "startAngle", "value": 0,
      "bind": {"input": "range", "min": 0, "max": 6.29, "step": 0.01}
    },
    {
      "name": "endAngle", "value": 6.29,
      "bind": {"input": "range", "min": 0, "max": 6.29, "step": 0.01}
    },
    {
      "name": "padAngle", "value": 0,
      "bind": {"input": "range", "min": 0, "max": 0.1}
    },
    {
      "name": "innerRadius", "value": 0,
      "bind": {"input": "range", "min": 0, "max": 90, "step": 1}
    },
    {
      "name": "cornerRadius", "value": 0,
      "bind": {"input": "range", "min": 0, "max": 10, "step": 0.5}
    },
    {
      "name": "sort", "value": false,
      "bind": {"input": "checkbox"}
    }
  ],

  "data": [
    {
      "name": "table",
      "values": """+str(list_of_elements)+""",
      "transform": [
        {
          "type": "pie",
          "field": """+'"{}"'.format(list_keys[0])+""",
          "startAngle": {"signal": "startAngle"},
          "endAngle": {"signal": "endAngle"},
          "sort": {"signal": "sort"}
        }
      ]
    }
  ],

  "scales": [
    {
      "name": "color",
      "type": "ordinal",
      "domain": {"data": "table", "field": """+'"{}"'.format(list_keys[1])+"""},
      "range": {"scheme": "category20"}
    }
  ],

  "marks": [
    {
      "type": "arc",
      "from": {"data": "table"},
      "encode": {
        "enter": {
          "fill": {"scale": "color", "field": """+'"{}"'.format(list_keys[1])+"""},
          "x": {"signal": "width / 2"},
          "y": {"signal": "height / 2"}
        },
        "update": {
          "startAngle": {"field": "startAngle"},
          "endAngle": {"field": "endAngle"},
          "padAngle": {"signal": "padAngle"},
          "innerRadius": {"signal": "innerRadius"},
          "outerRadius": {"signal": "width / 2"},
          "cornerRadius": {"signal": "cornerRadius"}
        }
      }
    }
  ]
}
"""

JSON_bar_chart=JSON_bar_chart.replace("'",'"')
JSON_pie_chart=JSON_pie_chart.replace("'",'"')

#print(JSON_bar_chart)
choice_of_chart=int(input('Please choose a chart from below:\n1.Bar Chart\n2.Pie Chart\nchoice: '))

with open('visualize.json', 'w') as outfile:
    if choice_of_chart==1:
      outfile.write(JSON_bar_chart)
    elif choice_of_chart==2:
      outfile.write(JSON_pie_chart)

os.system('vg2pdf visualize.json trail.pdf')
os.system('open trail.pdf')