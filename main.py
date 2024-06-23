from data_importer import DataImport
from file_handler import FileHandler
from categorizer import Categorizer

def main():
    output_file = 'output.csv'
    sample_csv = 'TestCases/L¦nkonto-3643468492-20240616.csv'
    bank = 'Danske Bank'
    rules_file = 'categorization_rules.json'

    data_importer = DataImport(sample_csv, bank)
    data_importer.load_data()
    file_handler = FileHandler(output_file)

    if not data_importer.data:
        print("No data imported.")
        return

    categorizer = Categorizer(rules_file)
    categorized_data = categorizer.categorize(data_importer.data)

    if file_handler.check_output_file_exists():
        file_handler.append_to_output_file(categorized_data)
    else:
        file_handler.create_output_file(categorized_data)

if __name__ == "__main__":
    main()
