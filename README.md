# XMLuvation - XML Evaluation Tool that searches for matches based on one or multiple XPath Expressions

![python-powered-w-200x80](https://github.com/user-attachments/assets/ff891665-6ac6-4fc3-a12d-39876708c8b3)![Logo_Full_Transparent_Cropped](https://github.com/zaricj/XMLuvation/assets/93329694/d9ea10b0-30e7-412e-b3ee-f2d75806e134)![xml_transparent_150x150](https://github.com/zaricj/XMLuvation/assets/93329694/7abe5b04-b8fc-41da-9e70-c3254067841c)![Geis Logo Transparent](https://github.com/zaricj/XMLuvation/assets/93329694/7fb55018-6ac4-4f31-adfa-35fd0e6b33af)

## Overview

XMLuvation is a Python application designed to parse and evaluate XML files. It provides a user-friendly interface for performing various operations such as reading XML files, filtering XML content based on XPath Expressions and look for matches in a single or multiple XML Files in a specified Folder and exporting the evaluation results to a CSV file.

## Features

- XML Parsing and Evaluation: XMLuvation allows users to read a XML file and view it's content.
- XPath Filtering: Users can filter and look for matches in XML content using XPath expressions, which can be added to a Listbox, where the added Filters are used for Evaluation.
- Export to CSV: Evaluation results can be exported to a CSV file for further analysis or processing, headers are created dynamically based on the added XPath Expression(s).
- Convert CSV to different filetypes: The CSV Evaluation result can be converted to different filetypes with the help of the Pandas module.
- Load CSV for display and filter content: Load the CSV file into a table view to display it's content and filter results based on the selected header.
- User Interface: The application features a simple and intuitive graphical user interface built using the ~PySimpleGUI~ FreeSimpleGUI library and an alternative GUI using the PySide6 library.

## Installation

To run XMLuvation, you need to have Python installed on your system. The required dependencies are as follows:

### Requirements

- Python 3.x

**3rd party and standard packages:**
| 3rd Part Packages | Standard Packages |
|-------------------|-------------------|
| FreeSimpleGUI | csv |
| lxml | os |
| pandas | re |
| tabulate | webrowser |
| openpyxl | |
| qt_material | |
| pyside6 | |

### Install the required dependencies via requirements.txt

`pip install -r requirements.txt`

## Main Usage Guide

1. Select Folder: Choose a folder containing XML files, the statusbar will show the total amount of found XML Files.
2. Read XML: Read an XML file from the selected folder to extract tag and attribute information into the Comboboxes.
3. Build XPath: Build XPath expressions based on selected tag and attribute values.
4. Add XPath Filter: Add XPath filters to match specific criteria in XML files.
5. Export as CSV: Export evaluation results, including matched XML files and corresponding XPath filters, as a CSV file.

## Additional Information

XPath Syntax Help: Access a quick reference guide to XPath syntax for building expressions.

## Support

If you encounter any issues or have any feedback, please feel free to open an issue on the GitHub repository.

## Credits

XMLuvation was created by me. It utilizes the FreeSimpleGUI and PySide6 library for building the graphical user interface, the lxml library for parsing XML files and Pandas for converting the CSV file.

## License

This project is licensed under the MIT License.

## Screenshot PySimpleGUI

##### Main View

![XMLuvation_P1](https://github.com/zaricj/XMLuvation/assets/93329694/093ec68b-066b-4fca-9718-acb59bcb7d84)

##### CSV Conversion View

![XMLuvation_P2](https://github.com/zaricj/XMLuvation/assets/93329694/aad72324-2d1a-4c04-bc29-f23e64635b75)

## Screenshot PySide6

##### Main View

![XMLuvation_Pyside6_P1](https://github.com/user-attachments/assets/32670ae0-5362-47e8-a8ea-3610d568642b)

##### CSV Conversion and Table Display View

![XMLuvation_Pyside6_P2](https://github.com/user-attachments/assets/fa476b98-80a3-48ff-9205-1d5f16b4d7b5)
