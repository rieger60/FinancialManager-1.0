from data_importer import DataImport
from file_handler import FileHandler

def main():
    output_file = 'output.csv'
    sample_csv = 'TestCases/L¦nkonto-3643468492-20240616.csv'
    bank = 'Danske Bank'

    data_importer = DataImport(sample_csv, bank)
    data_importer.load_data()

    # Debugging statement to check loaded data
    if data_importer.data:
        print(f"Loaded data for {bank} from {sample_csv}:")
        for i, entry in enumerate(data_importer.data):
            print(entry)
            if i >= 4:  # Limit to first 5 entries for readability
                break
    else:
        print(f"No data loaded for {bank} from {sample_csv}")

    file_handler = FileHandler(output_file)

    if file_handler.check_output_file_exists():
        print("Appending to existing output file")
        file_handler.append_to_output_file(data_importer.data)
    else:
        print("Creating new output file")
        file_handler.create_output_file(data_importer.data)

if __name__ == "__main__":
    main()
