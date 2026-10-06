"""Generate allotaxonographs through Python.

Computation (RTD, diamond counts, wordshift, balance) runs in-process via the
`allotax` Rust bindings; node/JS is only used to render the plot (Svelte SSR
+ Puppeteer). For RTD data without a plot, call the bindings directly —
`allotax.rank_turbulence_divergence(df1, df2, alpha)` (DataFrames work as-is;
wrap file paths or record lists with `as_system`) — no JS needed at all.

As a test, run in terminal:
py-allotax example_data/boys_2022.json example_data/boys_2023.json test.pdf "0.17" "Boys 2022" "Boys 2023"

(or: python -m py_allotax ...)

Other formats: --desired_format svg | html
"""

import argparse
import html
import json
import math
import os
import re
import subprocess
import tempfile
import warnings
from importlib import resources

import allotax

from py_allotax.utils import as_system, parse_alpha

# Number of wordshift entries shown on the plot.
WORDSHIFT_TOP_N = 30

FORMATS = ("pdf", "svg", "html")


def _compute_plot_data(data1, data2, alpha, title1: str = "", title2: str = "") -> dict:
    """Compute all data the plot needs, in-process (no node/JS).

    Returns the Dashboard props dict (diamond_counts, ncells, wordshift,
    balance, normalization, alpha, maxlog10, max_count_log, title) — exposed
    to users as `AllotaxFigure.plot_data`.
    """
    system1 = as_system(data1)
    system2 = as_system(data2)
    alpha_value = parse_alpha(alpha)

    result = allotax.compute_allotax(
        system1, system2, alpha_value, wordshift_limit=WORDSHIFT_TOP_N
    )

    max_cell_value = max((cell["value"] for cell in result["diamond_counts"]), default=1)
    max_count_log = math.ceil(math.log10(max_cell_value)) + 1 if max_cell_value > 0 else 1

    return {
        "diamond_counts": result["diamond_counts"],
        "ncells": result["ncells"],
        "wordshift": result["wordshift"],
        "balance": result["balance"],
        "normalization": result["normalization"],
        # JSON cannot carry Infinity; the JS side converts the string back.
        "alpha": "Infinity" if math.isinf(alpha_value) else alpha_value,
        "maxlog10": result["maxlog10"],
        "max_count_log": max_count_log,
        "title": [title1, title2],
    }


def _ensure_node_modules(js_dir: str) -> None:
    """Install the JS render dependencies on first use.

    The wheel ships only package.json + render.js; `npm install` runs once
    here (which also lets puppeteer download its Chrome properly).
    """
    if os.path.isdir(os.path.join(js_dir, "node_modules")):
        return
    print(
        "First render: installing JS dependencies with npm "
        "(downloads Chrome for puppeteer; this can take a few minutes)..."
    )
    result = subprocess.run(
        ["npm", "install"], cwd=js_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"npm install failed in {js_dir}.\n{result.stderr}\n"
            "Ensure node/npm are installed (see README), or run "
            f"`npm install` manually in {js_dir}."
        )


def _render(
    plot_data: dict, output_file: str, desired_format: str = "pdf", quiet: bool = False
) -> None:
    """Render precomputed plot data to a file via node (Svelte SSR + Puppeteer).

    Layout is format-specific and applied here: pdf prints on an oversized
    A3 canvas; svg/html use the Dashboard's natural layout (same as the
    web app).
    """
    if desired_format not in FORMATS:
        raise ValueError(
            f"desired_format must be one of {FORMATS}; got {desired_format!r}"
        )

    props = dict(plot_data, marginInner=160, marginDiamond=40)
    if desired_format == "pdf":
        pdf_width = 4200
        pdf_height = 2970
        props.update(
            width=pdf_width,
            height=pdf_height,
            DashboardWidth=pdf_width,
            DashboardHeight=pdf_height,
        )

    # Write the precomputed props to a temporary file for the render script
    temp_file_path = tempfile.mktemp(suffix=".json")
    with open(temp_file_path, "w") as file:
        json.dump(props, file, allow_nan=False)

    js_file_path = resources.files('py_allotax').joinpath('render.js')
    _ensure_node_modules(os.path.dirname(str(js_file_path)))

    command = [
        "node",
        str(js_file_path),
        os.path.abspath(temp_file_path),
        os.path.abspath(output_file),
        desired_format,
    ]

    # Run the JS file and capture the output
    result = subprocess.run(command, capture_output=True, text=True, cwd=os.path.dirname(js_file_path))

    # Clean up temp file
    try:
        os.unlink(temp_file_path)
    except OSError:
        pass

    if result.returncode == 0:
        if not quiet:
            print(f"{desired_format.upper()} saved to {output_file}")
    else:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise Exception(f"Error in Graph Generation: {result.stderr}")


