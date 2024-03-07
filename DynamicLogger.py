import csv
import PySimpleGUI as sg
import re

# Define the layout
layout = [
    [sg.Text("Logger:")],
    [sg.Multiline(size=(50, 10), key='-LOG-', disabled=True, horizontal_scroll=True)],
    [sg.Text("Input Message and Variables (comma-separated):")],
    [sg.InputText(key='-INPUT-', enable_events=True)],
    [sg.Button('Log'), sg.Button('Clear'), sg.Button('Exit')]
]

# Create the window
window = sg.Window('Dynamic Logger with Variables', layout)

# CSV file path
csv_file_path = 'log.csv'

# Event loop
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    elif event == 'Log':
        # Get the input message and variables
        input_message_and_variables = values['-INPUT-']
        output_message = re.sub(r',\s*', ',', input_message_and_variables)
        parts = output_message.split(',')  # Split by comma
        # Initialize lists to store log message parts and field names
        log_parts = []
        field_names = []

        # Iterate over the parts
        for part in parts:
            # Check if the part starts with '!'
            if part.startswith('!'):
                # Add a prefix to the variable and append to log parts
                log_parts.append(f'Variable: {part}')
            else:
                # Add the part as a field name and append to field names
                field_names.append(part)

        # Concatenate the log message parts
        log_message = ' '.join(log_parts)
        # Log the message
        window['-LOG-'].update(f"{log_message.strip()}\n", append=True)
        print(log_message)
        # Write field names and log message to CSV
        with open('output.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(field_names)
            writer.writerow(log_parts)
    elif event == 'Clear':
        # Clear the logger
        window['-LOG-'].update('')
        window['-INPUT-'].update('')

# Close the window
window.close()
