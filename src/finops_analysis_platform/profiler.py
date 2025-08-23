import pandas as pd
from ydata_profiling import ProfileReport
from pathlib import Path

def create_profile_report(df: pd.DataFrame, title: str, output_dir: str = 'profiling_reports'):
    """
    Generates a data profiling report for a given DataFrame and saves it as an HTML file.

    Args:
        df: The DataFrame to profile.
        title: The title for the profiling report.
        output_dir: The directory where the report will be saved.
    """
    # Create the output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate the profile report
    profile = ProfileReport(df, title=title, explorative=True)

    # Save the report to an HTML file
    output_path = Path(output_dir) / f"{title.lower().replace(' ', '_')}_profile.html"
    profile.to_file(output_path)

    print(f"✅ Data profiling report saved to {output_path}")
    return str(output_path)
