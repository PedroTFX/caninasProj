import pandas as pd

def find_duplicate_sample_ids(file_path: str, sample_id_column: str = 'Sample ID'):
    # Try multiple encodings to handle non-UTF-8 encoded files
    encodings_to_try = ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252', 'utf-16', 'utf-32']
    last_err = None
    
    for enc in encodings_to_try:
        try:
            # Try reading the file with the current encoding and the correct delimiter (semicolon)
            print(f"Attempting to read with encoding: {enc}")
            df = pd.read_csv(file_path, encoding=enc, delimiter=';', on_bad_lines='skip')  # Correct delimiter for semicolon-separated file
            print(f"File successfully read with encoding: {enc}")
            break
        except UnicodeDecodeError as e:
            last_err = e
            print(f"Error reading file with encoding {enc}: {e}")
            continue
        except pd.errors.ParserError as e:
            print(f"Error parsing file with encoding {enc}: {e}")
            continue
    else:
        raise SystemExit(f"Unable to read the file with available encodings. Last error: {last_err}")
    
    # Normalize column names (strip leading/trailing spaces, convert to lower case)
    df.columns = df.columns.str.strip().str.lower()  # Normalize column names to lowercase and strip spaces
    
    # Print out normalized column names to see if 'sample id' exists
    print("Normalized column names:")
    print(df.columns)

    # Ensure the Sample ID column exists
    sample_id_column = sample_id_column.lower().strip()  # Normalize the column name to lowercase and strip spaces
    if sample_id_column not in df.columns:
        print(f"Error: '{sample_id_column}' column not found.")
        print(f"Available columns: {df.columns}")
        return
    
    # Find duplicate sample IDs
    duplicate_sample_ids = df[df.duplicated(subset=[sample_id_column], keep=False)][sample_id_column]
    
    # Check if there are any duplicates
    if duplicate_sample_ids.empty:
        print("No duplicate Sample IDs found.")
    else:
        # Output duplicate Sample IDs
        print("Found the following duplicate Sample IDs:")
        print(duplicate_sample_ids.unique())
        
        # Optionally, save these duplicate Sample IDs to a file
        duplicate_sample_ids.to_csv("duplicate_sample_ids.csv", index=False, header=True)
        print(f"Duplicate Sample IDs saved to 'duplicate_sample_ids.csv'.")

# Usage example:
file_path = "CBSS.updated_xlsx 2.csv"  # Replace this with the path to your CSV file
find_duplicate_sample_ids(file_path)
