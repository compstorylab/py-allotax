# Package decisions

## Decision (July 2026): computation extracted to the Rust core

Computation moved from the JS `allotaxonometer-ui` functions to the
[allotax](https://pypi.org/project/allotax/) PyO3 bindings over
[allotax-core](https://github.com/Vermont-Complex-Systems/allotaxonometer-core), the same Rust core the web app uses via WASM. The workflow is now:

1. Python computes RTD, diamond counts, wordshift, and balance in-process via `allotax`.
2. For `pdf`/`html`, Python passes the precomputed props to a render-only node script (`render.js`: Svelte SSR of the `Dashboard` + Puppeteer).
3. For RTD-only usage, `allotax.rank_turbulence_divergence` is called directly — no JS runs at all (roughly 30x faster than the former subprocess round-trip, and usable in HPC/conda environments where chromium discovery fails).

One source of truth for the math across web (WASM), Python, and any future
bindings. The original mixed-approach decision below is kept for history.

In 2.0 the API was renamed to domain terms and kept minimal: `allotaxonograph`
(one call, data to figure; `pdf`/`svg`/`html`; without `output_file` it
returns a figure that displays inline, with `.save()`, `.interactive()`, and
`.plot_data` for reuse); RTD-only users call `allotax.rank_turbulence_divergence`
directly with `as_system`. Compute and render remain separate
steps internally, but are not public API. `generate_svg` remains as a
deprecated alias.

## Decision (original)
Regarding the ideation below, we ended up going with the following workflow using a mixed Python and JavaScript approach:
1. User provides 2 datasets and alpha.
1. In JS, create a DOM.
1. Load the allotaxonometer html plot template into the DOM.
1. Calculate data for the plot and add that data to each plot's svg.
1. Serialize results to a HTML.
1. Intercept this result in Python with `subprocess`.
1. Library saves the HTML to a file (user input can opt to end processing here).
1. Library generates a static image file from the HTML.


## Design

### Goals
1. Main goal: User accessibility for the use case of integrating the graphing method in computational research.
    - This goal means ease of ease of use and ease of installation into their environment.
1. Maintainability
    - It is easy to make updates to the code, hopefully from its main `npm` package.
    - One realism we're already dealing with is a custom branch of the main `allotaxonometer` library that enables minor customization to facilitate the Python integration.
1. Performance
    - The rendering and format conversion method runs headlessly; it should be able to handle large data sets and be integrated into larger analyses or many runs, pipelines, parallel processing, etc.

### Design thoughts considered
1. Write the package only in JavaScript.
    - Pro: we wouldn't need to manage disparate ecosystems (Python and JavaScript).
    - Con: this route doesn't as readily acheve goal 1, as we presume scientific users would need to install an unfamiliar ecosystem.
1. Write the package in Python (while utilizing the `npm` library).
    - Pro: achieves goal 1 of ease of use
    - Con: may make goal 1 of ease of installation still difficult. We will perform early user testing to see how much of a barrier this is--noting this is an early version of the tool.
    - Add-on options to consider:
        1. Include any node.js library binaries in the Python library to negate a `npm` and `node.js` environment for users (assumption: ease of installation comes from Python installation being the only dependency). The difficulty with this route is that binaries for multiple OSs should be included.
            - **We want to attempt this route first to abstract away JS ecosystem.**
        1. Make a set-up/install script so the user does not need to worry about the installation of `node`, `npm`, and packages.
1. Containerize `py-allotax` to manage the environment.
    - Pro: this would make the environment easy and consistent across all users. Users would only need to worry about a Docker installation.
    - Con: user testing needed for accessibility goal; also unclear how much maintainability would be affected while the py-allotax's `allotaxonometer` library remains a branch of the main library.

 ### HTML to image options

 See [this issue](https://github.com/carterwward/py-allotax/issues/3) for details on options explored so far.

## Future improvements (TODOs):
1. Continue improving the ecosystem dependencies (or automation of set-up) to streamline ease of installation.
1. Extend methods:
    - ability to get computed ranks and other variables of interest (data that is generated for the creation of the graph but not returned anywhere).
    - ability to retrieve intermediate desired results to analyze or visualize in other tools.
1. Write up some examples, including a use case for big data using multiprocessing locally.
1. Improve or add more HTML to image conversion method(s).