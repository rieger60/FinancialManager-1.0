import json

class Categorizer:
    def __init__(self, rules_file='categorization_rules.json'):
        with open(rules_file, 'r', encoding='utf-8') as file:
            self.rules = json.load(file)

    def categorize(self, data):
        uncategorized_rows = []
        for row in data:
            description = row.get('Description', '')
            categorized = False
            for rule in self.rules:
                if rule['Keyword'].lower() in description.lower():
                    row['Main Category'] = rule['Main Category']
                    row['Sub Category'] = rule['Sub Category']
                    categorized = True
                    break
            
            if not categorized:
                uncategorized_rows.append(row)
                row['Main Category'] = 'Uncategorized'
                row['Sub Category'] = 'Uncategorized'
        
        if uncategorized_rows:
            self.save_uncategorized(uncategorized_rows)
        
        return data

    def save_uncategorized(self, rows):
        with open('uncategorized.txt', 'w', encoding='utf-8') as file:
            for row in rows:
                file.write(f"{row}\n")
