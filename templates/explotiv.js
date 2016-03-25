var width = 800,
    height = 800,
    legend_width = 50,
    legend_height = 500,
    legend_items = 20,
    selected_node,
    radius = (Math.min(width, height) / 2)-20,
    colormap = d3_scale.scaleViridis().domain([0.0,1.0]),
    majorGroupColormap = d3.scale.category20();

var major_groups = d3.set([6656, 40674, 32561, 7898, 4751]);


// https://github.com/wbkd/d3-extended
d3.selection.prototype.moveToFront = function() {  
  return this.each(function(){
    this.parentNode.appendChild(this);
  });
};


d3.selection.prototype.moveToBack = function() {  
    return this.each(function() { 
        var firstChild = this.parentNode.firstChild; 
        if (firstChild) { 
            this.parentNode.insertBefore(this, firstChild); 
        } 
    });
};


function dictValues(dict) {
    return Object.keys(dict).map(
        function(key) {
            return dict[key];
        }
    );
}


/* Return the mean of a dictionary's values
 */
function dictMean(dict) {
    return d3.mean(dictValues(dict));
}


function phyloViz(data) {

    //console.log(data);

    var legendContainer = d3.select("#explotiv-legend").append("svg")
                            .attr("width", 100)
                            .attr("height", 800)
                            .append("g")
                            .style("stroke", "black")
                            .attr("transform", 
                                  "translate(" + (((100-legend_width)/2)-2) + "," + (800-legend_height)/2 + ")");

    var legendData = d3.range(0,1,1/legend_items).reverse().map(function (i) {
                            return { 'height': legend_height / legend_items,
                                     'width': legend_width,
                                     'yloc': i * legend_height,
                                     'xloc': 0,
                                     'val': 1-i};
                      });

    var legendItems = legendContainer.selectAll("g")
                      .data(legendData).enter().append("g")
                              .attr("x", function (d) { return d.xloc; })
                              .attr("y", function (d) { return d.yloc; })
                              .attr("height", function (d) { return d.height; })
                              .attr("width", function (d) { return d.width * 2; })

    legendItems.append("text").attr("x", function (d) { return d.xloc + legend_width + 3; })
                              .attr("y", function (d) { return d.yloc; })
                              .attr("dy", ".35em")
                              .text(function (d) { return d.i; });
                       

    legendItems.append("rect").attr("x", function (d) { return d.xloc; })
                              .attr("y", function (d) { return d.yloc; })
                              .attr("height", function (d) { return d.height; })
                              .attr("width", function (d) { return d.width; })
                              .style("fill", function(d) { return colormap(d.val); })


    plotHistogram(null);

    var tip = d3.tip().attr('class', 'd3-tip')
        .offset(function() {
            return [this.getBBox().height / 2, -this.getBBox().width/2]
        }).html(function(d) { return d.organism + ' (<em>P</em>=' + +(data[d.taxid]).toFixed(3) + ')'; });


    var svg = d3.select("#explotiv-chart").append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
        .call(tip);


    var partition = d3.layout.partition()
        .size([2 * Math.PI, radius * radius])
        .value(function(d) { return data[d.taxid]; });


    var arc = d3.svg.arc()
        .startAngle(function(d)  { return d.x; })
        .endAngle(function(d)    { return d.x + d.dx; })
        .innerRadius(function(d) { return Math.sqrt(d.y); })
        .outerRadius(function(d) { return Math.sqrt(d.y + d.dy); });

    var path;
    d3.json("{{ url_for('static', filename='odb8_tree.json') }}", function(error, root) {
        if (error) throw error;

        path = svg.datum(root).selectAll("path").data(partition.nodes)
        path.enter().append("path")
            .attr("id", function(d) { return "node" + d.taxid; })
            .attr("class", function(d) { 
                return major_groups.has(d.taxid) ? "major_node" : "node"; 
            })
            .attr("display", function(d) { return d.depth ? null : "none"; }) // hide inner ring
            .attr("d", arc)
            .style("stroke", "#fff")
            .style("fill", function(d) {
                return colormap(data[d.taxid]);
            }).style("fill-rule", "evenodd")
            .on('mouseover', hoverInfoEnter)
            .on('mouseout', hoverInfoExit)
            .on('click', nodeClick);
        addMajorGroupMarkers();
    })


    function addMajorGroupMarkers() {
        console.log(d3.selectAll('.major_node').data());
        nodes = d3.selectAll('.major_node').data()
        nodes.map(function (d, i) {
                svg.append('path')
                .attr('d', d3.svg.arc()
                           .startAngle(d.x)
                           .endAngle(d.x+d.dx)
                           .innerRadius(radius)
                           .outerRadius(radius+20))
                .attr('id', 'major_node'+i)
                .style("fill", majorGroupColormap(i))
                .moveToBack()
        });
        svg.selectAll('.major_label').data(nodes)
            .enter().append('text')
            .attr('class', 'major_label')
            .attr('x', 5)
            .attr('dy', 15)
            .append('textPath')
            .attr('xlink:href', function(d,i) { return '#major_node'+i; })
            .text(function(d) { return d.organism; });
    }

    function hoverInfoEnter(d) {
        if (!selected_node) {
            d3.select("#hoverinfotext").remove();
            d3.select("#hoverinfodiv").append("span")
                                  .attr("id", "hoverinfotext")
                                  .html(d.organism + ' (<em>Score</em>=' + +(data[d.taxid]).toFixed(3) + ')');
        }
    }

    function hoverInfoExit(d) {
        d3.select("#hoverinfotext").remove();
    }

    function nodeClick(d) {

        removeSelection();
        selected_node = d;
        addSelection(selected_node);
        plotHistogram(selected_node);

    }

    function addSelection(d) {
        svg.append("path").attr("id", "selection")
                          .attr("d", d3.svg.arc().startAngle(d.x)
                                                 .endAngle(d.x + d.dx)
                                                 .innerRadius(Math.sqrt(d.y))
                                                 .outerRadius(radius))
                          .style("fill", "rgba(0,0,0,0.2)")
                          .on("click", removeSelection);
        //d3.select("#selection").moveToBack();
    }

    function removeSelection() {
        d3.select("#selection").remove();
        selected_node = 0;
        plotHistogram(null)
    }

    function plotHistogram(node) {
        chart_div = document.getElementById('histogram-chart');

        url = node ? '/node-data/' + node.taxid : '/node-means';
        organism = node ? node.organism : 'all Mean Scores';
        color = node ? colormap(data[node.taxid]) : colormap(0.5);

        d3.json(url, function(error, root) {
            if (error) throw error;

            chart_layout = { title: 'Score Distribution for ' + organism,
                             xaxis: { title: 'Score' },
                             yaxis: { title: 'Count' } }

            if (chart_div.data) {
                console.log('redraw');
                chart_div.data[0].x = dictValues(root.data);
                chart_div.data[0].marker.color = color;
                chart_div.layout.title = chart_layout.title;
                Plotly.redraw(chart_div);
            } else {
                chart_data = [
                    { x: dictValues(root.data),
                      type: 'histogram',
                      marker: { color: colormap(color),
                                opacity: 0.75
                     }}
                ]
                Plotly.plot(chart_div, chart_data, chart_layout);
            }
        });
    }

}


