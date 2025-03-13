from api.ragsystem.documents.csv.csv_processor import CSVProcessor

csv_path = './rag-data/rice/disease/tasks.csv'

csvExtractor = CSVProcessor(None)
results = csvExtractor.extract_content('tasks.csv')
for result in results:
    print(result)
    print("\n\n\n")