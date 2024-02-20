import json

def sum_claim_amounts(file_path):
    try:
        # Open and read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Initialize total sum
        total_sum = 0

        # Iterate over each entry and add up the claim amounts
        for entry in data:
            claim_amount = entry.get("Claim Amount", "0").replace(',', '')
            total_sum += float(claim_amount)

        return total_sum

    except FileNotFoundError:
        print("File not found.")
        return 0
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

# Replace 'extracted_data.json' with the actual path of your JSON file
total_claim_amount = sum_claim_amounts('extracted_data.json')
print(f"Total Claim Amount: {total_claim_amount}")