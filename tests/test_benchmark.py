import subprocess
import pytest
import os

class TestGenerateSVGBenchmark:
    
    @pytest.mark.parametrize("file1,file2,description", [
        ("example_data/boys_1968.json", "example_data/boys_2018.json", "Large_files_1968_2018"),
        ("example_data/boys_1895.json", "example_data/boys_2018.json", "Small_vs_Large_1895_2018"),
        ("example_data/boys_1895.json", "example_data/boys_1968.json", "Small_vs_Medium_1895_1968"),
        ("example_data/boys_2022.json", "example_data/boys_2023.json", "Recent_Large_2022_2023"),
    ], ids=[
        "Large files (1968+2018)", 
        "Small vs Large (1895+2018)", 
        "Small vs Medium (1895+1968)",
        "Recent Large (2022+2023)"
    ])
    def test_generate_svg_performance(self, benchmark, file1, file2, description, tmp_path):
        """Benchmark the script execution with different file combinations"""
        
        # Store the actual file paths in benchmark metadata
        benchmark.extra_info.update({
            'file1_path': file1,
            'file2_path': file2,
            'test_description': description
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