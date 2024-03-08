import csv

def dic_creator():
    key = ["FirstName","LastName","ID"] 
    value = ["Joe","Rogan","224"]

    log_message = ' '.join([f"{field_name}: {log_part}" for field_name, log_part in zip(key, value)])
    log_message_dict = {field_name: log_part for field_name, log_part in zip(key, value)}

    return log_message_dict

func_return = dic_creator()

with open('output.csv', 'w', newline='') as csvfile:
    keys = func_return.keys()
    values = func_return.items()
    dic_writer = csv.DictWriter(csvfile, fieldnames=keys)
    dic_writer.writeheader()
    dic_writer.writerow(func_return)

print(func_return)

# Profilename:, !//datawizardprofile[@name]/@name, has value, !//filter[@id='127']/@description, if field, !//field[@id='127']/@description
# Message, !//filter[@id], Text, !//filter
# Field,!//field[@name]/@name