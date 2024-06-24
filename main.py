from data_importer import DataImport
from duplicate_checker import DuplicateChecker
from file_handler import FileHandler
from categorizer import Categorizer
from utility_functions import UtilityFunction

def main():
    output_file = 'output.csv'
    sample_csv = 'TestCases/L¦nkonto-3643468492-20240616.csv'
    bank = 'Danske Bank'
    rules_file = 'categorization_rules.json'

    #check if output file exists
    check_existing_output = UtilityFunction(output_file)
    check_existing_output.create_output_file_if_not_exists()

    data_importer = DataImport(sample_csv, bank)
    data_importer.load_data()
    duplicate_checker = DuplicateChecker(data_importer.data, output_file)
    duplicate_checker.remove_duplicates()
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
