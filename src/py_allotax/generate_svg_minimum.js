import fs from 'fs';
import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import * as d3 from 'd3';
import { combElems, rank_turbulence_divergence, diamond_count, wordShift_dat, balanceDat } from 'allotaxonometer-ui';
import { Dashboard } from 'allotaxonometer-ui/ssr';
import { render } from 'svelte/server';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function renderDashboard(props) {
  const result = render(Dashboard, { props });
  
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Allotaxonometer Dashboard</title>
  <style>
    body {
      margin: 0;
      padding: 20px;
      font-family: system-ui, sans-serif;
    }
  </style>
</head>
<body>
  ${result.body}
</body>
</html>`;
}

(async () => {
  try {
    // Parse command line arguments
    const tempFilePath = process.argv[2];
    const outputPath = process.argv[3];
    const desiredFormat = process.argv[4] || 'pdf'; // pdf or html
    
    if (!tempFilePath || !outputPath) {
      console.error('Usage: node generate_svg_minimum.js <temp_file> <output_file> [format]');
      process.exit(1);
    }
    
    // Load data from temp file
    const fullTempPath = resolve(__dirname, tempFilePath);
    
    if (!fs.existsSync(fullTempPath)) {
      console.error(`File not found: ${fullTempPath}`);
      process.exit(1);
    }
    
    const tempData = await import(`file://${fullTempPath}`);
    const { data1, data2, alpha, title1, title2 } = tempData;
    
    console.log('Processing data...');
    
    // Process data with new API
    const me = combElems(data1, data2);
    const rtd = rank_turbulence_divergence(me, alpha);
    const dat = diamond_count(me, rtd);

    // Extract processed data
    const diamond_dat = dat.counts;
    
    // Calculate derived values
    const maxlog10 = Math.ceil(Math.max(
      Math.log10(Math.max(...me[0].ranks)),
      Math.log10(Math.max(...me[1].ranks))
    ));
    
    const max_count_log = Math.ceil(Math.log10(d3.max(diamond_dat, d => d.value))) + 1;

    // Generate chart data
    const barData = wordShift_dat(me, dat).slice(0, 30);
    const max_shift = d3.max(barData, d => Math.abs(d.metric));
    const balanceData = balanceDat(data1, data2);
    
    console.log('Generating HTML...');
    
    // Generate HTML
    const html = renderDashboard({
      dat,
      alpha,
      divnorm: rtd.normalization,
      barData,
      balanceData,
      title: [title1, title2],
      maxlog10,
      max_count_log,
      height: 815,
      width: 1200,
      DiamondHeight: 600,
      DiamondWidth: 600,
      marginInner: 160,
      marginDiamond: 40,
      xDomain: [-max_shift * 1.5, max_shift * 1.5],
      showDiamond: true,
      showWordshift: true,
      showDivergingBar: true,
      showLegend: true
    });
    
    // Always save HTML file (for testing)
    const htmlPath = outputPath.replace('.pdf', '.html');
    fs.writeFileSync(htmlPath, html);
    console.log(`HTML saved to ${htmlPath}`);
    
    // Only generate PDF if format is 'pdf'
    if (desiredFormat === 'pdf') {
      console.log('Launching browser...');
      
      const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      });
      
      const page = await browser.newPage();
      
      await page.setContent(html, { 
        waitUntil: 'networkidle0',
        timeout: 30000 
      });
      
      console.log('Generating PDF...');
      
      await page.pdf({
        path: outputPath,
        format: 'A3',
        landscape: true,
        printBackground: true,
        preferCSSPageSize: false,
        margin: {
          top: '10mm',
          right: '10mm',
          bottom: '10mm',
          left: '10mm'
        },
        scale: 0.8
      });
      
      await browser.close();
      console.log(`PDF successfully generated: ${outputPath}`);
    }
    
  } catch (error) {
    console.error('Error generating files:', error.message);
    console.error('Stack:', error.stack);
    process.exit(1);
  }
})();