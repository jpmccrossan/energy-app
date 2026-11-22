# api/management/commands/import_energy_data.py

from django.core.management.base import BaseCommand
from api.etl import process_energy_csv

class Command(BaseCommand):
    help = 'Imports data from the energy_data.csv file'

    def handle(self, *args, **kwargs):
        file_path = 'energy_data.csv'
        self.stdout.write(f"Starting data import from {file_path}...")
        
        try:
            with open(file_path, 'rb') as f: # Open in binary mode
                result = process_energy_csv(f)
                
                if result['status'] == 'success':
                    self.stdout.write(self.style.SUCCESS(f"Data imported successfully!"))
                    self.stdout.write(f"Processed {result['processed_rows']} rows.")
                    if result['errors']:
                        self.stdout.write(self.style.WARNING("Some rows were skipped:"))
                        for error in result['errors']:
                            self.stdout.write(error)
                else:
                    self.stdout.write(self.style.ERROR(f"An error occurred: {result['message']}"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: {file_path} not found."))