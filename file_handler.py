import os
import pandas as pd

class FileHandler:
    def __init__(self, output_file):
        self.output_file = output_file

    def check_output_file_exists(self):
        return os.path.exists(self.output_file)

    def create_output_file(self, data):
        if data:
            df = pd.DataFrame(data)
            df.to_csv(self.output_file, index=False)
        else:
            print("No data to write to output file")

    def validate_csv(self):
        try:
            df = pd.read_csv(self.output_file, sep = ";")
            return df
        except pd.errors.EmptyDataError as e:
            print(f"Error reading existing output file: {e}")
            return pd.DataFrame()
        except pd.errors.ParserError as e:
            print(f"Error parsing existing output file: {e}")
            with open(self.output_file, 'r') as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if len(line.split(',')) != 10:  # Expecting 10 columns per row
                        print(f"Invalid line {i+1}: {line.strip()}")
            return pd.read_csv(self.output_file, on_bad_lines='skip', sep = ";")

    def append_to_output_file(self, data):
        if self.check_output_file_exists():
            existing_df = self.validate_csv()
        else:
            print("existing not found")
            existing_df = pd.DataFrame()

        if data:
            new_df = pd.DataFrame(data)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_csv(self.output_file, index=False, sep=';')
        else:
            print("No data to append to output file")
