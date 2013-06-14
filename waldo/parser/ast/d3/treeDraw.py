#!/usr/bin/env python

'''
Most of the code in this module is directly adapted from
examples/tree/tree.js and examples/tree/tree.css from the d3 examples
folder located here:
http://mbostock.github.com/d3/
'''


def prettyDrawTree(filename,data,pathToD3,width=5000,height=3000):
    page = generatePage(data,pathToD3,width,height);
    filer = open(filename,'w');
    filer.write(page);
    filer.flush();
    filer.close();


def generatePage(data, pathToD3,width,height):
    
    text = '''
   <html>
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <script type="text/javascript" src="''' + pathToD3 + '''/d3.v2.js"></script>

<style type="text/css">
.node circle {
  fill: #fff;
  stroke: steelblue;
  stroke-width: 1.5px;
}

.node {
  font: 8px sans-serif;
}

.link {
  fill: none;
  stroke: #ccc;
  stroke-width: 1.5px;
}
</style>

  </head>
  <body>
    <div id="chart"></div>

<script>
var w = ''' + str(width) + ''',
    h = ''' + str(height) + ''';

var tree = d3.layout.tree()
    .size([w, h/3 ]);

var VERTICAL_SPACING = 8;


var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.x, d.y]; });

var vis = d3.select("#chart").append("svg")
    .attr("width", w)
    .attr("height", h)
    .append("g")
    .attr("transform", "translate(-40, 40)");


function exec (json) {
  var nodes = tree.nodes(json);

  //draws the connections between the items  
  var link = vis.selectAll("path.link")
      .data(tree.links(nodes))
      .enter().append("path")
      .attr("class", "link")
      .attr("d", diagonal);

    
  //controls where the circles and text actually get drawn.  
  var node = vis.selectAll("g.node")
      .data(nodes)
      .enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

  node.append("circle")
      .attr("r", 4.5); //circle radius


  node.append("text")
      .attr("dx", function(d) {
       if (d.children)
          -8;
       else
       {
          if(d.drawHigh)
            return 2;
       }
       return -8;
       })
      .attr("dy", function(d) { if (d.drawHigh) return -8; return 12;})
      .attr("text-anchor", function(d) { return d.children ? "end" : "start"; })
      .text(function(d) { return d.name; });


  //draws value
  node.append("text")
      .attr("dx", function(d) {
       if (d.children)
          -8;
       else
       {
          if(d.drawHigh)
            return 2;
       }
       return -8;
       })
      .attr("dy", function(d)
                  {
                      if (d.drawHigh)
                          return -8 + 1*VERTICAL_SPACING;
                      return 12 + 1*VERTICAL_SPACING;
                  })
      .attr("text-anchor", function(d) { return d.children ? "end" : "start"; })
      .text(function(d)
            {
               if(d.value)
                 return d.value;
               return '--';
            });

  //draws type
  node.append("text")
      .attr("dx", function(d) {
       if (d.children)
          -8;
       else
       {
          if(d.drawHigh)
            return 2;
       }
       return -8;
       })
      .attr("dy", function(d)
                  {
                      if (d.drawHigh)
                          return -8 + 2*VERTICAL_SPACING;
                      return 12 + 2*VERTICAL_SPACING;
                  })
      .attr("text-anchor", function(d) { return d.children ? "end" : "start"; })
      .text(function(d)
            {
               if(d.type)
                 return d.type;
               return '--';
            });

  //draws slice annotation name
  node.append("text")
      .attr("dx", function(d) {
       if (d.children)
          -8;
       else
       {
          if(d.drawHigh)
            return 2;
       }
       return -8;
       })
      .attr("dy", function(d)
                  {
                      if (d.drawHigh)
                          return -8 + 3*VERTICAL_SPACING;
                      return 12 + 3*VERTICAL_SPACING;
                  })
      .attr("text-anchor", function(d) { return d.children ? "end" : "start"; })
      .text(function(d)
            {
               if(d.sliceAnnotationName)
                 return d.sliceAnnotationName;
               return '--';
            });


  //draws slice annotation type name
  node.append("text")
      .attr("dx", function(d) {
       if (d.children)
          -8;
       else
       {
          if(d.drawHigh)
            return 2;
       }
       return -8;
       })
      .attr("dy", function(d)
                  {
                      if (d.drawHigh)
                          return -8 + 4*VERTICAL_SPACING;
                      return 12 + 4*VERTICAL_SPACING;
                  })
      .attr("text-anchor", function(d) { return d.children ? "end" : "start"; })
      .text(function(d)
            {
               if(d.sliceAnnotationType)
                 return d.sliceAnnotationType;
               return '--';
            });

}


exec(getJSON());


function getJSON()
{
    return ''' + data + ''';
}

</script>


  </body>
</html>

    '''
    return text;
