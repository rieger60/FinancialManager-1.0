from data_importer import DataImport

def main():
    sample_csv = 'danske_bank.csv'

    data_importer = DataImport(sample_csv, 'Danske Bank')

    data_importer.load_data()

    if data_importer.data:
        for transaction in data_importer.data:
            print(transaction)
    else:
        print("No data was loaded. Please check the file path and the format")

if __name__ == "__main__":
    main()