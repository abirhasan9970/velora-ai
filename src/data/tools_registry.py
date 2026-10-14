register(ToolSpec(
    name="upload_dataset",
    description=(
        "Copy a CSV/Excel file from anywhere on disk into the project's uploads folder. "
        "Use this when the user wants to analyze a file that isn't already in the uploads dir. "
        "Provide the full file path."
    ),
    parameters={"source_path": "Absolute path to the file on disk, e.g. 'C:/Users/me/Downloads/data.csv'"},
    function=__import__("src.tools.upload_tools", fromlist=["tool_upload_dataset"]).tool_upload_dataset,
))

register(ToolSpec(
    name="generate_report",
    description=(
        "Generate a full Markdown analysis report for a dataset in uploads/. "
        "Includes overview, summary statistics, correlations, outliers, and charts. "
        "Returns the report file path and chart paths."
    ),
    parameters={"filename": "Name of the file in the uploads folder"},
    function=__import__("src.tools.upload_tools", fromlist=["tool_generate_report"]).tool_generate_report,
))
