import * as d3 from "d3";
import { alloColors } from "../aesthetics.js";

export default function myLegend(max_count_log, {
  tickSize = 0,
  width = 300,
  height = 44 + tickSize,
  marginTop = 13,
  marginBottom = 16 + tickSize,
  marginLeft = 0,
  N_CATEGO = 20,
  passed_svg,
  } = {}) {

    const ramp = d3.range(N_CATEGO).map(i =>
          d3.rgb(d3.interpolateInferno(i / (N_CATEGO - 1))).hex()
    );
    const color = d3.scaleOrdinal(d3.range(N_CATEGO), ramp);


    if (passed_svg === undefined) passed_svg = d3.create("svg")

    const g = passed_svg
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .style("overflow", "visible")
        .style("display", "block");

    // let x;
    let x = d3.scaleBand()
       .domain(color.domain())
       .rangeRound([marginLeft, width - 100]);

    g.append("g")
     .selectAll("rect")
     .data(color.domain())
     .join("rect")
       .attr("x", (d) => (x(d)))
       .attr("y", marginTop)
       .attr("width", Math.max(0, x.bandwidth()))
       .attr("height", x.bandwidth())
       .attr("fill", color)
       .attr("transform", "rotate(-90) translate(-70,0)")
       .attr("stroke", "black")
       .attr("stroke-width", 0.65)
       .attr("shape-rendering", "crispEdges");  // prevents anti-alias blur in some browsers

    // let x2;
    let x2 = d3.scaleBand()
       .domain(d3.range(max_count_log).map(i => 10**i).sort(d3.descending))
       .rangeRound([marginLeft-40, width-90]);


    g.append("g")
        .call(d3.axisBottom(x2).tickSize(tickSize))
          .attr("text-anchor", "start")
          .call(g => g.selectAll("text")
          .style("font-size", "14px"))
          .attr("fill", alloColors.css.verydarkgrey)
        .call(g => g.select(".domain").remove())
        .call(g => g.append("text")
          .attr("x", marginLeft - 25) // magic number moving legend title left and right
          .attr("y", marginTop + marginBottom) // magic number moving legend title up and down
          .attr("fill", "currentColor")
          .attr("text-anchor", "start")
          .attr("font-size", 14)
          .attr("class", "title")
          .text("Counts per cell"))
          .style("font-family", `"EB Garamond", "Garamond", "Century Schoolbook L", "URW Bookman L", "Bookman Old Style", "Times", serif`)
          .attr("fill", alloColors.css.verydarkgrey)
        .attr("transform", "rotate(-90) translate(-60,5)") // magic number moving ticks and title up and down and left and right
          .selectAll('text')
          .attr("dx", 30) // magic number moving ticks left and right
          .attr("dy", -5) // magic number
          .attr('transform', 'rotate(90)') // rotating ticks and title

    return g.node();
  }