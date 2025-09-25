import json

# Define the names for the input and output files
input_filename = 'reg1.json'
output_filename = 'regulation.json'

try:
    # Open and read the original JSON file
    with open(input_filename, 'r') as f:
        # Load the JSON content into a Python list
        data = json.load(f)

    # Loop through each item (dictionary) in the list
    for item in data:
        # --- Format the 'question' string ---
        # Split the question into number and text
        parts = item["question"].split(" ", 1)
        # Add a period and space after the number
        if len(parts) == 2:
            item["question"] = f"{parts[0]}. {parts[1]}"

        # --- Format the 'options' list ---
        formatted_options = []
        for option in item["options"]:
            # Split the option into letter and text
            option_parts = option.split(" ", 1)
            # Add a period and space after the letter
            if len(option_parts) == 2:
                formatted_options.append(f"{option_parts[0]}. {option_parts[1]}")
            else:
                formatted_options.append(option) # Keep as is if format is unexpected
        item["options"] = formatted_options


        # --- Format the 'answer' string ---
        # Split the answer into letter and text
        answer_parts = item["answer"].split(" ", 1)
        # Add a period and space after the letter
        if len(answer_parts) == 2:
            item["answer"] = f"{answer_parts[0]}. {answer_parts[1]}"


    # Open the new file in write mode to save the changes
    with open(output_filename, 'w') as f:
        # Write the modified Python list back to the new JSON file
        # 'indent=2' makes the file readable
        json.dump(data, f, indent=2)

    print(f"Success! The data has been reformatted and saved to '{output_filename}'")

except FileNotFoundError:
    print(f"Error: The file '{input_filename}' was not found. Please ensure it is in the same directory as the script.")
except Exception as e:
    print(f"An error occurred: {e}")