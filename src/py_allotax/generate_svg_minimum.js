import fs from 'fs';
import { JSDOM } from 'jsdom';
import createAllotaxChart from './AllotaxChart.js';

(async () => {
  // Dynamically import d3
  const d3 = await import('d3');

  // Create a new JSDOM instance (this is the headless window, no browser UI)
  const dom = new JSDOM();
  // Load your HTML file
  //index and index2 are the same, index2 is just cleaner.
  const htmlContent = fs.readFileSync(process.argv[3], 'utf8');
  dom.window.document.body.innerHTML = htmlContent;
  const { document } = dom.window;
  global.document = document;  // Make document globally available

  // Accept the path to the temporary file from the command line arguments
  const tempFilePath = process.argv[2];
  // Use require to load the JavaScript module
  const tempData = await import(tempFilePath);
  const { data1, data2, alpha, title1, title2 } = tempData;

  // Create a D3.js SVG visualization for each plot
  const diamond_svg = d3.select("#diamondplot svg");
  const legend_svg = d3.select("#legend svg");
  const balance_svg = d3.select("#balance svg");
  const wordshift_svg = d3.select("#wordshift svg");

  // System titles are positioned in the index.html
  d3.select("#title1").text(title1);
  d3.select("#title2").text(title2);

  // Create the allotaxChart instance with the provided data and arguments
  await createAllotaxChart(data1, data2, alpha, title1, title2, { diamond_svg, wordshift_svg, legend_svg, balance_svg });

  // Serialize the SVG to a string (other methods don't provide full HTML)
  const svgString = dom.serialize();
  // save the HTML as a svg after converting it to a canvas (html2canvas)


  // Print the SVG string to the console
  console.log(svgString);
  dom.window.close(); // Close the JSDOM window
})();