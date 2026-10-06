import fs from 'fs';
import { createRequire } from 'module';
import puppeteer from 'puppeteer';
import { Dashboard } from 'allotaxonometer-ui/ssr';
import { render } from 'svelte/server';

const require = createRequire(import.meta.url);

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
    const propsFilePath = process.argv[2];
    const outputPath = process.argv[3];
    const desiredFormat = process.argv[4] || 'pdf';

    if (!propsFilePath || !outputPath) {
      console.error('Usage: node render.js <props_json_file> <output_file> [pdf|svg|html]');
      process.exit(1);
    }

    if (!fs.existsSync(propsFilePath)) {
      console.error(`File not found: ${propsFilePath}`);
      process.exit(1);
    }

    // All computation happens in Python (allotax Rust bindings); this script
    // only renders the precomputed props to HTML/SVG/PDF.
    const props = JSON.parse(fs.readFileSync(propsFilePath, 'utf8'));

    // JSON cannot carry Infinity, so Python sends it as a string.
    if (props.alpha === 'Infinity') {
      props.alpha = Infinity;
    }

    console.log('Generating HTML...');

    const html = renderDashboard(props);

    if (desiredFormat === 'html') {
      fs.writeFileSync(outputPath, html);
      console.log(`HTML saved to ${outputPath}`);
      return;
    }

    console.log('Launching browser...');

    const browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    // Viewport must fit the dashboard so flex layout doesn't wrap.
    await page.setViewport({
      width: (props.DashboardWidth || 1200) + 200,
      height: (props.DashboardHeight || 815) + 200
    });

    await page.setContent(html, {
      waitUntil: 'networkidle0',
      timeout: 30000
    });

    if (desiredFormat === 'svg') {
      // Same approach as the allotaxonometer web app's "Download SVG":
      // dom-to-image serializes the laid-out dashboard into a standalone SVG.
      console.log('Generating SVG...');

      await page.addScriptTag({ path: require.resolve('dom-to-image-more') });
      const dataUrl = await page.evaluate(() => {
        const node = document.querySelector('#allotaxonometer-dashboard') || document.body;
        return window.domtoimage.toSvg(node);
      });

      const svg = decodeURIComponent(
        dataUrl.replace(/^data:image\/svg\+xml;charset=utf-8,/, '')
      );
      fs.writeFileSync(outputPath, svg);
      console.log(`SVG saved to ${outputPath}`);
    } else {
      // PDF (default); also writes the intermediate HTML alongside.
      const htmlPath = outputPath.replace('.pdf', '.html');
      fs.writeFileSync(htmlPath, html);
      console.log(`HTML saved to ${htmlPath}`);

      console.log('Generating PDF...');

      await page.pdf({
        path: outputPath,
        format: 'A3',
        landscape: true,
        printBackground: true,
        preferCSSPageSize: false,
        margin: {
          top: '40mm',
          left: '40mm'
        },
        scale: 1.0
      });

      console.log(`PDF successfully generated: ${outputPath}`);
    }

    await browser.close();

  } catch (error) {
    console.error('Error generating files:', error.message);
    console.error('Stack:', error.stack);
    process.exit(1);
  }
})();
