"""Functions to generate allotaxonometer through Python.
Notes:
As a test, run in terminal:
python3 generate_svg.py convert/boys_2022.json convert/boys_2023.json output_charts/test.pdf "0.17" "Boys 2022" "Boys 2023"

If you only want the html file, not the pdf, run:
python3 generate_svg.py convert/boys_2022.json convert/boys_2023.json output_charts/test.pdf "0.17" "Boys 2022" "Boys 2023" --desired_format "html"

If you want RTD data only:
python3 generate_svg.py convert/boys_2022.json convert/boys_2023.json output_data/rtd.json "0.17" "Boys 2022" "Boys 2023" --desired_format "rtd-json"
"""

import argparse
import os
import json
import subprocess
import tempfile
from importlib import resources
from typing import Optional, Dict, Any

from py_allotax.utils import verify_input_data


def generate_svg(
    json_file_1: str,
    json_file_2: str,
    output_file: str,
    alpha: str,
    title1: str,
    title2: str,
    desired_format: str = "pdf",
) -> Optional[Dict[Any, Any]]:
    """Generate static allotaxonometer plot using Svelte SSR + Puppeteer, or return RTD data.
    
    Args:
        json_file_1: Path to first JSON data file
        json_file_2: Path to second JSON data file  
        output_file: Path to save output file
        alpha: Alpha value for RTD calculation
        title1: Title for system 1
        title2: Title for system 2
        desired_format: Output format - "pdf", "html", "rtd-json", "rtd-csv", "rtd-console"
        
    Returns:
        Dict containing RTD data if format is rtd-*, None otherwise
    """
    verify_input_data(json_file_1, json_file_2)
    with open(json_file_1, "r") as file:
        data1_json = json.loads(file.read())
    with open(json_file_2, "r") as file:
        data2_json = json.loads(file.read())

    # Write the json data to a temporary file
    temp_file_path = tempfile.mktemp(suffix=".mjs")
    with open(temp_file_path, "w") as file:
        file.write(f"const data1 = {json.dumps(data1_json)};\n")
        file.write(f"const data2 = {json.dumps(data2_json)};\n")
        file.write(f"const alpha = {alpha};\n")
        file.write(f"const title1 = \"{title1}\";\n")
        file.write(f"const title2 = \"{title2}\";\n")
        file.write("export { data1, data2, alpha, title1, title2 };")

    js_file_path = resources.files('py_allotax').joinpath('generate_svg_minimum.js')
    
    # Convert to absolute paths
    abs_temp_file_path = os.path.abspath(temp_file_path)
    abs_output_file = os.path.abspath(output_file)
    
    # Add format argument to command
    command = ["node", str(js_file_path), abs_temp_file_path, abs_output_file, desired_format]

    # Run the JS file and capture the output
    result = subprocess.run(command, capture_output=True, text=True, cwd=os.path.dirname(js_file_path))

    # Clean up temp file
    try:
        os.unlink(temp_file_path)
    except OSError:
        pass

    # Check if the command was successful
    if result.returncode == 0:
        if desired_format == "pdf":
            print(f"PDF saved to {output_file}")
        elif desired_format == "html":
            print(f"HTML saved to {output_file}")
        elif desired_format.startswith("rtd-"):
            format_type = desired_format.split("-")[1]
            print(f"RTD data saved as {format_type.upper()} to {output_file}")
            
            # If RTD JSON format, load and return the data
            if format_type == "json":
                try:
                    with open(output_file, "r") as f:
                        rtd_data = json.load(f)
                    return rtd_data
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Warning: Could not load RTD data from {output_file}: {e}")
                    return None
            elif format_type == "console":
                # For console output, the RTD data was printed to stdout
                print("RTD data output to console (see above)")
                return None
        
        return None
    else:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise Exception(f"Error in Graph Generation: {result.stderr}")


def generate_rtd_only(
    json_file_1: str,
    json_file_2: str,
    alpha: str,
    title1: str = "",
    title2: str = "",
    output_format: str = "json"
) -> Dict[Any, Any]:
    """Convenience function to generate only RTD data without file output.
    
    Args:
        json_file_1: Path to first JSON data file
        json_file_2: Path to second JSON data file
        alpha: Alpha value for RTD calculation
        title1: Title for system 1 (optional)
        title2: Title for system 2 (optional)  
        output_format: Format for RTD data - "json", "csv", or "console"
        
    Returns:
        Dict containing RTD data
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        temp_output = tmp_file.name
    
    try:
        rtd_data = generate_svg(
            json_file_1=json_file_1,
            json_file_2=json_file_2,
            output_file=temp_output,
            alpha=alpha,
            title1=title1,
            title2=title2,
            desired_format=f"rtd-{output_format}"
        )
        return rtd_data
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_output)
        except OSError:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate allotaxonometer plot or RTD data."
    )
    parser.add_argument(
        "json_file_1", type=str, help="Path to the first json data file."
    )
    parser.add_argument(
        "json_file_2", type=str, help="Path to the second json data file."
    )
    parser.add_argument(
        "output_file", type=str, help="Path to save the output file."
    )
    parser.add_argument("alpha", type=str, help="Alpha value.")
    parser.add_argument("title1", type=str, help="Title for system 1")
    parser.add_argument("title2", type=str, help="Title for system 2.")

    # Optional argument
    parser.add_argument(
        "--desired_format",
        type=str,
        default="pdf",
        choices=["pdf", "html", "rtd-json", "rtd-csv", "rtd-console"],
        help="Desired output format (default: pdf).",
    )

    args = parser.parse_args()

    result = generate_svg(
        args.json_file_1,
        args.json_file_2,
        args.output_file,
        args.alpha,
        args.title1,
        args.title2,
        args.desired_format,
    )
    
    # If RTD data was returned, you could do something with it here
    if result and args.desired_format == "rtd-json":
        print(f"RTD data successfully processed and saved.")
        # Optional: print some summary stats
        if 'rtd' in result:
            print("RTD calculation completed successfully.")