def _js_versions() -> tuple:
    """Versions of allotaxonometer-ui and svelte from the shipped package.json,
    so the CDN-mounted interactive figure matches the SSR render exactly."""
    pkg = json.loads(
        resources.files('py_allotax').joinpath('package.json').read_text()
    )
    deps = pkg["dependencies"]
    return deps["allotaxonometer-ui"].lstrip("^~"), deps["svelte"].lstrip("^~")


class _InteractiveView:
    """Interactive view of a figure: an iframe mounting the client-side
    Dashboard (hover tooltips, same component as the web app) from esm.sh.

    Needs internet at viewing time, and a frontend that runs scripts in
    outputs (JupyterLab, classic notebook, standalone browser). Sandboxed
    renderers such as VS Code's may block the CDN script — use the default
    static view there, or `.save_html(path)` and open it in a browser.
    """

    def __init__(self, plot_data: dict):
        self.plot_data = plot_data

    def _page(self) -> str:
        ui_version, svelte_version = _js_versions()
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://esm.sh/allotaxonometer-ui@{ui_version}/dist/style.css">
</head><body style="margin:0;font-family:system-ui">
<div id="app"></div>
<script type="module">
  import {{ Dashboard }} from 'https://esm.sh/allotaxonometer-ui@{ui_version}?deps=svelte@{svelte_version}';
  import {{ mount }} from 'https://esm.sh/svelte@{svelte_version}';
  const props = {json.dumps(self.plot_data)};
  if (props.alpha === 'Infinity') props.alpha = Infinity;
  mount(Dashboard, {{ target: document.getElementById('app'), props }});
