import argparse
import os
from typing import Optional

from .file import File


def orca_to_html(input_file: str, output_file: str, insert_css: bool = True, insert_js: bool = True,
                 insert_left_sidebar: bool = True, insert_colorcomment_sidebar: bool = True):
    """
    Converts an ORCA output file to an HTML document, optionally including CSS, JavaScript, a left sidebar (TOC),
    and a color-comment sidebar.

    Parameters:
        input_file (str): Path to the input ORCA file.
        output_file (str): Path where the HTML file will be saved.
        insert_css (bool): Flag to include CSS in the HTML output. Included by default.
        insert_js (bool): Flag to include JavaScript in the HTML output. Included by default.
        insert_left_sidebar (bool): Flag to include a left sidebar (TOC) in the HTML output. Included by default.
        insert_colorcomment_sidebar (bool): Flag to include a color-comment sidebar in the HTML output. Included by default.

    This function does not return any value but outputs the converted HTML file to the specified output path.
    """
    # Assuming the existence of a `File` class and its `save_as_html` method as in the original script
    orca_file = File(file_path=input_file)
    orca_file.save_as_html(
        output_file_path=output_file,
        insert_css=insert_css,
        insert_js=insert_js,
        insert_left_sidebar=insert_left_sidebar,
        insert_colorcomment_sidebar=insert_colorcomment_sidebar
    )


def orca_to_html_cli():
    """
    Parses command-line arguments to convert an ORCA output file to an HTML document with optional features.

    This function is the entry point when using the script from the command line. It handles parsing the input and output file paths, as well as optional flags for including CSS, JavaScript, a left sidebar (TOC), and a color-comment sidebar in the generated HTML document.

    The flags for optional features are set to include the features by default. Use '--no-' prefix to exclude a feature (e.g., --no-insert_css).
    """
    parser = argparse.ArgumentParser(
        description="Convert an ORCA output file to an HTML document with optional features.")

    parser.add_argument("input_file", type=str,
                        help="Path to the input ORCA file.")
    parser.add_argument("output_file", type=str,
                        help="Path where the HTML file will be saved.")
    parser.add_argument("--insert_css", action="store_false", default=True,
                        help="Exclude CSS from the HTML output. Included by default.")
    parser.add_argument("--insert_js", action="store_false", default=True,
                        help="Exclude JavaScript from the HTML output. Included by default.")
    parser.add_argument("--insert_left_sidebar", action="store_false", default=True,
                        help="Exclude a left sidebar (TOC) from the HTML output. Included by default.")
    parser.add_argument("--insert_colorcomment_sidebar", action="store_false", default=True,
                        help="Exclude a color-comment sidebar from the HTML output. Included by default.")

    args = parser.parse_args()

    orca_to_html(input_file=args.input_file, output_file=args.output_file,
                 insert_css=args.insert_css, insert_js=args.insert_js,
                 insert_left_sidebar=args.insert_left_sidebar,
                 insert_colorcomment_sidebar=args.insert_colorcomment_sidebar)


def orca_parse(input_file: str, output_file: str, file_format: str = 'auto', readable_name: Optional[str] = None,
               raw_data_substrings: list[str] = []):
    """
    Exports data from an ORCA output file to various formats based on specified filtering criteria.

    The function supports CSV, JSON, HTML, and Excel formats for output, with 'auto' format detection based on the output file extension. It also allows for filtering the ORCA elements by their readable name or substrings of their raw data.

    Parameters:
        input_file (str): Path to the input ORCA file.
        output_file (str): Path where the output file will be saved.
        file_format (str): Desired output format ('auto', 'csv', 'json', 'html', 'xlsx'). Defaults to 'auto'.
        readable_name (Optional[str]): Filter elements by their readable name (None by default).
        raw_data_substrings (list[str]): list of substrings to filter elements by their raw data ([] by default).

    The function doesn't return any value but saves the extracted data to the specified output path in the chosen format.
    """
    # Assuming the existence of a `File` class with a `get_data` method as indicated in the original script
    orca_file = File(file_path=input_file)
    data = orca_file.get_data(
        extract_only_raw=True, readable_name=readable_name, raw_data_substring=raw_data_substrings).drop('Element', axis=1)
    data_sorted = data.sort_values(by='Position')

    if file_format == 'auto':
        file_format = os.path.splitext(output_file)[-1][1:]

    if file_format == 'csv':
        data_sorted.to_csv(output_file, index=False)
    elif file_format == 'json':
        data_sorted.to_json(output_file, orient="records", lines=True)
    elif file_format == 'html':
        data_sorted.to_html(output_file, index=False)
    elif file_format == 'xlsx':
        data_sorted.to_excel(output_file, index=False)


def orca_parse_cli():
    """
    Parses command-line arguments to export data from an ORCA output file to specified formats based on filtering criteria.

    The script supports exporting to CSV, JSON, HTML, and Excel formats, with the option to filter ORCA elements by their readable name or substrings of their raw data.

    The function serves as the entry point when the script is executed from the command line, handling the parsing of input and output file paths, output format, and filtering options.
    """
    parser = argparse.ArgumentParser(
        description="Export data from an ORCA output file to specified formats based on filtering criteria.")

    parser.add_argument("input_file", type=str,
                        help="Path to the input ORCA file.")
    parser.add_argument("output_file", type=str,
                        help="Path where the output file will be saved.")
    parser.add_argument("-f", "--format", choices=['auto', 'csv', 'json', 'html', 'xlsx'], default='auto',
                        help="Output format (csv, json, html, xlsx). Defaults to 'auto' for detection based on file extension.")
    parser.add_argument("--readable_name", type=str, default=None,
                        help="Filter elements by their readable name.")
    parser.add_argument("--raw_data_substring", action='append', default=[],
                        help="Filter elements by a substring of their raw data. Can be used multiple times.")

    args = parser.parse_args()

    orca_parse(input_file=args.input_file, output_file=args.output_file, file_format=args.format,
               readable_name=args.readable_name, raw_data_substrings=args.raw_data_substring)
