"""
Command-line interface for benchmarking functionality.

This module provides a command-line interface for running parameter
optimization, comparison, and benchmarking tasks.
"""

import argparse
import sys

from ..config.paths import get_data_directory


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Local Deep Research Benchmarking Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run parameter optimization
  python -m local_deep_research.benchmarks.cli optimize "What are the latest advancements in quantum computing?"

  # Compare different configurations
  python -m local_deep_research.benchmarks.cli compare "What are the effects of climate change?" --configs configs.json

  # Run efficiency profiling
  python -m local_deep_research.benchmarks.cli profile "How do neural networks work?"
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Optimizer parser
    optimize_parser = subparsers.add_parser(
        "optimize", help="Optimize parameters"
    )
    optimize_parser.add_argument("query", help="Research query to optimize for")
    optimize_parser.add_argument(
        "--output-dir",
        default=str(get_data_directory() / "optimization_results"),
        help="Directory to save results",
    )
    optimize_parser.add_argument("--model", help="Model name for the LLM")
    optimize_parser.add_argument("--provider", help="Provider for the LLM")
    optimize_parser.add_argument("--search-tool", help="Search tool to use")
    optimize_parser.add_argument(
        "--temperature", type=float, default=0.7, help="LLM temperature"
    )
    optimize_parser.add_argument(
        "--n-trials",
        type=int,
        default=30,
        help="Number of parameter combinations to try",
    )
    optimize_parser.add_argument(
        "--timeout", type=int, help="Maximum seconds to run optimization"
    )
    optimize_parser.add_argument(
        "--n-jobs",
        type=int,
        default=1,
        help="Number of parallel jobs for optimization",
    )
    optimize_parser.add_argument(
        "--study-name", help="Name of the Optuna study"
    )
    optimize_parser.add_argument(
        "--speed-focus", action="store_true", help="Focus optimization on speed"
    )
    optimize_parser.add_argument(
        "--quality-focus",
        action="store_true",
        help="Focus optimization on quality",
    )

    # Comparison parser
    compare_parser = subparsers.add_parser(
        "compare", help="Compare configurations"
    )
    compare_parser.add_argument("query", help="Research query to compare with")
    compare_parser.add_argument(
        "--configs",
        required=True,
        help="JSON file with configurations to compare",
    )
    compare_parser.add_argument(
        "--output-dir",
        default="data/benchmark_results/comparison",
        help="Directory to save results",
    )
    compare_parser.add_argument("--model", help="Model name for the LLM")
    compare_parser.add_argument("--provider", help="Provider for the LLM")
    compare_parser.add_argument("--search-tool", help="Search tool to use")
    compare_parser.add_argument(
        "--repetitions",
        type=int,
        default=1,
        help="Number of repetitions for each configuration",
    )

    # Profiling parser
    profile_parser = subparsers.add_parser(
        "profile", help="Profile resource usage"
    )
    profile_parser.add_argument("query", help="Research query to profile")
    profile_parser.add_argument(
        "--output-dir",
        default="data/benchmark_results/profiling",
        help="Directory to save results",
    )
    profile_parser.add_argument("--model", help="Model name for the LLM")
    profile_parser.add_argument("--provider", help="Provider for the LLM")
    profile_parser.add_argument("--search-tool", help="Search tool to use")
    profile_parser.add_argument(
        "--iterations", type=int, default=2, help="Number of search iterations"
    )
    profile_parser.add_argument(
        "--questions", type=int, default=2, help="Questions per iteration"
    )
    profile_parser.add_argument(
        "--strategy", default="iterdrag", help="Search strategy to use"
    )

    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    parse_args()

    print(
        "This legacy CLI is deprecated. "
        "Please use 'ldr benchmark' (cli/benchmark_commands.py) instead."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
