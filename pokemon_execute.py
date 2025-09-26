import json
import csv
import os
from pathlib import Path

def extract_pokemon_data(json_file_path):
    """
    Extract specific fields from Pokemon card JSON file
    Returns a list of dictionaries with extracted data
    """
    extracted_data = []
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        for card in data:
            # Only process Pokemon cards (skip Trainer and Energy cards)
            if card.get('supertype') == 'Pokémon':
                extracted_card = {
                    'id': card.get('id', ''),
                    'name': card.get('name', ''),
                    'subtypes': ', '.join(card.get('subtypes', [])) if card.get('subtypes') else '',
                    'level': card.get('level', ''),
                    'hp': card.get('hp', ''),
                    'types': ', '.join(card.get('types', [])) if card.get('types') else '',
                    'weaknesses': ', '.join([f"{w.get('type', '')}({w.get('value', '')})" 
                                           for w in card.get('weaknesses', [])]) if card.get('weaknesses') else ''
                }
                extracted_data.append(extracted_card)
                
    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file {json_file_path}")
    except Exception as e:
        print(f"Error processing {json_file_path}: {str(e)}")
    
    return extracted_data

def process_multiple_json_files(input_directory, output_file):
    """
    Process multiple JSON files and combine them into a single output
    """
    all_data = []
    input_path = Path(input_directory)
    
    # Find all JSON files in the directory
    json_files = list(input_path.glob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in {input_directory}")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    for json_file in json_files:
        print(f"Processing: {json_file.name}")
        data = extract_pokemon_data(json_file)
        all_data.extend(data)
    
    # Write to CSV file
    write_to_csv(all_data, output_file)
    
    # Write to SQL INSERT statements
    write_to_sql(all_data, output_file.replace('.csv', '.sql'))
    
    print(f"Extracted {len(all_data)} Pokemon cards")
    print(f"Data written to {output_file} and {output_file.replace('.csv', '.sql')}")

def write_to_csv(data, output_file):
    """
    Write extracted data to CSV file
    """
    if not data:
        print("No data to write")
        return
    
    fieldnames = ['id', 'name', 'subtypes', 'level', 'hp', 'types', 'weaknesses']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def write_to_sql(data, output_file):
    """
    Write extracted data as SQL INSERT statements
    """
    if not data:
        print("No data to write")
        return
    
    with open(output_file, 'w', encoding='utf-8') as sqlfile:
        # Create table statement
        sqlfile.write("""-- Pokemon Cards Table Creation
CREATE TABLE IF NOT EXISTS pokemon_cards (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    subtypes VARCHAR(100),
    level VARCHAR(10),
    hp VARCHAR(10),
    types VARCHAR(100),
    weaknesses VARCHAR(100)
);

-- Clear existing data (optional)
-- DELETE FROM pokemon_cards;

-- Insert statements
""")
        
        for card in data:
            # Escape single quotes in strings
            escaped_card = {}
            for key, value in card.items():
                if isinstance(value, str):
                    escaped_card[key] = value.replace("'", "''")
                else:
                    escaped_card[key] = value
            
            sql_statement = f"""INSERT INTO pokemon_cards (id, name, subtypes, level, hp, types, weaknesses) 
VALUES ('{escaped_card['id']}', '{escaped_card['name']}', '{escaped_card['subtypes']}', 
        '{escaped_card['level']}', '{escaped_card['hp']}', '{escaped_card['types']}', '{escaped_card['weaknesses']}');
"""
            sqlfile.write(sql_statement)

# Example usage functions
def process_single_file(json_file_path, output_csv="pokemon_data.csv"):
    """
    Process a single JSON file
    """
    data = extract_pokemon_data(json_file_path)
    write_to_csv(data, output_csv)
    write_to_sql(data, output_csv.replace('.csv', '.sql'))
    print(f"Processed {len(data)} Pokemon cards from {json_file_path}")

def main():
    """
    Main function - modify these paths according to your setup
    """
    # Option 1: Process a single file
    # process_single_file('base1.json', 'pokemon_data.csv')
    
    # Option 2: Process multiple files from a directory
    input_directory = '.'  # Current directory - change this to your JSON files directory
    output_file = 'all_pokemon_data.csv'
    process_multiple_json_files(input_directory, output_file)

if __name__ == "__main__":
    main()
