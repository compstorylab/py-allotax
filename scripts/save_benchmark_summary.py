#!/usr/bin/env python3
"""Claude generated"""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

def get_project_version():
    """Get current project version from pyproject.toml"""
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip().startswith('version = '):
                    return line.split('=')[1].strip().strip('"\'')
    except:
        pass
    return "unknown"

def get_git_info():
    """Get git commit and check if dirty"""
    try:
        commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], text=True).strip()
        status = subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip()
        dirty = bool(status)
        return commit + ("-dirty" if dirty else "")
    except:
        return "unknown"

def get_file_info(filepath):
    """Get file size and record count"""
    if not os.path.exists(filepath):
        return {"size_kb": 0, "records": 0}
    
    size_bytes = os.path.getsize(filepath)
    size_kb = round(size_bytes / 1024, 1)
    
    # Try to count records in JSON
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                records = len(data)
            elif isinstance(data, dict) and 'data' in data:
                records = len(data['data'])
            else:
                records = 1
    except:
        records = 0
    
    return {"size_kb": size_kb, "records": records}

def extract_file_paths(test_name):
    """Extract file paths from test name"""
    file_mapping = {
        "Large files (1968+2018)": {
            "file1": "example_data/boys_1968.json",
            "file2": "example_data/boys_2018.json"
        },
        "Small vs Large (1895+2018)": {
            "file1": "example_data/boys_1895.json",
            "file2": "example_data/boys_2018.json"
        },
        "Small vs Medium (1895+1968)": {
            "file1": "example_data/boys_1895.json",
            "file2": "example_data/boys_1968.json"
        }
    }
    
    return file_mapping.get(test_name, {"file1": "", "file2": ""})

def save_simple_summary():
    """Save a simple benchmark summary with file size info"""
    benchmarks_dir = Path(".benchmarks")
    if not benchmarks_dir.exists():
        print("No .benchmarks directory found. Run benchmarks first.")
        return
    
    results_files = list(benchmarks_dir.rglob("*.json"))
    if not results_files:
        print("No benchmark results found.")
        return
    
    latest_file = max(results_files, key=os.path.getmtime)
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    # Create summary with version and file info
    summary = {
        "timestamp": datetime.now().isoformat()[:19],
        "version": get_project_version(),
        "git_commit": get_git_info(),
        "results": []
    }
    
    for bench in data.get("results", []):
        name = bench["name"]
        stats = bench["stats"]
        
        # Extract description
        if "Large files" in name:
            desc = "Large files (1968+2018)"
        elif "Small vs Large" in name:
            desc = "Small vs Large (1895+2018)"  
        elif "Small vs Medium" in name:
            desc = "Small vs Medium (1895+1968)"
        else:
            desc = name
        
        # Get file paths and sizes
        file_paths = extract_file_paths(desc)
        file1_info = get_file_info(file_paths["file1"])
        file2_info = get_file_info(file_paths["file2"])
        
        summary["results"].append({
            "test": desc,
            "mean_time": round(stats["mean"], 3),
            "min_time": round(stats["min"], 3),
            "rounds": stats.get("rounds", 1),
            "files": {
                "file1": {
                    "path": file_paths["file1"],
                    "size_kb": file1_info["size_kb"],
                    "records": file1_info["records"]
                },
                "file2": {
                    "path": file_paths["file2"], 
                    "size_kb": file2_info["size_kb"],
                    "records": file2_info["records"]
                },
                "total_size_kb": file1_info["size_kb"] + file2_info["size_kb"],
                "total_records": file1_info["records"] + file2_info["records"]
            }
        })
    
    # Save to .benchmarks directory
    summary_file = benchmarks_dir / "summary_history.json"
    
    # Load existing history
    history = []
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            history = json.load(f)
    
    # Add new entry
    history.append(summary)
    
    # Keep only last 50 entries
    history = history[-50:]
    
    # Save
    with open(summary_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"Summary saved to {summary_file}")
    print(f"Version: {summary['version']}, Commit: {summary['git_commit']}")
    
    # Show file sizes in current run
    print(f"\nFile sizes in this run:")
    for result in summary["results"]:
        files = result["files"]
        print(f"  {result['test']}: {files['total_size_kb']}KB total ({files['total_records']} records)")
        print(f"    File1: {files['file1']['size_kb']}KB ({files['file1']['records']} records)")
        print(f"    File2: {files['file2']['size_kb']}KB ({files['file2']['records']} records)")
    
    # Show comparisons
    show_comparisons(history)

def show_comparisons(history):
    """Show comparison with previous runs"""
    if len(history) < 2:
        print("Need more runs for comparison.")
        return
    
    curr = history[-1]
    
    print(f"\n📊 PERFORMANCE COMPARISONS")
    print("=" * 60)
    
    # Compare with previous run
    prev = history[-2]
    print(f"\nVs Previous Run ({prev['version']} @ {prev['git_commit']}):")
    compare_runs(prev, curr)
    
    # Compare with same version (if exists)
    same_version_runs = [h for h in history[:-1] if h['version'] == curr['version']]
    if same_version_runs:
        baseline = same_version_runs[-1]
        print(f"\nVs Same Version Baseline ({baseline['git_commit']}):")
        compare_runs(baseline, curr)

def compare_runs(baseline, current):
    """Compare two benchmark runs with file size info"""
    for curr_result in current["results"]:
        test_name = curr_result["test"]
        curr_time = curr_result["mean_time"]
        curr_size = curr_result["files"]["total_size_kb"]
        
        baseline_result = next((r for r in baseline["results"] if r["test"] == test_name), None)
        if baseline_result:
            baseline_time = baseline_result["mean_time"]
            baseline_size = baseline_result["files"]["total_size_kb"]
            
            time_change = ((curr_time - baseline_time) / baseline_time) * 100
            size_change = curr_size - baseline_size
            
            if abs(time_change) < 1:
                icon = "➡️"
            elif time_change > 5:
                icon = "🔴"
            elif time_change < -5:
                icon = "🟢"
            elif time_change > 0:
                icon = "🟡"
            else:
                icon = "🟡"
            
            size_info = f" | {curr_size}KB" + (f" ({size_change:+.1f}KB)" if size_change != 0 else "")
            print(f"  {icon} {test_name}: {baseline_time:.3f}s → {curr_time:.3f}s ({time_change:+.1f}%){size_info}")
        else:
            print(f"  ➕ {test_name}: {curr_time:.3f}s | {curr_size}KB (new test)")

def show_history(limit=10):
    """Show recent benchmark history with file sizes"""
    summary_file = Path(".benchmarks/summary_history.json")
    if not summary_file.exists():
        print("No benchmark history found.")
        return
    
    with open(summary_file, 'r') as f:
        history = json.load(f)
    
    print(f"\n📈 RECENT BENCHMARK HISTORY (last {limit} runs)")
    print("=" * 80)
    
    for run in history[-limit:]:
        print(f"\n{run['timestamp']} | v{run['version']} @ {run['git_commit']}")
        for result in run['results']:
            files = result['files']
            print(f"  {result['test']}: {result['mean_time']:.3f}s | {files['total_size_kb']}KB ({files['total_records']} records)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        show_history(limit)
    else:
        save_simple_summary()