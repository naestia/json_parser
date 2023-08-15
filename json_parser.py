import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from random import randint


file_name = "data.json"
data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)


def produce_json():
    """
    This function is primarily used as a main function to produce example JSON data
    to later be used when comparing timestamps.
    """
    output = {}
    output_list = []
    # Loop that generates 5 JSON objects to a list of dictionaries
    for index in range(5):
        timestamp = generate_timestamp()
        current_date = datetime.strptime(timestamp, "%y-%m-%dT%H:%M:%SZ")
        message = generate_message(current_date)
        example_dict = {"timestamp": timestamp, "message": message}
        output_list.append(example_dict)
    
    output["output"] = output_list
    write_json(output)


def write_json(output):
    """
    This function writes the example output to the chosen JSON file.
    It will create 'data.json' in the same.
    """
    json_object = json.dumps(output, indent=2)
    if not os.path.exists(data_file):
        Path(data_file).touch()
    else:
        answer = input(f"'{file_name}' already exists on disk. Would you like to replce '{file_name}'? (Y/n) >> ")
        if not answer.upper() == "Y":
            print(f"Not writing over current '{file_name}'...")
            return 0
    
    with open(data_file, "w") as file:
        file.write(json_object)


def generate_timestamp(current_date=None):
    """
    This function ranzomises a date between 2023-01-05 to 2023-01-10.
    This will later become the 'timestamp' in the json object.
    Uses timestamp format: "%y-%m-%dT%H:%M:%SZ".
    """
    if not current_date:
        current_date = datetime.strptime("23-01-05T09:00:00Z", "%y-%m-%dT%H:%M:%SZ")

    start_date, end_date = datetime(2023, 1, current_date.day), datetime(2023, 1, current_date.day + 4)
    number_of_days = (end_date - start_date).days
    new_date = randint(0, number_of_days)
    if new_date == 0:
        hour, minute, second = randint(current_date.hour, 12), randint((current_date.minute + 1), 59), randint((current_date.second + 1), 59)
    else:
        hour, minute, second = randint(6, 12), randint(0, 59), randint(0, 59)
    random_date = start_date + timedelta(days=new_date, hours=hour, seconds=second, minutes=minute)
    timestamp = datetime.strftime(random_date ,"%y-%m-%dT%H:%M:%SZ")
    return timestamp


def generate_message(current_date):
    """
    This function creates the 'message' object in the example JSON output.
    """
    rid_number = 16675
    version = 25.0
    idt_object = {}
    for item in range(5):
        dp_object = {"rid": f"{rid_number};PT=0", "v": round(version, 1), "ts": generate_timestamp(current_date)}
        idt_object[f"IDT_0{item + 1}"] = dp_object
        rid_number += 1
        version += 0.7

    message_object = {
            "level": "info",
            "s": "wideco/svinbound",
            "m": "ImportDataPointReport",
            "pn": "wideco",
            "lid": "Lejonfastigheter Djurgardsgatan 17",
            "pst": "provisioned",
            "body": {
                "c": 5,
                "dp": idt_object
            }
        }
    return message_object


def time_compare(dictionary_object):
    """
    This is the main function for looping through the JSON array, 
    extracting the 'timestamp' as well as the 'ts' and then comparing.
    """
    try:
        for index, object in enumerate(dictionary_object["output"]):
            current_timestamp = datetime.strptime(object["timestamp"], "%y-%m-%dT%H:%M:%SZ")
            # print(f"Current timestamp: {current_timestamp}")
            message = object["message"]
            body = message.get("body")
            if not body:
                key_error("body")
                return 1

            dp = body.get("dp")
            if not dp:
                key_error("dp")
                return 1

            idt_list = [idt for idt in dp]
            less_than_hour = False
            for idt in idt_list:
                idt_object = dp.get(idt)
                if not idt_object:
                    key_error("dp")
                    return 1

                idt_timestamp = datetime.strptime(idt_object["ts"], "%y-%m-%dT%H:%M:%SZ")
                time_diff = idt_timestamp - current_timestamp
                if time_diff.days == 0:
                    if time_diff.total_seconds() / 60 < 60:
                        less_than_hour = True
                
                if not less_than_hour:
                    print(f"Object: {index + 1} Current IDT: {idt} Start time: {current_timestamp} | End time: {idt_timestamp} | Time difference: {time_diff} Hours")

    except KeyError as er:
        key_error(er)
    except ValueError as err:
        print(f"ERROR: There might be an error with one or more values while parsing.. Possible error for value: {err}")


def key_error(error):
    print(f"ERROR: There might be an error where one or more keys does not exist.. Possible error for key: {error}")


def read_json():
    """
    This function reads the JSON file and returns the 
    JSON data as a dictionary for python to parse.
    """
    try:
        with open(data_file, "r") as file:
            data = file.read()

        json_data = json.loads(data)
        json_object = dict(json_data)
        return json_object
    except FileNotFoundError:
        print(f"'{file_name}' not found.")


if __name__ == "__main__":
    produce_json()
    dictionary_object = read_json()
    time_compare(dictionary_object)
