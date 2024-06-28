# XMLuvation - XML Parsing and Evaluation Tool for Matching XPath Expressions
![Logo_Full_Transparent_Cropped](https://github.com/zaricj/XMLuvation/assets/93329694/d9ea10b0-30e7-412e-b3ee-f2d75806e134)![xml_transparent_150x150](https://github.com/zaricj/XMLuvation/assets/93329694/7abe5b04-b8fc-41da-9e70-c3254067841c)![Geis Logo Transparent](https://github.com/zaricj/XMLuvation/assets/93329694/7fb55018-6ac4-4f31-adfa-35fd0e6b33af)

## Overview
XMLuvation is a Python application designed to parse and evaluate XML files. It provides a user-friendly interface for performing various operations such as reading XML files, filtering XML content based on XPath Expressions and look for matches in a single or multiple XML Files in a specified Folder, exporting the evaluation results to a CSV file.

## Features

* XML Parsing and Evaluation: XMLuvation allows users to read a XML file and view it's content.
* XPath Filtering: Users can filter and look for matches in XML content using XPath expressions, which can be added to a Listbox, where the added Filters are used for Evaluation.
* Export to CSV: Evaluation results can be exported to a CSV file for further analysis or processing.
* User Interface: The application features a simple and intuitive graphical user interface built using the PySimpleGUI library.

## Installation
To run XMLuvation, you need to have Python installed on your system. The required dependencies are as follows:

### Requirements

- Python 3.x
- PySimpleGUI library (install using pip install PySimpleGUI)
- lxml library (install using pip install lxml)
- pandas library (install using pip install pandas)
- tabulate library (install using pip install tabulate)
- openpyxl library (install using pip install openpyxl)
- csv library (included in the standard Python library)
- os library (included in the standard Python library)
- re library (included in the standard Python library)
- webbrowser library (included in the standard Python library)

## Usage Guide

1. Select Folder: Choose a folder containing XML files.
2. Read XML: Read an XML file from the selected folder to extract tag and attribute information.
3. Build XPath: Build XPath expressions based on selected tag and attribute values.
4. Add XPath Filter: Add XPath filters to match specific criteria in XML files.
5. Export as CSV: Export evaluation results, including matched XML files and corresponding XPath filters, as CSV files..

## Additional Information
XPath Syntax Help: Access a quick reference guide to XPath syntax for building expressions.

## Support
If you encounter any issues or have any feedback, please feel free to open an issue on the GitHub repository.

## Credits
XMLuvation was created by me. It utilizes the PySimpleGUI library for building the graphical user interface and the lxml library for parsing XML files.

## License
This project is licensed under the MIT License.

## Screenshot
##### Main View
![image](https://github.com/zaricj/XMLuvation/assets/93329694/ab775ec5-e1df-4a25-93ac-c3fe41d35ee6)

##### CSV Conversion View
![image](https://github.com/zaricj/XMLuvation/assets/93329694/876daa4b-d480-4601-a56b-23fcc553009e)


