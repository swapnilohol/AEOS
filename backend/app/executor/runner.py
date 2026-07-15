import subprocess
import tempfile
import os


def run_python_code(source_code: str):
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".py",
            delete=False,
            mode="w"
        ) as file:
            file.write(source_code)
            file_path = file.name

        result = subprocess.run(
            ["python3", file_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        os.remove(file_path)

        return {
            "output": result.stdout,
            "error": result.stderr,
            "status": "SUCCESS"
        }

    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": "Execution timeout",
            "status": "TIMEOUT"
        }

    except Exception as e:
        return {
            "output": "",
            "error": str(e),
            "status": "FAILED"
        }
