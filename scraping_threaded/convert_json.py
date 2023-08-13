import os
import json
from tqdm import tqdm  # Import the tqdm library

input_directory = './data/urls/'
output_directory = './data/urls_converted/'

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Iterate through all JSON files in the input directory
for input_file_name in os.listdir(input_directory):
    if input_file_name.endswith('.json'):
        input_file_path = os.path.join(input_directory, input_file_name)
        output_file_path = os.path.join(output_directory, input_file_name)

        # Initialize a list to store valid JSON objects
        valid_data = []

        # Read the input JSON file
        with open(input_file_path, 'r') as input_file:
            try:
                data = json.load(input_file).get("content")
                valid_data = data if isinstance(data, list) else []
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {input_file_name}: {e}")

        # Write each valid JSON object as a separate line in the output file
        with open(output_file_path, 'w') as output_file:
            # Initialize tqdm progress bar
            with tqdm(total=len(valid_data), desc=input_file_name) as pbar:
                for item in valid_data:
                    json.dump(item, output_file)
                    output_file.write('\n')  # Add a newline after each object
                    pbar.update(1)  # Update progress bar for each object