</script>
</body></html>"""

    def _repr_html_(self) -> str:
        srcdoc = html.escape(self._page(), quote=True)
        return (
            f'<iframe srcdoc="{srcdoc}" width="100%" height="760" '
            'style="border:none; min-width:700px;"></iframe>'
        )

    def save_html(self, path: str) -> None:
        """Write the interactive page to a standalone HTML file."""
        with open(path, "w") as f:
            f.write(self._page())
        print(f"Interactive HTML saved to {path}")


class AllotaxFigure:
    """Figure returned by `allotaxonograph` when no output_file is given.

    Displays inline in a notebook as a static SVG (works in every frontend).
    `.interactive()` returns the interactive Dashboard view; `.save(path)`
    writes a pdf/svg/html file.
    """

    def __init__(self, plot_data: dict):
        self.plot_data = plot_data
        self._svg = None

    def __repr__(self) -> str:
        return (
            "AllotaxFigure — displays inline in a notebook; "
            ".interactive() for the interactive view, .save(path) to write a file"
        )

    def _repr_svg_(self):
        """Static inline display, rendered lazily via node and cached.

        The root svg gets a viewBox and width=100% so it scales to the
        notebook output pane instead of overflowing at its fixed pixel size.
        """
        if self._svg is None:
            temp_svg = tempfile.mktemp(suffix=".svg")
            try:
                _render(self.plot_data, temp_svg, "svg", quiet=True)
                with open(temp_svg, "r") as f:
                    self._svg = f.read()
            finally:
                try:
                    os.unlink(temp_svg)
                except OSError:
                    pass
        match = re.match(r'(<svg[^>]*?) width="([\d.]+)" height="([\d.]+)"', self._svg)
        if match and "viewBox" not in match.group(1):
            head = f'{match.group(1)} viewBox="0 0 {match.group(2)} {match.group(3)}" width="100%"'
            return head + self._svg[match.end():]
        return self._svg

    def interactive(self) -> _InteractiveView:
        """Interactive Dashboard view (hover tooltips), loaded from esm.sh.

        Works in frontends that run scripts in outputs (JupyterLab, classic
        notebook); sandboxed renderers such as VS Code's may block it — use
        `.interactive().save_html(path)` and open in a browser instead.
        """
        return _InteractiveView(self.plot_data)

    def save(self, path: str, desired_format: str = None) -> None:
        """Write the figure to a file; format inferred from the extension."""
        if desired_format is None:
            extension = os.path.splitext(path)[1].lstrip(".").lower()
            desired_format = extension if extension in FORMATS else "pdf"
        _render(self.plot_data, path, desired_format)


def allotaxonograph(
    data1,
    data2,
    alpha,
    title1: str = "",
    title2: str = "",
    output_file: str = None,
    desired_format: str = None,
):
    """Generate an allotaxonograph comparing two systems.

    Without `output_file`, returns the chart as an object a Jupyter notebook
    displays inline (use `.save(path)` to also write it). With `output_file`,
    writes the file — format inferred from the extension (pdf/svg/html)
    unless `desired_format` says otherwise.

    To render the same comparison to several formats, keep the figure and
    call `.save()` repeatedly — computation happens only once.

    Args:
        data1: First system — path to a JSON data file, a pandas DataFrame
            with 'types' and 'counts' columns, a list of records, or a
            columnar dict (see `utils.as_system`)
        data2: Second system, same accepted forms
        alpha: Alpha value for RTD calculation ("0.17", "Infinity", or a float)
        title1: Title for system 1
        title2: Title for system 2
        output_file: Path to save the plot; omit to get the inline figure
        desired_format: "pdf", "svg", or "html"; default inferred from
            output_file extension (falling back to "pdf")
    """
    plot_data = _compute_plot_data(data1, data2, alpha, title1, title2)

    if output_file is None:
        return AllotaxFigure(plot_data)

    if desired_format is None:
        extension = os.path.splitext(output_file)[1].lstrip(".").lower()
        desired_format = extension if extension in FORMATS else "pdf"
    _render(plot_data, output_file, desired_format)


def generate_svg(
    data1,
    data2,
    output_file: str,
    alpha,
    title1: str,
    title2: str,
    desired_format: str = "pdf",
) -> None:
    """Deprecated alias for `allotaxonograph` (kept for pre-2.0 callers)."""
    warnings.warn(
        "generate_svg is deprecated; use allotaxonograph instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    allotaxonograph(
        data1, data2, alpha, title1, title2,
        output_file=output_file, desired_format=desired_format,
    )


def main() -> None:
    """CLI entry point (`py-allotax` or `python -m py_allotax`)."""
    parser = argparse.ArgumentParser(
        prog="py-allotax",
        description="Generate an allotaxonograph.",
    )
    parser.add_argument(
        "data_file_1", type=str, help="Path to the first json data file."
    )
    parser.add_argument(
        "data_file_2", type=str, help="Path to the second json data file."
    )
    parser.add_argument(
        "output_file", type=str, help="Path to save the output file."
    )
    parser.add_argument("alpha", type=str, help="Alpha value.")
    parser.add_argument("title1", type=str, help="Title for system 1")
    parser.add_argument("title2", type=str, help="Title for system 2.")
    parser.add_argument(
        "--desired_format",
        type=str,
        default="pdf",
        choices=list(FORMATS),
        help="Desired output format (default: pdf).",
    )

    args = parser.parse_args()

    allotaxonograph(
        args.data_file_1,
        args.data_file_2,
        args.alpha,
        args.title1,
        args.title2,
        output_file=args.output_file,
        desired_format=args.desired_format,
    )


if __name__ == "__main__":
    main()
