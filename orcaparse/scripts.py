from .file import File
import argparse


def orca_to_html():
    """
    Converts an ORCA output file to an HTML document, with options to include or exclude CSS, JavaScript, a left sidebar (TOC), and a color-comment sidebar.

    The script takes command-line arguments for the input ORCA file and the desired output HTML file path. Additional optional flags can be used to control the inclusion of CSS, JavaScript, and sidebar elements in the generated HTML.

    Usage:
        python script.py input_file output_file [--insert_css] [--insert_js] [--insert_left_sidebar] [--insert_colorcomment_sidebar]

    Arguments:
        input_file: Path to the input ORCA file.
        output_file: Path where the HTML file will be saved.
        --insert_css: Flag to include CSS in the HTML output (included by default, use --no-insert_css to exclude).
        --insert_js: Flag to include JavaScript in the HTML output (included by default, use --no-insert_js to exclude).
        --insert_left_sidebar: Flag to include a left sidebar (TOC) in the HTML output (included by default, use --no-insert_left_sidebar to exclude).
        --insert_colorcomment_sidebar: Flag to include a color-comment sidebar in the HTML output (included by default, use --no-insert_colorcomment_sidebar to exclude).
    """
    # Create a parser for the CLI arguments
    parser = argparse.ArgumentParser(
        description="Convert an ORCA output file to an HTML document with optional features.")

    # Define the CLI arguments
    parser.add_argument("input_file", help="Path to the input ORCA file.")
    parser.add_argument(
        "output_file", help="Path where the HTML file will be saved.")
    parser.add_argument("--insert_css", action="store_false", default=True,
                        help="Exclude CSS from the HTML output. Included by default.")
    parser.add_argument("--insert_js", action="store_false", default=True,
                        help="Exclude JavaScript from the HTML output. Included by default.")
    parser.add_argument("--insert_left_sidebar", action="store_false", default=True,
                        help="Exclude a left sidebar (TOC) from the HTML output. Included by default.")
    parser.add_argument("--insert_colorcomment_sidebar", action="store_false", default=True,
                        help="Exclude a color-comment sidebar from the HTML output. Included by default.")

    # Parse the CLI arguments
    args = parser.parse_args()

    # Initialize the File object and call the save_as_html method
    orca_file = File(file_path=args.input_file)
    orca_file.save_as_html(
        output_file_path=args.output_file,
        insert_css=args.insert_css,
        insert_js=args.insert_js,
        insert_left_sidebar=args.insert_left_sidebar,
        insert_colorcomment_sidebar=args.insert_colorcomment_sidebar
    )


def orca_parse():
    """
    Exports data from an ORCA output file to various formats based on specified criteria. The script supports exporting to CSV, JSON, HTML, and Excel formats.

    The function allows filtering the ORCA elements by their readable name or a substring of their raw data. The extracted data can then be saved in one of the supported formats, with CSV being the default.

    Usage:
        python script.py input_file output_file [--format csv|json|html|excel] [--readable_name NAME] [--raw_data_substring SUBSTRING]

    Arguments:
        input_file: Path to the input ORCA file.
        output_file: Path where the output file will be saved.
        --format: Desired output format (csv, json, html, excel). Defaults to 'csv'.
        --readable_name: Filter elements by their readable name (optional).
        --raw_data_substring: Filter elements by a substring of their raw data (optional).
    """
    # Create a parser for the CLI arguments
    parser = argparse.ArgumentParser(
        description="Export the raw or processed data from an ORCA output file based on specified criteria.")

    # Define the CLI arguments
    parser.add_argument("input_file", help="Path to the input ORCA file.")
    parser.add_argument(
        "output_file", help="Path where the output file will be saved.")
    parser.add_argument("-f", "--format", choices=['csv', 'json', 'html', 'excel'], default='csv',
                        help="Output format (csv, json, html, excel). Default is csv.")
    parser.add_argument("--readable_name", default=None,
                        help="Filter elements by their readable name.")
    parser.add_argument("--raw_data_substring", default=None,
                        help="Filter elements by a substring of their raw data.")

    # Parse the CLI arguments
    args = parser.parse_args()

    # Initialize the File object
    orca_file = File(file_path=args.input_file)

    # Get the data based on the specified criteria and extract_raw set to True
    data = orca_file.get_data(
        extract_raw=True, readable_name=args.readable_name, raw_data_substring=args.raw_data_substring)[['Type', 'Subtype', 'Position', 'ExtractedData']]

    # Sort the DataFrame by the 'Position' column
    data_sorted = data.sort_values(by='Position')

    # Save the data in the chosen format
    if args.format == 'csv':
        data_sorted.to_csv(args.output_file, index=False)
    elif args.format == 'json':
        data_sorted.to_json(args.output_file, orient="records", lines=True)
    elif args.format == 'html':
        data_sorted.to_html(args.output_file, index=False)
    elif args.format == 'excel':
        # Ensure you have the necessary dependencies installed for Excel output
        data_sorted.to_excel(args.output_file, index=False)
