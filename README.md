# XMLuvation

## Overview
XMLuvation is a Python application designed to parse and evaluate XML files. It provides a user-friendly interface for performing various operations such as reading XML files, filtering XML content based on specific criteria, and exporting the evaluation results to a CSV file.

## Features

* XML Parsing and Evaluation: XMLuvation allows users to read XML files, view their content, and evaluate them based on XPath expressions.
* XPath Filtering: Users can filter XML content using XPath expressions to extract specific elements or attributes.
* Export to CSV: Evaluation results can be exported to a CSV file for further analysis or processing.
* User Interface: The application features a simple and intuitive graphical user interface built using the PySimpleGUI library.

## Installation
To run XMLuvation, you need to have Python installed on your system. You can install the required dependencies using the following command:

```
pip install PySimpleGUI
pip install lxml
```

Usage:

* Run the Application: Launch the XMLuvation application by executing the Python script xmluvation.py.
* Read XML Files: Click on the "Browse Folder" button to select a folder containing XML files. The application will display the XML content in the output window.
* Filter XML Content: Use the dropdown menus to select tag names, tag values, attribute names, and attribute values for filtering the XML content. You can also build XPath expressions manually using theprovided * input field.
* Add Filters: Click on the "Add to Matching" button to add XPath filters for matching elements and the "Add to Logging" button to add XPath filters for logging purposes.
* Export Evaluation: Specify the output path for the CSV file by clicking on the "Save as" button. Then, click on the "Export" button to export the evaluation results to a CSV file.

## Theme Customization
XMLuvation allows users to customize the theme of the application interface. You can modify the theme settings by editing the my_new_theme dictionary in the Python script.

## Support
If you encounter any issues or have any feedback, please feel free to open an issue on the GitHub repository.

## Credits
XMLuvation was created by me. It utilizes the PySimpleGUI library for building the graphical user interface and the lxml library for parsing XML files.

## License
This project is licensed under the MIT License.

## Screenshot
![python_GFoOkSV6wT](https://github.com/zaricj/XMLuvation/assets/93329694/ad79cfcd-ff6e-433d-8db9-592a2f7baae3)
