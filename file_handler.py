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
            print(f"Output file created at {self.output_file} with {len(df)} rows.")
        else:
            print("No data to write to output file")

    def append_to_output_file(self, data):
        if os.path.exists(self.output_file) and os.path.getsize(self.output_file) > 0:
            try:
                existing_df = pd.read_csv(self.output_file)
                if existing_df.empty:
                    print("Existing output file is empty.")
                    raise pd.errors.EmptyDataError("No columns to parse from file")
            except pd.errors.EmptyDataError as e:
                print(f"Error reading existing output file: {e}")
                existing_df = pd.DataFrame()
        else:
            existing_df = pd.DataFrame()

        if data:
            new_df = pd.DataFrame(data)
            new_df = self.filter_new_data(existing_df, new_df)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_csv(self.output_file, index=False)
            print(f"Appended {len(new_df)} rows to the output file. Total rows now: {len(combined_df)}")
        else:
            print("No data to append to output file")

    def filter_new_data(self, existing_df, new_df):
        if 'UniqueID' in existing_df.columns:
            existing_hashes = set(existing_df['UniqueID'])
            new_df = new_df[~new_df['UniqueID'].isin(existing_hashes)]
            print(f"Filtered data to {len(new_df)} new rows.")
        else:
            print("No 'UniqueID' column found in existing data.")
        return new_df
