# OrcaParse

![logo](image/README/logo.png)

## About

Package for extracting the data from ORCA .out files.

This package is not only made to extract the data from premade extraction patterns but is mostly aimed toward the creation of user extraction patterns from the unknown blocks, to warranty the extraction from the outputs from the different ORCA versions.

It prevents the extraction of the data from incorrect parts of the output and creates the marking of the document.

## Python

Example of the pandas.DataFrame with the extracted data, both premade and created by a user. See examples for more details.


![python](image/README/python_pd.png)

## Scripts

The data can be extracted from the shell (see examples):


![scipt](image/README/script_html.png "HTML data output")

## HTML

Conversion of .out files into interactive HTML with block markup is available (see examples):


![html](image/README/html_preview.png "HTML output")

## Instalation

Git clone the repository and

```
pip install .
```
