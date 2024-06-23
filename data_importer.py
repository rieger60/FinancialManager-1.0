from currency_converter import CurrencyConverter, ECB_URL
from datetime import date, datetime
import hashlib
import logging
import pandas as pd
import tabula

class UtilityFunctions:
	def __init__(self, currency_converter):
		self.currency_converter = currency_converter

	def _convert_currency(self, amount, base_currency, target_currency, specified_date):
		try:
			extract_date = datetime.strptime(specified_date, '%d-%m-%Y').date()
			converted_amount = self.currency_converter.convert(amount, base_currency, target_currency, extract_date)
			return round(converted_amount, 2)
		except Exception as e:
			logging.error(f"Error converting currency: {str(e)}")
		return None # Return None if an exception occured

	def get_currency_rate(self, row):
		base_currency = row['Currency']
		target_currency = "DKK"
		return self._convert_currency(1.00, base_currency, target_currency, row['Date'])

	def calculate_target_currency_rate(self, row):
		specified_date = row['Date']
		base_currency = row['Currency']
		target_currency = "DKK"
		amount = row['Amount_currency']
		return self._convert_currency(amount, base_currency, target_currency, specified_date)

class DataImport:
	def __init__(self, file_path, bank, currency_converter=None):
		self.file_path = file_path
		self.bank = bank
		self.data = None
		self.currency_converter = currency_converter or CurrencyConverter(ECB_URL, 
															fallback_on_wrong_date=True, 
															fallback_on_missing_rate=True)
		self.load_methods = {
			'Danske Bank': self.load_DanskeBank,
			'Wise': self.load_Wise,
			'Norwegian': self.load_Norwegian,
			'Forbrugsforeningen': self.load_Forbrugsforeningen,
			'Lunar': self.load_Lunar
		}

	def load_data(self):
		if self.bank not in self.load_methods:
			raise ValueError(f"No data load method for bank: {self.bank}")

		load_method = self.load_methods[self.bank]
		load_method()

	def _common_preprocessing(self, df):
		df['UniqueID'] = df.apply(lambda row: 
			hashlib.md5(f"{row['Date']}_{row['Description']}_{row['Amount']}_{row['UniqueCol']}".encode()).hexdigest(), 
			axis=1
			)

	def load_Lunar(self):
		dtype_map = {
			'Dato': 'Date',
			'Tekst': 'Description',
			'Beløb': 'Amount',
			'Tid': 'UniqueCol'
		}

		df = pd.read_csv(
			self.file_path,
			delimiter=',',
			encoding='utf-8',
			usecols=list(dtype_map.keys())
		)

		df = df.rename(columns=dtype_map)

		df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d').dt.strftime('%d-%m-%Y')
		df['Amount'] = (
			df['Amount'].str.replace('.', '', regex=False)
			.str.replace(',', '.', regex=False)
			.astype(float)
		)

		df['Bank'] = 'Lunar'
		df['Amount_currency'] = df['Amount']
		df['Currency'] = 'DKK'
		df['Currency_Rate'] = 1

		self._common_preprocessing(df)

		selected_columns = [
			'Date', 'Description', 'Amount', 'Amount_currency', 
			'Currency', 'Currency_Rate', 'Bank', 'UniqueID'
		]
		self.data = df[selected_columns].to_dict(orient='records')

	def load_DanskeBank(self):
		dtype_map = {
			'Dato': 'Date',
			'Tekst': 'Description',
			'Beløb': 'Amount',
			'Saldo': 'UniqueCol',
			'Status': 'Status'
		}

		df = pd.read_csv(
			self.file_path,
			delimiter=';',
			encoding='ISO-8859-1',
			usecols=list(dtype_map.keys())
		)

		df = df[df['Status'] != 'Slettet']
		df = df[df['Status'] != 'Venter']

		df = df.rename(columns=dtype_map)

		df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y').dt.strftime('%d-%m-%Y')
		df['Amount'] = (
			df['Amount'].str.replace('.', '', regex=False)
			.str.replace(',', '.', regex=False)
			.astype(float)
		)
		
		df['Bank'] = 'Danske Bank'
		df['Amount_currency'] = df['Amount']
		df['Currency'] = 'DKK'
		df['Currency_Rate'] = 1

		self._common_preprocessing(df)

		selected_columns = [
			'Date', 'Description', 'Amount', 'Amount_currency', 
			'Currency', 'Currency_Rate', 'Bank', 'UniqueID'
		]
		self.data = df[selected_columns].to_dict(orient='records')


	def load_Wise(self):
		df = pd.read_csv(self.file_path, 
						 delimiter=',', 
						 encoding='utf-8')
		valid_rows = (df['Status'] != 'CANCELLED') & \
					 (df['Target amount (after fees)'] != 0) & \
					 (df['Source amount (after fees)'] != 0)
		df = df[valid_rows]

		df['Date'] = pd.to_datetime(df['Finished on'], 
									format='%Y-%m-%d %H:%M:%S').dt.strftime('%d-%m-%Y')
		
		df['Description'] = df.apply(
			lambda row: row['Source name'] if row['Direction'] == 'IN' else (
				row['Target name'] if row['Direction'] == 'OUT' else 'Internal transfer'),
				axis=1)
		df['Amount_currency'] = df.apply(
			lambda row: row['Source amount (after fees)'] if row['Direction'] == 'IN' else (
			row['Target amount (after fees)'] * -1 if row['Direction'] == 'OUT' else 0), 
			axis=1)
		df['Currency'] = df.apply(
			lambda row: row['Source currency'] if row['Direction'] == 'IN' else (
			row['Target currency'] if row['Direction'] == 'OUT' else row['Target currency']), 
			axis=1)

		# Create bank identifier
		df['Bank'] = 'Wise'

		#Create UniqueCol
		df['UniqueCol'] = df['ID']
 
		#create DKK_rate
		utility_functions_instance = UtilityFunctions(self.currency_converter)
		df['Amount'] = df.apply(utility_functions_instance.calculate_target_currency_rate, axis=1)
		df['Currency_Rate'] = df.apply(utility_functions_instance.get_currency_rate, axis=1)

		self._common_preprocessing(df)
		
		selected_columns = ['Date', 'Description', 'Amount', 'Amount_currency', 
							'Currency', 'Currency_Rate', 'Bank', 'UniqueID']
		self.data = df[selected_columns].to_dict(orient='records')

	def load_Norwegian(self):
		columns_to_read = {
			'TransactionDate': 'Date',
			'Text': 'Description',
			'Amount': 'Amount',
			'Type': 'Type',
			'Currency Amount': 'Amount_currency',
			'Currency': 'Currency',
			'Currency Rate': 'Currency_Rate'
		}
		df = pd.read_excel(self.file_path, usecols=list(columns_to_read.keys()))
		df = df.rename(columns=columns_to_read)

		df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%d-%m-%Y')
		if df['Date'].isnull().any():
			logging.warning(f"Some dates in {self.file_path} could not be parsed.")

		#Create UniqueCol
		df['UniqueCol'] = df['Type']
		self._common_preprocessing(df)
		df['Bank'] = 'Norwegian'
		
		df = df[df['Type'] != "Reserveret"]
		selected_columns = ['Date', 'Description', 'Amount', 'Amount_currency', 
							'Currency', 'Currency_Rate', 'UniqueID', 'Bank']	
		self.data = df[selected_columns].to_dict(orient='records')

	def load_Forbrugsforeningen(self):
		pdf_file = self.file_path
		pdf_dfs = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True, encoding='utf-8')
		concatenated_dfs = []

		for single_df in pdf_dfs:
			if {'Dato', 'Posteringstekst', 'Beløb', 'Valuta', 'Saldo'}.issubset(single_df.columns):
				renamed_df = single_df.rename(columns={
					'Dato': 'Date',
					'Posteringstekst': 'Description',
					'Beløb': 'Amount',
					'Valuta': 'Currency',
					'Saldo': 'UniqueCol'
				})
				concatenated_dfs.append(renamed_df)

		if not concatenated_dfs:
			logging.warning(f"No data was extracted from {pdf_file}")
			return pd.DataFrame()

		df = pd.concat(concatenated_dfs, ignore_index=True)
		df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y').dt.strftime('%d-%m-%Y')
		df['Amount'] = df['Amount'].str.replace('.', '').str.replace(',', '.', regex=False).astype(float)
		self._common_preprocessing(df)
		df['Bank'] = 'Forbrugsforeningen'
		df['Amount_currency'] = df['Amount']
		df['Currency_Rate'] = 1
		
		selected_columns = ['Date', 'Description', 'Amount', 'Amount_currency', 
							'Currency', 'Currency_Rate', 'Bank', 'UniqueID']

		self.data = df[selected_columns].to_dict(orient='records')