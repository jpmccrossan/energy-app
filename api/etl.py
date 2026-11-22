# api/etl.py

import csv
from .models import EnergyData
from datetime import datetime
from io import StringIO

def process_energy_csv(file_obj):
    """
    Processes an uploaded CSV file object and updates the EnergyData in the database.
    Returns a count of rows processed and any errors encountered.
    See Notes.txt for details and an example of the curl command to use.
    """
    try:
        # Decode the file object, which is in bytes, to a string
        csv_text = file_obj.read().decode('utf-8')
        reader = csv.DictReader(StringIO(csv_text))
        
        # Clear existing data
        EnergyData.objects.all().delete()
        
        processed_count = 0
        errors = []

        for row_raw in reader:
            row = {k.lower().strip(): v for k, v in row_raw.items()}
            dt_str = row.get('date_time') or row.get('atetime')

            if not dt_str:
                errors.append(f"Skipping row: 'date_time' or 'atetime' column not found in {row}")
                continue

            try:
                if len(dt_str) > 3 and dt_str[-3] in ('+', '-') and dt_str[-2:].isdigit() and ':' not in dt_str[-3:]:
                    dt_str += ':00'
                
                dt_obj_aware = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S%z')

                EnergyData.objects.create(
                    date_time=dt_obj_aware,
                    net_demand=int(row.get('net_demand', 0)),
                    total_system_demand=int(row.get('total_system_demand', 0)),
                    england_wales_demand=int(row.get('england_wales_demand', 0)),
                    generation=int(row.get('generation', 0)),
                    gas=int(row.get('gas', 0)),
                    coal=int(row.get('coal', 0)),
                    nuclear=int(row.get('nuclear', 0)),
                    scot_wind=float(row.get('scot_wind', 0.0)),
                    eng_wind=float(row.get('eng_wind', 0.0)),
                    uk_wind=int(float(row.get('uk_wind', 0))),
                    wind_capacity=int(row.get('wind_capacity', 0)),
                    hydro=int(row.get('hydro', 0)),
                    imports=int(row.get('imports', 0)),
                    ifa_flow=int(row.get('ifa_flow', 0)),
                    ifa2_flow=int(row.get('ifa2_flow', 0)),
                    britned_flow=int(row.get('britned_flow', 0)),
                    moyle_flow=int(row.get('moyle_flow', 0)),
                    east_west_flow=int(row.get('east_west_flow', 0)),
                    nemo_flow=int(row.get('nemo_flow', 0)),
                    nsl_flow=int(row.get('nsl_flow', 0)),
                    eleclink_flow=int(row.get('eleclink_flow', 0)),
                    net_interc_flow=int(row.get('net_interc_flow', 0)),
                    biomass=int(row.get('biomass', 0)),
                    other=int(row.get('other', 0)),
                    solar=int(row.get('solar', 0)),
                    solar_cap=int(row.get('solar_cap', 0)),
                    pumped_storage=int(row.get('pumped_storage', 0)),
                    storage=int(row.get('storage', 0)),
                    carbon_intensity=int(row.get('carbon_intensity', 0)),
                    low_carbon=int(row.get('low_carbon', 0)),
                    zero_carbon=int(row.get('zero_carbon', 0)),
                    renewable=int(row.get('renewable', 0)),
                    fossil=int(row.get('fossil', 0)),
                    gas_perc=float(row.get('gas_perc', 0.0)),
                    coal_perc=float(row.get('coal_perc', 0.0)),
                    nuclear_perc=float(row.get('nuclear_perc', 0.0)),
                    wind_perc=float(row.get('wind_perc', 0.0)),
                    hydro_perc=float(row.get('hydro_perc', 0.0)),
                    imports_perc=float(row.get('imports_perc', 0.0)),
                    biomass_perc=float(row.get('biomass_perc', 0.0)),
                    other_perc=float(row.get('other_perc', 0.0)),
                    solar_perc=float(row.get('solar_perc', 0.0)),
                    storage_perc=float(row.get('storage_perc', 0.0)),
                    generation_perc=int(float(row.get('generation_perc', 0))),
                    low_carbon_perc=float(row.get('low_carbon_perc', 0.0)),
                    zero_carbon_perc=float(row.get('zero_carbon_perc', 0.0)),
                    renewable_perc=float(row.get('renewable_perc', 0.0)),
                    fossil_perc=float(row.get('fossil_perc', 0.0)),
                )
                processed_count += 1
            except (ValueError, KeyError) as e:
                errors.append(f"Skipping row due to error: {e}. Row: {row}")
                continue

        return {"status": "success", "processed_rows": processed_count, "errors": errors}
    except Exception as e:
        return {"status": "error", "message": str(e)}

