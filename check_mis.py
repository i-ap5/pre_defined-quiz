import json
import re

# Define the names for the input and output files
input_filename = 'regulation.json'
output_filename = 'formatted_data.json'

try:
    # --- 1. READ THE FILE ---
    with open(input_filename, 'r') as f:
        data = json.load(f)

    # --- 2. CHECK FOR MISSING QUESTION NUMBERS ---
    existing_numbers = set()
    for item in data:
        # Use regex to find the first number in the question string
        match = re.match(r'^\d+', item['question'])
        if match:
            # Add the found number (as an integer) to our set
            existing_numbers.add(int(match.group(0)))

    if existing_numbers:
        # Determine the full range of questions we should have
        min_num = min(existing_numbers)
        max_num = max(existing_numbers)
        full_set = set(range(min_num, max_num + 1))

        # Find the difference between the full set and the numbers we have
        missing_numbers = sorted(list(full_set - existing_numbers))

        if missing_numbers:
            print(f"Found missing question numbers: {missing_numbers}")
        else:
            print("No missing question numbers found in the sequence.")
    else:
        print("Could not find any question numbers to check.")


    # --- 3. REFORMAT THE JSON DATA (As requested before) ---
    for item in data:
        # Format the 'question' string
        parts = item["question"].split(" ", 1)
        if len(parts) == 2 and parts[0].isdigit():
            item["question"] = f"{parts[0]}. {parts[1]}"

        # Format the 'options' list
        formatted_options = []
        for option in item["options"]:
            option_parts = option.split(" ", 1)
            if len(option_parts) == 2:
                formatted_options.append(f"{option_parts[0]}. {option_parts[1]}")
            else:
                formatted_options.append(option)
        item["options"] = formatted_options

        # Format the 'answer' string
        answer_parts = item["answer"].split(" ", 1)
        if len(answer_parts) == 2:
            item["answer"] = f"{answer_parts[0]}. {answer_parts[1]}"

    # --- 4. WRITE THE REFORMATTED DATA TO A NEW FILE ---
    with open(output_filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Success! The data has also been reformatted and saved to '{output_filename}'")

except FileNotFoundError:
    print(f"Error: The file '{input_filename}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")