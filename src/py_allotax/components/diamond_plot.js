import * as d3 from "d3";

import { alpha_norm_type2, rin } from 'allotaxonometer';

import { alloColors, alloFonts } from '../aesthetics.js';


export default function DiamondChart(dat, alpha, divnorm, {
  title,
  maxlog10,
  DiamondHeight = 600,
  marginInner = 160,
  marginDiamond = 40,
  passed_svg
 } = {}) {

  const draw_polygon = (g, tri_coords, bg_color) => g
        .append("polygon")
         .attr("fill", bg_color)
         .attr("fill-opacity", 0.8)  // was 0.2, diamond background opacity
         .attr("stroke", "black")
         .attr("stroke-width", 0.5)
         .attr("points", tri_coords)


  const innerHeight = DiamondHeight - marginInner;
  const diamondHeight = innerHeight - marginDiamond;

  const ncells = d3.max(dat, d => d.x1)
  const max_rank = d3.max(dat, (d) => d.rank_L[1]);
  const rounded_max_rank = 10**Math.ceil(Math.max(Math.log10(max_rank)))
  const relevant_types = chosen_types(dat, ncells)
  const xyDomain = [1, rounded_max_rank];


  const xy         = d3.scaleBand().domain(dat.map(d=>d.y1)).range([0, diamondHeight])

  const logScale = d3.scaleLog().domain(xyDomain).range([0, innerHeight]).nice()
  const linScale = d3.scaleLinear().domain([0,ncells-1]).range([0, innerHeight])
  const color_scale = d3.scaleSequentialLog().domain([rounded_max_rank, 1]).interpolator(d3.interpolateInferno)

  // Background polygons
  const grey_triangle = [[innerHeight, innerHeight], [0, 0], [innerHeight, 0]].join(" ")
  const blue_triangle = [[innerHeight, innerHeight], [0, 0], [0, innerHeight]].join(" ")


  // SVG container and transformations
  if (passed_svg === undefined) passed_svg = d3.create("svg");

  const g = passed_svg.style("overflow", "visible")
       .attr('transform', `scale (-1,1) rotate(45) translate(${innerHeight/4},${innerHeight/4})`)
       .attr('height', DiamondHeight)
       .attr('width', DiamondHeight);

  // AXIS ----------------------------------

  const xAxis = (g, scale) => g
      .attr("transform", `translate(0, ${innerHeight})`)
      .call(d3.axisBottom(scale)
        .tickValues(scale.ticks().filter(t => Number.isInteger(Math.log10(t))))
        .tickFormat(d3.format("~g"))
        .tickSize(10))  // Longer tick lines (negative = extend up)
      .call((g) => g.select(".domain").remove())
      .call((g) => g.selectAll(".tick line").attr("stroke-width", 0.5)) // Thinner ticks
      .selectAll('text')
        .attr('transform', 'scale(-1,1) rotate(45)')
        .attr('font-size', 12)
        .style("font-family", alloFonts)
        .attr('dx', 11)
        .attr('dy', 0)
        // for posterity: after much consternation (thinking the log scaling in pixels was messing up, it turned out to be text alignment)
        .style("text-anchor", "start"); // right-align text

  const yAxis = (g, scale) => g
      .call(d3.axisLeft(scale)
        .tickValues(scale.ticks().filter(t => Number.isInteger(Math.log10(t))))
        .tickFormat(d3.format("~g"))
        .tickSize(10))  // Longer tick lines (negative = extend left)
      .call((g) => g.select(".domain").remove())
      .call((g) => g.selectAll(".tick line").attr("stroke-width", 0.5)) // Thinner ticks
      .attr("transform", `translate(${innerHeight}, 0) scale(-1, 1)`)
      .selectAll('text')
        .attr('dx', 0)
        .attr('dy', 13)
        .attr('transform', 'rotate(45)')
        .attr('font-size', 12)
        .style("font-family", alloFonts)
        .style("text-anchor", "end"); // left-align text


  const xAxisLab = (g, x, text, dy, alpha) => g
      .append("text")
        .attr("x", x)
        .attr("dy", dy)
        .attr("fill", alloColors.css.darkergrey)
        .attr("font-size", 16)
        .attr("opacity", alpha)
        .attr("text-anchor", 'middle')
        .text(text)
          .attr('transform', `scale(-1,1) translate(-${innerHeight}, 0)`);


  const yAxisLab = (g, x, text, dy, alpha) => g
      .append("text")
        .attr("x", x)
        .attr("dy", dy)
        .attr("fill", alloColors.css.darkergrey)
        .attr("font-size", 16)
        .attr("opacity", alpha)
        .attr("text-anchor", 'middle')
        .text(text)
          .attr('transform', `rotate(90)`);


  const xGrid = (g, scale, ncells) => g
      .append('g')
      //                   + => ylines to the right , lower xlines
      //                   - => ylines to the left, higher xlines
      .attr("transform", `translate(0, -10)`)
      .call(d3.axisBottom(scale).ticks(ncells/2).tickFormat("")) // rm tick values
      .call((g) => g.select(".domain").remove())
      .call((g) => g
          .selectAll(".tick line")
          .attr("stroke", alloColors.css.darkergrey)
            .style("stroke-dasharray", ("1, 3")) // 1 dash unit then 3 gap units
          .attr("y1", -innerHeight+10) // y1 == - ? longer ylines on the top : shorter ylines on the top?
      );

  const yGrid = (g, scale, ncells) => g
      .append("g")
      //                      + => xlines to the left , lower ylines
      //                      - => xlines to the right, higher ylines
      .call(d3.axisRight(scale).ticks(ncells/2).tickFormat(""))
      .call((g) => g.select(".domain").remove())
      .call((g) => g
          .selectAll(".tick line")
          .attr("stroke", alloColors.css.darkergrey)
          .style("stroke-dasharray", ("1, 3")) // 1 dash unit then 3 gap units
          .attr("x2", innerHeight) // x2 == - ?  shorter xlines on the right :  longer xlines on the right
      );

  g.append('g')
      .call(xAxis, logScale)
      .call(xAxisLab, innerHeight/2, "Rank r", 45, 0.8)
      .call(xAxisLab, innerHeight/2, "for", 63, 0.8)
      .call(xAxisLab, innerHeight/2, title[1], 80, 0.8)
      .call(xAxisLab, innerHeight-40, "more →", 60, 0.8)
      .call(xAxisLab, innerHeight-40, "frequent", 75, 0.8)
      .call(xAxisLab, 40, "← less", 60, 0.8)
      .call(xAxisLab, 40, "frequent", 75, 0.8)
      .call(xGrid, linScale, ncells)
      .style("font-family", alloFonts)
;
  g.append('g')
      .call(yAxis, logScale)
      .call(yAxisLab, innerHeight/2, "Rank r", 45, .7)
      .call(yAxisLab, innerHeight/2, "for", 63, .7)
      .call(yAxisLab, innerHeight/2, title[0], 80, .7)
      .call(yAxisLab, innerHeight-40, "less →", 60, .7)
      .call(yAxisLab, innerHeight-40, "frequent", 75, .7)
      .call(yAxisLab, 40, "← more", 60, .7)
      .call(yAxisLab, 40, "frequent", 75, .7)
      .call(yGrid, linScale, ncells)
      .style("font-family", alloFonts)
;

  // BACKGROUND POLYGONS

  draw_polygon(g, blue_triangle, alloColors.css.paleblue)
  draw_polygon(g, grey_triangle, alloColors.css.lightgrey)


  // CONTOUR LINES

  const mycontours = get_contours(alpha, maxlog10, divnorm)

  const x = d3.scaleLinear([0, maxlog10], [0, innerHeight])
  const y = d3.scaleLinear([maxlog10, 0], [innerHeight, 0])

  const pathData = d3.line()
        .x((d, i) => x(d[0]))
        .y((d, i) => y(d[1]));

   g.append("g")
        .attr("fill", "none")
        .attr("stroke", alloColors.css.verydarkgrey)
      .selectAll("path")
        .data(mycontours)
        .enter() // Enter selection to create paths
        .append("path")
        .attr("d", pathData)  // use path for more granularity
        .attr("stroke-width", 0.25)
        .attr("stroke-opacity", 0.9);

  // Heatmap ----------------------------------
    // Out of numerous options, the closest to the matlab version is drawing cell strokes/borders as a separate layer

  // BASE LAYER: Heatmap cells with fill, NO stroke
  const cells = g
    .selectAll('rect.heat')
    .data(dat)
    .enter()
    .append('rect')
    .attr('class', 'heat')
    .attr('x', d => xy(d.x1))
    .attr('y', d => xy(d.y1))
    .attr('width', xy.bandwidth())
    .attr('height', xy.bandwidth())
    .attr('fill', d => d.value === 0 ? "none" : color_scale(d.value))

  // OVERLAY LAYER: Stroke-only rects (placed on top)
  // this option looks better than default but still have some overlapping color
  const overlays = g
    .selectAll('rect.outline')
    .data(dat)
    .enter()
    .append('rect')
    .attr('class', 'outline')
    .attr('x', d => xy(d.x1))
    .attr('y', d => xy(d.y1))
    .attr('width', xy.bandwidth())
    .attr('height', xy.bandwidth())
    .attr('fill', d => d.value > 0 ? 'rgba(255,255,255,0.001)' : 'none')  // optional near-invisible fill
    .attr('stroke', d => d.value > 0 ? alloColors.css.darkergrey : 'none')
    .attr('stroke-width', d => d.value > 0 ? 1.18 : 0)
    .attr('stroke-opacity', d => d.value > 0 ? 0.4 : 0);

  // this option insets them, gets rid of border overlap color issue but creates double borders on bordering cells
  // const inset = 1; // amount to shrink on each side
  // const overlays = g
  //   .selectAll('rect.outline')
  //   .data(dat)
  //   .enter()
  //   .append('rect')
  //   .attr('class', 'outline')
  //   .attr('x', d => xy(d.x1) + inset / 2)
  //   .attr('y', d => xy(d.y1) + inset / 2)
  //   .attr('width', xy.bandwidth() - inset)
  //   .attr('height', xy.bandwidth() - inset)
  //   .attr('fill', d => d.value > 0 ? 'rgba(255,255,255,0.001)' : 'none') // optional near-transparent fill
  //   .attr('stroke', d => d.value > 0 ? alloColors.css.verydarkgrey : 'none')
  //   .attr('stroke-width', d => d.value > 0 ? 1.0 : 0) // can lower to match new inset
  //   .attr('stroke-opacity', d => d.value > 0 ? 0.4 : 0);

    g.selectAll('text')
      .data(dat)
      .enter()
      .append('text')
      .filter(d => rin(relevant_types, d.types.split(",")).some((x) => x === true))
      .text(d => d.types.split(",")[0])
        .attr("x", (d) => xy(d.x1))
        .attr("y", (d) => Number.isInteger(d.coord_on_diag) ? xy(d.y1) : xy(d.y1)-1) // avoid text occlusion
        .attr("dx", d => d.x1 - d.y1 <= 0 ? 5 : -5)
        .attr("dy", 5)
        .attr("fill", alloColors.css.darkergrey)
        .attr("font-size", 12)
        .style("font-family", alloFonts)
        .attr("transform", d => `scale(1,-1) rotate(-90) rotate(-45, ${xy(d.x1)}, ${xy(d.y1)}) translate(${d.which_sys === "right" ? xy(Math.sqrt(d.cos_dist))*1.5 : -xy(Math.sqrt(d.cos_dist))*1.5}, 0)`) // little humph
        .attr("text-anchor", d => d.x1 - d.y1 <= 0 ? "start" : "end");


    // Draw the middle line
    g.append('line')
     .style("stroke", alloColors.css.verydarkgrey)
     .style("stroke-width", 0.5)
     .attr("x1", 0)
     .attr("y1", 0)
     .attr("x2", innerHeight-7)
     .attr("y2", innerHeight-7)


  return g.node();
}


