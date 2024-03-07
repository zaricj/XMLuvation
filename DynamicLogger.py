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
        log_values = []
        field_names = []
        placeholder_count = 0
        # Iterate over the parts
        for part in parts:
            # Check if the part starts with '!'
            if part.startswith('!'):
                # Add a prefix to the variable and append to log parts
                log_values.append(part[1:])
                print(log_values)
            else:
                # Add the part as a field name and append to field names
                field_names.append(part)
            if len(log_values) > len(field_names):
                placeholder_count += 1
                field_names.append(f"PlaceholderHeader{placeholder_count}")
        # Concatenate log parts with corresponding field names (assuming order matches)
        log_message = ' '.join([f"{field_name} {log_part}" for field_name, log_part in zip(field_names, log_values)])
        log_message_dict = {field_name: log_part for field_name, log_part in zip(field_names, log_values)}
        keysget = log_message_dict.keys()
        # Log the message
        window['-LOG-'].update(f"{log_message.strip()}\n", append=True)
        print(log_message)
        print("________")
        print(log_message_dict)
        print("keys")
        print(keysget)
        # Write field names and log message to CSV
        with open('output.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(field_names)
            writer.writerow(log_values)
    elif event == 'Clear':
        # Clear the logger
        window['-LOG-'].update('')
        window['-INPUT-'].update('')

# Close the window
window.close()
