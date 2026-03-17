"""
Output formatters for sanpy CLI.

Supports JSON, CSV, and table (human-readable) output formats.
"""

import csv
import io
import json
from typing import List

import pandas as pd
import typer


def format_dataframe(df: pd.DataFrame, fmt: str = "table") -> str:
    """
    Format a pandas DataFrame for CLI output.

    Args:
        df: The DataFrame to format
        fmt: Output format - 'json', 'csv', or 'table'

    Returns:
        Formatted string representation
    """
    if fmt == "json":
        # Reset index to include datetime in output
        if df.index.name == "datetime" or isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()
        return df.to_json(orient="records", date_format="iso", indent=2)
    elif fmt == "csv":
        return df.to_csv()
    else:  # table (default)
        return df.to_string()


def format_list(items: List[str], fmt: str = "table", header: str = "name") -> str:
    """
    Format a list of strings for CLI output.

    Args:
        items: List of strings to format
        fmt: Output format - 'json', 'csv', or 'table'
        header: Column header for CSV output

    Returns:
        Formatted string representation
    """
    if fmt == "json":
        return json.dumps(items, indent=2)
    elif fmt == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
        writer.writerow([header])
        for item in items:
            writer.writerow([item])
        return buffer.getvalue().rstrip("\n")
    else:  # table
        return "\n".join(items)


def format_dict(data: dict, fmt: str = "table") -> str:
    """
    Format a dictionary for CLI output.

    Args:
        data: Dictionary to format
        fmt: Output format - 'json', 'csv', or 'table'

    Returns:
        Formatted string representation
    """
    if fmt == "json":
        return json.dumps(data, indent=2, default=str)
    elif fmt == "csv":
        # Use csv module for proper escaping of commas, quotes, and newlines
        buffer = io.StringIO()
        writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["key", "value"])
        for k, v in data.items():
            writer.writerow([k, v])
        return buffer.getvalue().rstrip("\n")
    else:  # table
        max_key_len = max(len(str(k)) for k in data.keys()) if data else 0
        lines = []
        for k, v in data.items():
            lines.append(f"{str(k).ljust(max_key_len)}  {v}")
        return "\n".join(lines)


def format_api_calls(calls: List[tuple], fmt: str = "table") -> str:
    """
    Format API calls history for CLI output.

    Args:
        calls: List of (datetime, count) tuples
        fmt: Output format - 'json', 'csv', or 'table'

    Returns:
        Formatted string representation
    """
    if fmt == "json":
        data = [{"date": str(date), "api_calls": count} for date, count in calls]
        return json.dumps(data, indent=2)
    elif fmt == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["date", "api_calls"])
        for date, count in calls:
            writer.writerow([date, count])
        return buffer.getvalue().rstrip("\n")
    else:  # table
        if not calls:
            return "No API calls recorded"
        lines = ["Date                 API Calls", "-" * 35]
        for date, count in calls:
            lines.append(f"{str(date).ljust(20)} {count}")
        return "\n".join(lines)


def output(text: str, err: bool = False) -> None:
    """
    Print text to stdout or stderr.

    Args:
        text: Text to print
        err: If True, print to stderr
    """
    typer.echo(text, err=err)
