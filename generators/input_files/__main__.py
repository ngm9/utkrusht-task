"""
CLI entry point for the input-files generator.

Usage:
    python -m generators.input_files --name "Java" --proficiency BASIC
    python -m generators.input_files --name "Java, Kafka" --proficiency BASIC --dry-run
"""

from generators.input_files.generator import generate_input_files

if __name__ == "__main__":
    generate_input_files()