function filter_contours(tmpcontours, Ninset, maxlog10) {

  const chart2val = d3.scaleLinear()
    .domain([0, Ninset]) // unit: km
    .range([0, maxlog10]) // unit: pixels

  let out = []
  // Extract Coordinates:
  tmpcontours.forEach((contour) => {
    contour.coordinates.forEach((pair, i) => {
      const tmpr1 = pair[0].map(d => d[0]); // x-coordinates
      const tmpr2 = pair[0].map(d => d[1]); // y-coordinates

      // Array to store filtered coordinate pairs in zipped format
      const filteredPairs = [];

      // Loop through each coordinate and calculate `tmpxrot`
      for (let index = 0; index < tmpr1.length-1; index++) {
        const x1 = chart2val(tmpr1[index]);
        const x2 = chart2val(tmpr2[index]);

        // Calculate tmpxrot
        const tmpxrot = Math.abs(x2 - x1) / Math.sqrt(2);

        // If the condition is met, add the coordinate pair [x1, x2] to `filteredPairs`
        if (Math.abs(tmpxrot) >= 0.1 & x1 != maxlog10 & x2 != 0 & x1 != 0 & x2 != maxlog10) {
          filteredPairs.push([x1, x2]);
        }
      }

      // Only push to `out` if we have filtered pairs
      if (filteredPairs.length > 0) {
        out.push(filteredPairs); // Store each set of filtered pairs in `out`
      }
    })
  })
return out
}

