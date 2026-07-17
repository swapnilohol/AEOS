import subprocess
import tempfile


def execute_python(code: str, input_data: str = ""):

    runner_code = f"""
import json

{code}

data = json.loads({input_data!r})

result = solve(**data)

print(result)
"""

    with tempfile.NamedTemporaryFile(
        suffix=".py",
        mode="w",
        delete=False
    ) as f:

        f.write(runner_code)
        file_path = f.name


    try:
        result = subprocess.run(
            ["python3", file_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        return {
            "status": "SUCCESS",
            "output": result.stdout.strip(),
            "error": result.stderr
        }


    except Exception as e:

        return {
            "status": "FAILED",
            "output": "",
            "error": str(e)
        }
