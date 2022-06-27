#Imports
from os import close
import sys
import getopt
import json
import datetime
from datetime import timedelta
from typing import List

from numpy import result_type

def init_procc(argv: list[str]):
    '''
        Function takes in an array of arguments passed in CLI and checks if everything is correct \n
        Return -> String containing file name
    '''

    input_file = ""
    global window_size
    help = """
        {0} ---- help menu ----
        -h | --help
        -i | --input_file <file_name>.json
        -w | --window_size <value>
    """.format(argv[0])
    
    try:
        opts, args = getopt.getopt(argv[1:], "hi:w:", ["help", "input_file=", "window_size="])
    except:
        print(help)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help)
            sys.exit(2)

        elif opt in ("-i", "--input_file"):
            input_file = arg

            # Check file extension 
            if not input_file.endswith(".json"):
                print("Wrong type of file! Please use a JSON file for input.")
                sys.exit(2)

        elif opt in ("-w", "--window_size"):
            window_size = arg

            # if value passed is 0, nothing to show
            if int(window_size) == 0:
                sys.exit(2)

    # Everything is correct, check if file opens
    return input_file
              

def file_verify(file: str):
    '''
        Function takes in a String that is the file name and verify if it opens correctly \n
        Return -> Dictionary containing the loaded JSON file
    '''

    try:
        f = open(file, "r")

    except ValueError as e:
        print("Invalid JSON file!")
        sys.exit(2)

    # File opens correctly, process JSON data
    jsonLoaded = json.load(f)
    f.close()

    return jsonLoaded

def process_data(data: list):
    '''
        Function to process the JSON data \n
        Return ->   dict : Dictionary containing all the timestamps in the file, inside display window size \n
                    str  : Current timestamp with seconds zeroed
    '''

    values = {} #DS to store the values

    # Get current time
    current_time = datetime.datetime.now()
    
    # Replace current timestamp seconds with 00
    current_time_zeroed = current_time.replace(second=0)
    
    # Get current delta of current timestamp
    current_delta = current_time_zeroed - timedelta(minutes=int(window_size))

    # Loop to check JSON data
    for i in reversed(data):

        # Get timestamp of current item and replace seconds with 00
        date_time_obj = datetime.datetime.strptime(i['timestamp'][:-7], '%Y-%m-%d %H:%M:%S')
        date_time_obj_zeroed = date_time_obj.replace(second=0)

        # Verify if it's inside specified delta
        if current_delta <= date_time_obj_zeroed:
            if str(date_time_obj_zeroed) in values:
                values[str(date_time_obj_zeroed)] += [i['duration']]
            else:
                values[str(date_time_obj_zeroed)] = [i['duration']]
        else:
            break

    # Data is arranged, calling this function will prepare the gathered data for output
    return values, str(current_time_zeroed)[:-7]   
    
def prepare_output(data: dict, timestamp: str):
    '''
        Function prepare the data for output \n
        Return -> Data structured for display
    '''

    outputList = []
    tmp = {}
    # Max timestamp in dictionary
    if data:
        maxTimestamp = list(data.keys())[0]
    else:
        print("List is empty!")
        sys.exit(2)

    # Treating the first item in the dictionary
    tmp["date"] = timestamp
    if maxTimestamp != timestamp:
        tmp["average_delivery_time"] = 0
    else:
        tmp["average_delivery_time"] = sum(data[timestamp]) / len(data[timestamp])

    outputList += [tmp]
    tmp = {}
    
    # Add all the minutes left to the DS, with the corresponding average value
    counter = int(window_size)
    while counter > 0:
        date_time_obj = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        current_delta = date_time_obj - timedelta(minutes=1)
        counter = counter - 1

        delta_str = str(current_delta)
            
        if not delta_str in list(data.keys()):
            tmp["date"] = delta_str
            tmp["average_delivery_time"] = 0
            outputList += [tmp]

        else:
            tmp["date"] = delta_str
            tmp["average_delivery_time"] = sum(data[delta_str]) / len(data[delta_str])
            outputList += [tmp]

        tmp = {}
        timestamp = str(current_delta)
            
    # Everything is ready to be printed
    return outputList

def output(data: list):
    '''
        Function will prepare the presentation and print data to terminal
    '''

    strData = str(data).replace('\'', '\"')
    jsonOutput = json.loads(strData)

    # Print all the data to the terminal
    for i in jsonOutput:
        print(i)

    # Create/Replace the JSON file in current directory
    try:
       jsonFile = open("jsonOutput.json", "w")
       jsonFile.write(strData)

    except ValueError as e:
        print("Error creating JSON file!")
        sys.exit(2)
    
    jsonFile.close()
        
if __name__ == "__main__":
    '''
        Main function - starts processing
    '''

    input_file = init_procc(sys.argv)

    jsonLoaded = file_verify(input_file)  

    values, timestamp = process_data(jsonLoaded)

    outputList = prepare_output(values, timestamp)  

    output(outputList)