function make_grid(Ninset, tmpr1, tmpr2, alpha, divnorm) {
  // No matrix in js :(
  // we could try to do like in the original d3.contour, where they do
  // calculation to work with a flat array.
  // Instead we flatten that List of list later.

  const deltamatrix = Array.from({ length: Ninset }, () => Array(Ninset).fill(0));

  // Populate deltamatrix with alpha_norm_type2 values and set the diagonal and adjacent values
  for (let i = 0; i < Ninset; i++) {
    for (let j = 0; j < Ninset; j++) {
        const divElem = alpha_norm_type2(1 / tmpr1[i], 1 / tmpr2[j], alpha);
        // const normalization = divnorm; // Harcoded from Boys 1968 vs 2018 with alpha=0.08
        deltamatrix[i][j] = divElem / divnorm;
    }

    //     %% prevent contours from crossing the center line
    deltamatrix[i][i] = -1;

    // Set adjacent diagonal elements to -1 if within bounds
    if (i < Ninset - 1) {
      deltamatrix[i][i + 1] = -1;
      deltamatrix[i + 1][i] = -1;
    }
  }

  return deltamatrix;
};

function get_contours(alpha, maxlog10, divnorm) {
  // only for alpha != 0 and alpha != Infinity

  const Ninset = 10 ** 3
  const tmpr1 = d3.range(0, 1000).map(d => Math.pow(10, d / 999 * 5));
  const tmpr2 = d3.range(0, 1000).map(d => Math.pow(10, d / 999 * 5));

  // Create a scale to generate `Ncontours + 2` values linearly spaced between 1 and `tmpr1Length`
  const Ncontours = 10;
  const scale = d3.scaleLinear()
    .domain([0, Ncontours + 1])
    .range([1, tmpr1.length]);


  const contour_indices = d3.range(Ncontours + 2).map(i => Math.round(scale(i)));
  const grid = make_grid(Ninset, tmpr1, tmpr2, alpha, divnorm)
  const indices = contour_indices.slice(1, -1);
  const lastRow = grid[grid.length - 1];
  const heights = indices.map(index => lastRow[index]);

  // equivalent to `contourc`
  // we first create a generator
  // then we pass to Z (flatDeltamatrix)
  const logTmpr = tmpr1.map(Math.log10)

  const contourGenerator = d3.contours()
      .size([logTmpr.length, logTmpr.length])  // Set the grid size
      .thresholds(heights); // I guess this is equivalent? These are levels.

  const flatDeltamatrix = grid.flat();
  const tmpcontours = contourGenerator(flatDeltamatrix);

  return filter_contours(tmpcontours, Ninset, maxlog10)

}

function chosen_types(dat, ncells) {
  const cumbin = d3.range(0, ncells, 1.5)
  const relevant_types = []

  for (let sys of ["right", "left"]) {
    for (let i=1; i < cumbin.length; i++) {
      const filtered_dat = dat.filter(d => d.value > 0 && d.which_sys == sys)
                              .filter(d => d.coord_on_diag >= cumbin[i-1] &&
                                           d.coord_on_diag < cumbin[i])
      if (filtered_dat.length > 0) {
        const cos_dists = filtered_dat.map(d => d.cos_dist)
        const max_dist = cos_dists.reduce((a, b) => { return Math.max(a, b) })
        const max_dist_idx = cos_dists.indexOf(max_dist)
        const name = d3.shuffle(filtered_dat[max_dist_idx]['types'].split(","))[0]
        relevant_types.push(name)
      }
  }
  }
  return relevant_types
}
