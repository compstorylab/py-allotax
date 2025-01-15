# Allotaxonometer through Python

The `py-allotax` implements a python interface to the `allotaxonometer` library. The tool here provides a way for users to input data and arguments and receive back a saved plot! The tool is designed to be used in a command line or in a python notebook in a few lines of code (see usage instructions at the bottom).

Table of contents:
- [Installation](#installation)
- [Usage instructions](#usage-instructions)
- [Developer Notes](#developer-notes)
- [Frequent questions or issues](#frequent-questions-or-issues)
- [Repo structure notes](#repo-structure-notes)
- [Resources](#resources)



## Installation

1. Requires `python3.11` or greater.

1. If JavaScript tool installs are needed (never used or installed `npm`, `nvm`, `node`):
    1. Here are the recommended [steps to install `nvm`](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating). `nvm` is a node version manager that streamlines installing the other 2.
    - Otherwise (not recommended): [steps to individually install `node` and `npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
1. Once you have `nvm`, install the latest of both `node` and `npm` with:
    ```bash
    nvm install --lts
    ```
1. One package depends on having Chrome (brower) or Chromium (browser driver) installed. **If you have Chrome installed, you can skip this step**. Otherwise, install Chrome or Chromium.

1. Activate your desired python environment then
    ```bash
    pip3 install py-allotax
    ```

## Usage instructions

### Package
If working in a python notebook or script, you can install the package and use the function directly. Example data can be downloaded from the `example_data` directory to run the example below and those found in the `examples.ipynb`. [boys 2022](example_data/boys_2022.csv) and [boys 2023](example_data/boys_2023.json) are the examples used below.

```python
import os
from py_allotax.generate_svg import generate_svg
data_path1 = os.path.join("example_data", "boys_2022.json")
data_path2 = os.path.join("example_data", "boys_2023.json")
generate_svg(data_path1, data_path2, "test.pdf", "0.17", "Boys 2022", "Boys 2023")
```

If running the example, you can check your result against the [example output](example_charts).


### CLI

1. Clone the GitHub repository.
1. Verify your data is in the required format (`.json`) by seeing json examples in `example_data/`.
    - See helper functions in `utils` to convert among `csv`, `json`, and `js` formats.
    - The method `utils.convert_csv_data` exists to convert your data from `.csv` to `.json` if needed--see `examples.ipynb`.
1. Add your 2 system's files. You need 2 `data.json` files, one for each system.

Verify this test against `example_charts/test.pdf`.


To get help, you can run the following `python src/py_allotax/generate_svg.py --help`. It will show the following:
```
usage: generate_svg.py [-h] [--desired_format {pdf,html}] json_file_1 json_file_2 output_file alpha title1 title2

Generate allotaxonometer plot.

positional arguments:
  json_file_1           Path to the first json data file.
  json_file_2           Path to the second json data file.
  output_file           Path to save the output pdf file.
  alpha                 Alpha value.
  title1                Title of system 1
  title2                Title of system 2.

options:
  -h, --help            show this help message and exit
  --desired_format {pdf,html}
                        Desired output format (default: pdf).
```

## Developer Notes
### Dependency Manager
[pdm](https://pdm-project.org/latest/#installation) is required for the build and testing.

### Setup
Once `pdm` is installed, run:
```
pdm sync
```
to install all python dependencies.

### Testing

To test the package without building and installing, simply run:
```
pdm run pytest
```
This will execute the tests written in the `tests` dir.

### Package Build
Clone this repo and install the requirements:

```bash
git clone https://github.com/compstorylab/py-allotax.git &&
cd py-allotax &&
./scripts/build.sh
```

You should see a `.whl` file in the newly created `dist` directory.

## Frequent questions or issues

Will any data format work?
- There are specific column/variable names, and the data must be in `.json` format. The column names and formats vary across a few of the allotaxonometer tools, so there is a data format conversion function in `utils.py` to go from `.csv` to `.json`. See `examples.ipynb` for how to convert your data from `.csv` to `.json`.

I use Google colab or online-based coding environments only.
- Currently, this tool is a repo (not yet a package) and its dependencies may be difficult to install in an online environment. We recommend using Python virtual environments or Anaconda to create and manage Python environments locally. See below some shell instructions to get started with a Python virtual environment.

    <details>
    <summary>Click for Python virtual environment instructions</summary>

    - Navigate to ('change directory' with `cd`) the folder where your coding or related work lives. These instructions will create a folder here containing your environment, `env`. Inside the folder, python’s virtual environment library, `venv`, will create files and download libraries. Each time you activate this environment, you have access to its libraries and can manage them.
        ```
        cd path-to-create-env
        ```
    - Generate an `env` with a name such as `allotax_env`:
        ```
        python3 -m venv <name_of_env>
        ```
    - Activate (source) the `env`; unless you automate this step, you will need to do this each time you restart your shell or change `env`.
        - In the directory where your `env` is, enter `pwd` (print working directory) to get its full path. Copy that path and fill in below, leaving the `bin/activate` at the end:
            ```
            source /replace-wth-path-to/name_of_env/bin/activate
            ```
        - Now you can install the python packages needed or do other library management (type `pip help` for more commands):
            ```
            pip3 install pandas pyhtml2pdf selenium==4.25.0
            ```
    - You are set up to use a coding application (IDE) or command line to run this tool. If you do not have Anaconda, we recommend VS Code (where you can work with `.ipynb` files as you might in Jupyter or Colab).
    </details>


Where do I find the output?
- It is at the path you specified (argument provided) when you ran the `generate_svg`.

Terminal says there is no `nvm` after installing it.
- Restart your terminal to activate it.

Terminal says there is no `node` even after I have already run `py-allotax` methods.
- This seems to happen when switching environments or changing branches. You can simply re-run the installs. You should already have `nvm` and be able to start from there.

I am receiving this error: `AttributeError: 'ChromiumRemoteConnection' object has no attribute '_url’`.
- One of secondary dependencies is `selenium`, and it seems to break if the version is higher than 4.25.0. Run `pip3 install selenium==4.25.0`.

I am receiving an `npm` error regarding `canvas`, `pixman`, or other packages I do not recognize.
- You may need `canvas` and its dependencies. Please follow [this guide](https://www.npmjs.com/package/canvas#compiling) to installing it based on your OS.

Other packages are erring out or not installing.
- We will eventually package this repo and streamline installation.


<br>
<br>

Users accessing these tools is our primary goal, so feel free to contact us by submitting an issue in the repo, emailing, or reaching out in one of our Slack spaces. Include these notes on your issue:
1. What exactly you did and steps leading up to it, and
2. Things you may have tried, and
3. The exact error message(s).


## Repo structure notes
- Inside `src`:
    - `generate_svg.py` is the main script to generate the pdf. You can run this from command line or in a notebook.
- Outside `src`: you can download example data and charts and a notebook to run pre-constructed examples that use the library.
- Once you set up your ecosystem, you will see `node_modules/`, which will contain the `npm` packages.


## Resources

- [Allotaxonometer main package](https://github.com/jstonge/allotaxonometer)
- [Allotaxonometer web app](https://allotax.vercel.app/)
- The work and paper leading to these tools is [here](https://doi.org/10.1140/epjds/s13688-023-00400-x).
