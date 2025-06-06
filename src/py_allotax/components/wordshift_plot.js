import * as d3 from "d3";
import { alloColors } from "../aesthetics.js";

export default function WordShiftChart(data, {
  x = d => d,
  y = (d, i) => i,
  title,
  marginTop = 50,
  marginRight = 60,
  marginBottom = 40,
  marginLeft = 70,
  width = 360,
  height,
  xType = d3.scaleLinear,
  xDomain,
  xFormat = '%',
  xLabel = '← System 1 · Divergence contribution · System 2 →',
  yPadding = 0,
  yDomain,
  colors = [alloColors.css.lightgrey, alloColors.css.paleblue],
  passed_svg,
} = {}) {
  const xAxisYOffset = 10; // Space below x-axis

  // Compute values
  const X = d3.map(data, x);
  const Y = d3.map(data, y);

  if (xDomain === undefined) xDomain = d3.extent(X);
  if (yDomain === undefined) yDomain = Y;
  yDomain = new d3.InternSet(yDomain);

  const I = d3.range(X.length).filter(i => yDomain.has(Y[i]));
  const YX = d3.rollup(I, ([i]) => X[i], i => Y[i]);

  const bandHeight = 18;
  const compactHeight = yDomain.size * bandHeight;
  const innerWidth = width - marginLeft - marginRight;
  const innerHeight = compactHeight + xAxisYOffset;

  if (height === undefined) height = innerHeight + marginTop + marginBottom;

  const xRange = [0, innerWidth];
  const yRange = [xAxisYOffset, xAxisYOffset + compactHeight];

  const xScale = xType(xDomain, xRange);
  const yScale = d3.scaleBand(yDomain, yRange).padding(yPadding);
  const xAxis = d3.axisTop(xScale).ticks(width / 80, xFormat);
  const yAxis = d3.axisLeft(yScale).tickSize(0).tickPadding(3);
  const format = xScale.tickFormat(100, xFormat);

  if (title === undefined) {
    title = i => `${Y[i]}\n${format(X[i])}`;
  } else if (title !== null) {
    const O = d3.map(data, d => d);
    const T = title;
    title = i => T(O[i], i, data);
  }

  if (passed_svg === undefined) passed_svg = d3.create("svg");

  passed_svg
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", `0 0 ${width} ${height}`); // allow full visible space

  const shiftSvgBy = 12; // shift svg up to align with system titles
  const g = passed_svg.append("g")
    .attr("transform", `translate(${marginLeft}, ${marginTop - shiftSvgBy})`);

  // X-axis group
  g.append("g")
    .attr("transform", `translate(0,${xAxisYOffset})`)
    .call(xAxis)
    .call(g => g.select(".domain").remove())
    .call(g => g.selectAll(".tick line").clone()
      .attr("y2", innerHeight - xAxisYOffset)
      .attr("stroke-opacity", 0.1))
    .call(g => g.append("text")
      .attr("x", xScale(0))
      .attr("y", -35)
      .attr("fill", "currentColor")
      .attr("text-anchor", "middle")
      .text(xLabel))
    .attr("font-family", "Times, serif")
    .attr("font-size", 16)
    .attr("fill", alloColors.css.verydarkgrey);

  // Bars
  const barHeightFactor = 0.7;
  const bar = g.append("g")
    .selectAll("rect")
    .data(I)
    .join("rect")
    .attr("fill", i => colors[X[i] > 0 ? colors.length - 1 : 0])
    .attr("x", i => Math.min(xScale(0), xScale(X[i])))
    .attr("width", i => Math.abs(xScale(X[i]) - xScale(0)))
    .attr("height", yScale.bandwidth() * barHeightFactor)
    .attr("y", i => yScale(Y[i]) + (yScale.bandwidth() - yScale.bandwidth() * barHeightFactor) / 2)
    .attr("font-family", "Times, serif")
    .attr("font-size", 14);

  if (title) bar.append("title").text(title);

  // Y-axis
// Y-axis with split tick labels (name and numbers)
  g.append("g")
    .attr("transform", `translate(${xScale(0)},0)`)
    .call(yAxis)
    .call(g => g.selectAll(".tick text")
      .each(function(y) {
        const fullText = y;  // The tick label text, e.g. "Grover (413.5 ⇋ 20)"

        // Parse into name and numbers
        const splitIndex = fullText.indexOf(' ');
        let name_y, numbers_y;
        if (splitIndex === -1) {
          name_y = fullText;
          numbers_y = "";
        } else {
          name_y = fullText.slice(0, splitIndex);
          numbers_y = fullText.slice(splitIndex + 1).trim();
          // Strip first and last characters from numbers_y if possible
          if (numbers_y.length > 2) {
            numbers_y = numbers_y.slice(1, numbers_y.length - 1);
          }
        }

        const xValue = YX.get(y); // value associated with this label
        const tickGroup = d3.select(this.parentNode);

        // Remove the original text element since we will create two separate texts
        d3.select(this).remove();

        // Name text on the normal side
        tickGroup.append("text")
          .text(name_y)
          .attr("font-family", "Times, serif")
          .attr("font-size", 14)
          .attr("fill", alloColors.css.verydarkgrey)
          .attr("dy", "0.32em")
          .attr("x", xValue > 0 ? 6 : -6)
          .attr("text-anchor", xValue > 0 ? "start" : "end");

        if (numbers_y) {
          // Numbers text on the opposite side
          tickGroup.append("text")
            .text(numbers_y)
            .attr("font-family", "Times, serif")
            .attr("font-size", 14)
            .attr("opacity", 0.5)
            .attr("fill", alloColors.css.darkergrey)
            .attr("dy", "0.32em")
            .attr("x", xValue > 0 ? -6 : 6)
            .attr("text-anchor", xValue > 0 ? "end" : "start");
        }
      }))
    .attr("font-family", "Times, serif")
    .attr("font-size", 14);


  return passed_svg.node();
}
