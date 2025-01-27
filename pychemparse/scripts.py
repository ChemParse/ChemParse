import argparse
import os
from typing import Optional

from .file import File


def chem_to_html(input_file: str, output_file: str, insert_css: bool = True, insert_js: bool = True,
                 insert_left_sidebar: bool = True, insert_colorcomment_sidebar: bool = True, mode: str = 'ORCA') -> None:
    """
    Converts an ORCA (or GPAW) output file to an HTML document with various optional features like CSS, JavaScript, and sidebars.

    :param input_file: The path to the input file, typically an ORCA output file.
    :type input_file: str
    :param output_file: The destination path where the HTML file will be saved.
    :type output_file: str
    :param insert_css: If `True`, includes default CSS styles in the HTML output.
    :type insert_css: bool, optional
    :param insert_js: If `True`, includes JavaScript for interactive elements in the HTML output.
    :type insert_js: bool, optional
    :param insert_left_sidebar: If `True`, adds a left sidebar for navigation in the HTML output.
    :type insert_left_sidebar: bool, optional
    :param insert_colorcomment_sidebar: If `True`, adds a sidebar for color-coded comments in the HTML output.
    :type insert_colorcomment_sidebar: bool, optional
    :param mode: Specifies the processing mode, which can be 'ORCA', 'GPAW' or 'VASP'. Default is 'ORCA'.
    :type mode: str, optional
    """
    orca_file = File(file_path=input_file, mode=mode)
    orca_file.save_as_html(
        output_file_path=output_file,
        insert_css=insert_css,
        insert_js=insert_js,
        insert_left_sidebar=insert_left_sidebar,
        insert_colorcomment_sidebar=insert_colorcomment_sidebar
    )


def chem_to_html_cli() -> None:
    """
    CLI entry point for converting an ORCA or GPAW output file to an HTML document. Parses command-line arguments for input and output file paths and optional features.

    This function facilitates the use of the conversion utility from the command line, allowing users to specify the input and output files as well as toggle optional features like CSS, JavaScript, and sidebars via command-line flags.
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
    parser.add_argument("--mode", choices=['ORCA', 'GPAW', 'VASP'], default='ORCA',
                        help="Mode of the input file ('ORCA', 'GPAW' or 'VASP'). Defaults to 'ORCA'.")

    args = parser.parse_args()

    chem_to_html(input_file=args.input_file, output_file=args.output_file,
                 insert_css=args.insert_css, insert_js=args.insert_js,
                 insert_left_sidebar=args.insert_left_sidebar,
                 insert_colorcomment_sidebar=args.insert_colorcomment_sidebar,
                 mode=args.mode
                 )


def chem_parse(input_file: str, output_file: str, file_format: str = 'auto',
               readable_name: Optional[str] = None,
               raw_data_substrings: list[str] = [],
               raw_data_not_substrings: list[str] = [],
               mode: str = 'ORCA'):
    """
    Parses an ORCA (or GPAW) output file and exports filtered data to the specified format.

    This function supports exporting to CSV, JSON, HTML, and Excel formats. The output format can be auto-detected based on the file extension of the output path. Data can be filtered by readable names or the presence/absence of specific substrings in the raw data.

    :param input_file: The path to the ORCA output file to be processed.
    :type input_file: str
    :param output_file: The file path where the exported data will be saved.
    :type output_file: str
    :param file_format: The desired output format ('auto', 'csv', 'json', 'html', 'xlsx'). If 'auto', the format is inferred from the output file extension.
    :type file_format: str, optional
    :param readable_name: Filters elements by their readable name, if specified.
    :type readable_name: Optional[str], optional
    :param raw_data_substrings: Filters elements containing these substrings in their raw data.
    :type raw_data_substrings: list[str], optional
    :param raw_data_not_substrings: Filters elements not containing these substrings in their raw data.
    :type raw_data_not_substrings: list[str], optional
    :param mode: Specifies the mode of the input file, which can be 'ORCA', 'GPAW' or 'VASP'. Default is 'ORCA'.
    :type mode: str, optional
    """
    orca_file = File(file_path=input_file, mode=mode)
    data = orca_file.get_data(
        extract_only_raw=True, readable_name=readable_name,
        raw_data_substring=raw_data_substrings,
        raw_data_not_substring=raw_data_not_substrings).drop('Element', axis=1)
    data_sorted = data.sort_values(by='CharPosition')

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


def chem_parse_cli():
    """
    Command-line interface for the `chem_parse` function, allowing users to export data from an ORCA output file from the terminal.

    This CLI provides options for specifying the input and output file paths, the desired output format, filtering criteria based on readable names and raw data substrings, and the processing mode.
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
    parser.add_argument("--raw_data_not_substring", action='append', default=[],
                        help="Filter elements by absence of a substring of their raw data. Can be used multiple times.")
    parser.add_argument("--mode", choices=['ORCA', 'GPAW', 'VASP'], default='ORCA',
                        help="Mode of the input file ('ORCA', 'GPAW' or 'VASP'). Defaults to 'ORCA'.")

    args = parser.parse_args()

    chem_parse(input_file=args.input_file, output_file=args.output_file, file_format=args.format,
               readable_name=args.readable_name, raw_data_substrings=args.raw_data_substring,
               raw_data_not_substrings=args.raw_data_not_substring, mode=args.mode)