function phyloInit() {
    d3.json("{{ url_for('phylo_pane.node_means') }}", function(error, obj) {
        if (error) throw error;
        phyloViz(obj.data);
    });
}

function save() {
    savePlot(4.0, "{{name}}", "{{ url_for('static', filename='style.css') }}", 'svg');
}

function savePlot(scaling, filename, stylesheetfile, format) {

    // First lets get the stylesheet
    var sheetlength = stylesheetfile.length;
    var style = document.createElementNS("http://www.w3.org/1999/xhtml", "style");
    style.textContent += "<![CDATA[\n";
    for (var i=0;i<document.styleSheets.length; i++) {
    str = document.styleSheets[i].href;
    if(null == str) continue;

    if (str.substr(str.length-sheetlength)==stylesheetfile){
            var rules;
            if(document.styleSheets[i].cssRules) {
                rules = document.styleSheets[i].cssRules;
            } else if (document.styleSheets[i].rules) {
                rules = document.styleSheets[i].rules;
            }
            if(rules) {
                for (var j=0; j<rules.length;j++){
                    style.textContent += (rules[j].cssText + "\n");
                }
            }
            break;
        }
    }
    style.textContent += "]]>";

    // Now we clone the SVG element, resize and scale it up
    var containertag = document.getElementById('explotiv-chart');
    var clonedSVG = containertag.cloneNode(true);
    var svg = clonedSVG.getElementsByTagName("svg")[0];


    svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    console.log(svg)

    var content = clonedSVG.innerHTML.trim();

    if(format == 'svg') {
    var a = document.createElement('a');
    a.href = "data:application/octet-stream;base64;attachment," + btoa(content);
    a.download = filename + ".svg";
    a.click();

    } 
}
