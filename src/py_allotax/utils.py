"""Convert data files from csv or js format to json.

Note:
- CSV file must be in the final format you would use in the allotax webapp
with columns of these names and ordering: ['types', 'counts', 'total_unique', 'probs']
"""

import os
import json
import subprocess
import tempfile
import pandas as pd
from importlib import resources

def get_rtd(json_file_1: str, json_file_2: str, alpha: str, top_n: int = 30):
    """Get RTD + words driving divergence as DataFrame.
    
    Args:
        top_n: Number of top words to return. Use 0 or -1 for all words.
    """
    
    # Load data
    with open(json_file_1) as f:
        data1 = json.load(f)
    with open(json_file_2) as f:
        data2 = json.load(f)
    
    # Create temp files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as input_file, \
         tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_file:
        
        # Write JS input file
        input_file.write(f"""
const data1 = {json.dumps(data1)};
const data2 = {json.dumps(data2)};
const alpha = {alpha};
const title1 = "";
const title2 = "";
export {{ data1, data2, alpha, title1, title2 }};
""")
        input_file.flush()
        
        # Run JS script
        js_file = resources.files('py_allotax').joinpath('generate_svg_minimum.js')
        subprocess.run([
            "node", str(js_file), 
            input_file.name, 
            output_file.name, 
            "rtd-json",
            str(top_n if top_n > 0 else 0)  # Pass top_n to JS
        ], check=True)
        
        # Read result
        with open(output_file.name) as f:
            result = json.load(f)
        
        # Convert to DataFrame
        words_df = pd.DataFrame(result['barData'])
        
        return {
            'rtd': result['rtd'],
            'words_df': words_df,
            'total_words': result.get('total_words', len(words_df))
        }
def strip_export_statement(js_content):
    """Strip the 'export const data =' part from the JS content."""
    return js_content.replace("export const data =", "").strip()


def convert_csv_data(desired_format: str, path1: str, path2: str) -> None:
    """Convert 2 data files from .csv format to .json or .js format.
    Args:
        desired_format: The format to convert to ('json' or 'js').
        path1: Path to the first CSV file (with extension).
        path2: Path to the second CSV file (with extension).
    """
    extensions = {"json": ".json", "js": ".js"}  # Supported formats

    for path in [path1, path2]:
        # Load the data
        df = pd.read_csv(f"{path}")
        # change col name total_unique to totalunique
        df.rename(columns={"total_unique": "totalunique"}, inplace=True)
        df["probs"] = df["probs"].round(4)
        # re-order cols to types, counts, totalunique, probs
        df = df[["types", "counts", "totalunique", "probs"]]

        # Convert the data to a dictionary
        data = df.to_dict(orient="records")

        # Save both datasets as variables to a json file
        f_type = extensions[desired_format]
        # Re-use filename without extension (strip .csv)
        f_name = os.path.basename(path).rsplit(".", 1)[0]
        with open(f"{f_name}{f_type}", "w", encoding="utf-8") as f:
            if desired_format == "js":
                f.write(f"export const data = {json.dumps(data)};")
            else:
                json.dump(data, f, ensure_ascii=False, indent=4)


def convert_js_data(desired_format: str, path1: str, path2: str) -> None:
    """Convert 2 data files from .js format to .csv or .json format.
    Args:
        desired_format: The format to convert to ('csv' or 'json').
        path1: Path to the first .js file (with extension).
        path2: Path to the second .js file (with extension).
    """
    for path in [path1, path2]:
        # Re-use filename without extension (strip .js)
        f_name = os.path.basename(path).rsplit(".", 1)[0]

        # Load the data
        with open(f"{path}", "r") as f:
            js_content = f.read()
            data = json.loads(strip_export_statement(js_content))
            if desired_format == "csv":
                df = pd.DataFrame(data)
                df.to_csv(f"{f_name}.csv", index=False)
            else:
                with open(f"{f_name}.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)


def verify_input_data(datafile_1, datafile_2) -> None:
    """Verifies the format of provided files match the required json format with
    keys: ['types', 'counts', 'totalunique', 'probs'].
    """
    for file in [datafile_1, datafile_2]:
        # verify the data opens (otherwise return note about invalid json structure)
        try:
            with open(file, "r") as f:
                data = json.loads(f.read())
        except json.JSONDecodeError:
            raise ValueError(
                f"Invalid JSON structure in {file}. File should be"
                + "a .json wherein the data is a list of dictionaries."
            )
        # verify the data has the required keys
        if not all(k in data[0] for k in ["types", "counts", "totalunique", "probs"]):
            raise ValueError(
                f"Data in {file} does not match the required format: ['types', 'counts', 'totalunique', 'probs']"
            )
