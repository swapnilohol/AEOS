from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageConfig:
    image: str
    source_filename: str
    compile_cmd: str | None  # shell command, run in /workspace; None if no compile step
    run_cmd: str  # shell command, run in /workspace, with stdin redirected from input.txt


LANGUAGE_CONFIGS: dict[str, LanguageConfig] = {
    "python": LanguageConfig(
        image="python:3.12-slim",
        source_filename="main.py",
        compile_cmd=None,
        run_cmd="python3 main.py < input.txt",
    ),
    "javascript": LanguageConfig(
        image="node:22-alpine",
        source_filename="main.js",
        compile_cmd=None,
        run_cmd="node main.js < input.txt",
    ),
    "java": LanguageConfig(
        image="eclipse-temurin:21-jdk",
        source_filename="Main.java",
        compile_cmd="javac Main.java",
        run_cmd="java Main < input.txt",
    ),
    "cpp": LanguageConfig(
        image="gcc:13",
        source_filename="main.cpp",
        compile_cmd="g++ -std=c++17 -O2 -o main main.cpp",
        run_cmd="./main < input.txt",
    ),
}


def get_language_config(language: str) -> LanguageConfig:
    key = language.strip().lower()
    if key not in LANGUAGE_CONFIGS:
        supported = ", ".join(sorted(LANGUAGE_CONFIGS))
        raise ValueError(f"Unsupported language '{language}'. Supported: {supported}")
    return LANGUAGE_CONFIGS[key]
