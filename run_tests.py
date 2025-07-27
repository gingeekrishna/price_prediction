#!/usr/bin/env python3
"""
Test Runner Script

A convenient script to run various test configurations
for the Vehicle Price Prediction system.

Usage:
    python run_tests.py [options]
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(command: list, description: str) -> bool:
    """
    Run a command and return success status.
    
    Args:
        command: List of command components
        description: Description of what the command does
        
    Returns:
        True if command succeeded, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {command[0]}")
        return False


def main():
    """Main function to handle command line arguments and run tests."""
    
    parser = argparse.ArgumentParser(description="Test runner for Vehicle Price Prediction")
    
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "all", "coverage", "lint", "format"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--coverage-html",
        action="store_true",
        help="Generate HTML coverage report"
    )
    
    parser.add_argument(
        "--fix-format",
        action="store_true",
        help="Auto-fix formatting issues"
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print(f"🚀 Starting test suite for Vehicle Price Prediction")
    print(f"📁 Working directory: {project_root.absolute()}")
    
    success_count = 0
    total_count = 0
    
    # Define test commands based on arguments
    commands = []
    
    if args.type in ["unit", "all"]:
        cmd = ["python", "-m", "pytest", "tests/", "-m", "unit"]
        if args.verbose:
            cmd.append("-v")
        if args.parallel:
            cmd.extend(["-n", "auto"])
        commands.append((cmd, "Unit Tests"))
    
    if args.type in ["integration", "all"]:
        cmd = ["python", "-m", "pytest", "tests/", "-m", "integration"]
        if args.verbose:
            cmd.append("-v")
        commands.append((cmd, "Integration Tests"))
    
    if args.type == "coverage":
        cmd = ["python", "-m", "pytest", "tests/", "--cov=src", "--cov-report=term-missing"]
        if args.coverage_html:
            cmd.append("--cov-report=html")
        if args.verbose:
            cmd.append("-v")
        commands.append((cmd, "Coverage Tests"))
    
    if args.type == "all" and not args.coverage_html:
        cmd = ["python", "-m", "pytest", "tests/"]
        if args.verbose:
            cmd.append("-v")
        if args.parallel:
            cmd.extend(["-n", "auto"])
        commands.append((cmd, "All Tests"))
    
    if args.type == "lint":
        commands.extend([
            (["flake8", "src/", "tests/"], "Flake8 Linting"),
            (["mypy", "src/"], "Type Checking"),
        ])
    
    if args.type == "format":
        if args.fix_format:
            commands.extend([
                (["black", "src/", "tests/"], "Code Formatting (Black)"),
                (["isort", "src/", "tests/"], "Import Sorting (isort)"),
            ])
        else:
            commands.extend([
                (["black", "--check", "src/", "tests/"], "Code Format Check (Black)"),
                (["isort", "--check-only", "src/", "tests/"], "Import Sort Check (isort)"),
            ])
    
    # Run commands
    for command, description in commands:
        total_count += 1
        if run_command(command, description):
            success_count += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print(f"🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
