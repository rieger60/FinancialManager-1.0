import pandas as pd
import os

class DuplicateChecker:
    def __init__(self, new_transactions_df, existing_data_file):
        self.new_data = new_transactions_df
        if os.path.exists(existing_data_file):
            self.existing_data = pd.read_csv(existing_data_file, sep=';')
        else:
            print(f"Warning: {existing_data_file} does not exist. Proceeding without existing data.")
            self.existing_data = pd.DataFrame(columns=new_transactions_df.columns)

    def remove_duplicates(self):
        print(f"Type of self.new_data: {type(self.new_data)}")
        if isinstance(self.new_data, pd.DataFrame):
            existing_ids = set(self.existing_data['UniqueID'])
            self.new_data = self.new_data[~self.new_data['UniqueID'].isin(existing_ids)]
        else:
            raise TypeError("self.new_data must be a pandas DataFrame")