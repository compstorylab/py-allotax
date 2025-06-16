"""Claude generated"""
import subprocess
import pytest
import os
import json

class TestGenerateSVGBenchmark:
    
    @pytest.mark.benchmark
    @pytest.mark.parametrize("file1,file2,description", [
        ("example_data/boys_1968.json", "example_data/boys_2018.json", "Large_files_1968_2018"),
        ("example_data/boys_1895.json", "example_data/boys_2018.json", "Small_vs_Large_1895_2018"),
        ("example_data/boys_1895.json", "example_data/boys_1968.json", "Small_vs_Medium_1895_1968"),
    ], ids=["Large files (1968+2018)", "Small vs Large (1895+2018)", "Small vs Medium (1895+1968)"])
    def test_generate_svg_performance(self, benchmark, file1, file2, description, tmp_path):
        """Benchmark the script execution with different file combinations"""
        
        # Collect file metadata
        file1_size = os.path.getsize(file1) if os.path.exists(file1) else 0
        file2_size = os.path.getsize(file2) if os.path.exists(file2) else 0
        
        # Add metadata to benchmark
        benchmark.extra_info.update({
            'test_description': description,
            'file1_path': file1,
            'file2_path': file2,
            'file1_size_kb': round(file1_size / 1024, 1),
            'file2_size_kb': round(file2_size / 1024, 1),
            'total_input_size_kb': round((file1_size + file2_size) / 1024, 1)
        })
        
        output_file = tmp_path / f"test_{description}.pdf"
        
        args = [
            "python", "src/py_allotax/generate_svg.py",
            file1, file2, str(output_file), "0.17", 
            "Boys-File1", "Boys-File2"
        ]
        
        def run_script():
            return subprocess.run(args, check=True, capture_output=True, text=True)
        
        result = benchmark.pedantic(run_script, rounds=3, iterations=1)
        assert result.returncode == 0
        assert output_file.exists()