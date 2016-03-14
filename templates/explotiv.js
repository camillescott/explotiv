var width = 960,
    height = 700,
    radius = Math.min(width, height) / 2,
    colormap = d3_scale.scaleViridis().domain([0.0,1.0]);





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

    console.log(data);

    var tip = d3.tip().attr('class', 'd3-tip')
        .offset(function() {
            return [this.getBBox().height / 2, -this.getBBox().width/2]
        }).html(function(d) { return d.organism + ' (' + data[d.taxid] + ')'; });


    var svg = d3.select("#chart").append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height * .52 + ")")
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

        path = svg.datum(root).selectAll("path")
            .data(partition.nodes)
            .enter().append("path")
            .attr("display", function(d) { return d.depth ? null : "none"; }) // hide inner ring
            .attr("d", arc)
            .style("stroke", "#fff")
            .style("fill", function(d) {
                return colormap(data[d.taxid]);
            }).style("fill-rule", "evenodd")
            .on('mouseover', tip.show)
            .on('mouseout', tip.hide);
    });
}


function phyloInit() {
    d3.json("{{ url_for('phylo_pane.probability_means') }}", function(error, obj) {
        if (error) throw error;
        phyloViz(obj.data);
    });
}
