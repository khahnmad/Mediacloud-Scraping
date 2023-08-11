import json
from tqdm import tqdm  # Import the tqdm librar

input_file_path = 'example_data.json'
output_file_path = 'articles.json'

# Read the input JSON file
with open(input_file_path, 'r') as input_file:
    data = json.load(input_file).get("content")

# Write each JSON object as a separate line in the output file
with open(output_file_path, 'w') as output_file:
    with tqdm(total=len(data)) as pbar:  # Initialize tqdm progress bar
        for item in data:
            json.dump(item, output_file)
            output_file.write('\n')  # Add a newline after each object
            pbar.update(1)  # Update progress bar for each object
