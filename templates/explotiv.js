var width = 960,
    height = 700,
    radius = Math.min(width, height) / 2,
    probs,
    max_count,
    colormap;

d3.json("{{ url_for('static', filename='lamprey.taxid.probs.full.json') }}", function(error, result) {
    probs = result;
    max_prob = d3.max(Object.keys(probs).map(
        function(key) {
            return probs[key];
        })
    );
    //colormap = d3.scale.linear()
    //               .domain([0,max_prob])
    //                .range(colorbrewer.RdBu[9]);
    colormap = d3_scale.scaleViridis().domain([0,max_prob])
});


var tip = d3.tip().attr('class', 'd3-tip')
        .offset(function() {
            return [this.getBBox().height / 2, -this.getBBox().width/2]
        }).html(function(d) { return d.organism + ' (' + probs[d.taxid] + ')'; });

var svg = d3.select("#chart").append("svg")
    .attr("width", width)
    .attr("height", height)
  .append("g")
    .attr("transform", "translate(" + width / 2 + "," + height * .52 + ")")
    .call(tip);

var partition = d3.layout.partition()
    //.sort(null)
    .size([2 * Math.PI, radius * radius])
    .value(function(d) { return probs[d.taxid]; });
    //.value(function(d) { return counts[d.taxid] ? counts[d.taxid] : 1; });

var arc = d3.svg.arc()
    .startAngle(function(d) { return d.x; })
    .endAngle(function(d) { return d.x + d.dx; })
    .innerRadius(function(d) { return Math.sqrt(d.y); })
    .outerRadius(function(d) { return Math.sqrt(d.y + d.dy); });

d3.json("{{ url_for('static', filename='odb8_tree.json') }}", function(error, root) {
  if (error) throw error;

  var path = svg.datum(root).selectAll("path")
      .data(partition.nodes)
    .enter().append("path")
      .attr("display", function(d) { return d.depth ? null : "none"; }) // hide inner ring
      .attr("d", arc)
      .style("stroke", "#fff")
      .style("fill", function(d) { return colormap(probs[d.taxid]); })
      .style("fill-rule", "evenodd")
      .on('mouseover', tip.show)
      .on('mouseout', tip.hide);
});

// Interpolate the arcs in data space.
function arcTween(a) {
  var i = d3.interpolate({x: a.x0, dx: a.dx0}, a);
  return function(t) {
    var b = i(t);
    a.x0 = b.x;
    a.dx0 = b.dx;
    return arc(b);
  };
}

//d3.select(self.frameElement).style("height", height + "px");
