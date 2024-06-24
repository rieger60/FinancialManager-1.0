import os
import pandas as pd

class UtilityFunction:
    required_columns = ['Date', 'Description', 'Amount', 'Amount_currency', 
                        'Currency', 'Currency_Rate', 'Bank', 'UniqueID']

    def __init__(self, file_path):
        self.file_path = file_path

    def create_output_file_if_not_exists(self):
        if not os.path.exists(self.file_path):
            df = pd.DataFrame(columns=self.required_columns)
            df.to_csv(self.file_path, index=False, sep=";")
