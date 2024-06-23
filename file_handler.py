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

    def append_to_output_file(self, data):
        if os.path.exists(self.output_file) and os.path.getsize(self.output_file) > 0:
            try:
                existing_df = pd.read_csv(self.output_file)
                if existing_df.empty:
                    raise pd.errors.EmptyDataError("No columns to parse from file")
            except pd.errors.EmptyDataError as e:
                print(f"Error reading existing output file: {e}")
                existing_df = pd.DataFrame()
        else:
            existing_df = pd.DataFrame()

        if data:
            new_df = pd.DataFrame(data)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_csv(self.output_file, index=False)
        else:
            print("No data to append to output file")
