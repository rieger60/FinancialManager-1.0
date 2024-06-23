import json
import os
import pandas as pd

class CategoryUpdater:
    def __init__(self, output_file='output.csv', uncategorized_file='uncategorized.txt', categorization_rules_file='categorization_rules.json'):
        self.output_file = output_file
        self.uncategorized_file = uncategorized_file
        self.categorization_rules_file = categorization_rules_file
        self.categorization_rules = self.load_categorization_rules()

    def load_categorization_rules(self):
        with open(self.categorization_rules_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def load_uncategorized(self):
        if not os.path.exists(self.uncategorized_file):
            return []

        with open(self.uncategorized_file, 'r', encoding='utf-8') as file:
            return [eval(line.strip()) for line in file]

    def categorize_description(self, description):
        description_lower = description.lower()
        for rule in self.categorization_rules:
            if rule.get('Keyword').lower() in description_lower:
                return rule.get('Main Category'), rule.get('Sub Category')
        return None, None

    def update_output_file(self):
        uncategorized_rows = self.load_uncategorized()
        if not uncategorized_rows:
            return

        df = pd.read_csv(self.output_file)
        updated_uncategorized = []

        for row in uncategorized_rows:
            unique_id = row['UniqueID']
            description = row.get('Description')

            if description:
                main_category, sub_category = self.categorize_description(description)
                if main_category and sub_category:
                    df.loc[df['UniqueID'] == unique_id, 'Main Category'] = main_category
                    df.loc[df['UniqueID'] == unique_id, 'Sub Category'] = sub_category
                    df.loc[df['UniqueID'] == unique_id, 'Description'] = description
                else:
                    updated_uncategorized.append(row)
            else:
                updated_uncategorized.append(row)

        df.to_csv(self.output_file, index=False)

        with open(self.uncategorized_file, 'w', encoding='utf-8') as file:
            for row in updated_uncategorized:
                file.write(str(row) + '\n')

if __name__ == "__main__":
    updater = CategoryUpdater()
    updater.update_output_file()
