"""Convert NESO's public "Historic GB Generation Mix" CSV into this app's energy_data.csv format.

Download df_fuel_ckan.csv from https://www.neso.energy/data-portal/historic-generation-mix (no account needed), then:

    python scripts/neso_to_energy_csv.py df_fuel_ckan.csv --from-year 2020 --to-year 2023

This writes energy_data.csv next to manage.py, ready for `python manage.py import_energy_data`.
NESO's file has the generation mix, carbon intensity and percentage columns. It does not include demand or
interconnector flows, so those fields import as 0.
"""
import argparse
import csv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# app column -> NESO column, for whole-number fields (MW, gCO2/kWh)
INTS = {
    'gas': 'GAS', 'coal': 'COAL', 'nuclear': 'NUCLEAR', 'hydro': 'HYDRO', 'imports': 'IMPORTS',
    'biomass': 'BIOMASS', 'other': 'OTHER', 'solar': 'SOLAR', 'storage': 'STORAGE', 'generation': 'GENERATION',
    'carbon_intensity': 'CARBON_INTENSITY', 'low_carbon': 'LOW_CARBON', 'zero_carbon': 'ZERO_CARBON',
    'renewable': 'RENEWABLE', 'fossil': 'FOSSIL',
}
# app column -> NESO column, for percentages
PERCS = {
    'gas_perc': 'GAS_perc', 'coal_perc': 'COAL_perc', 'nuclear_perc': 'NUCLEAR_perc', 'hydro_perc': 'HYDRO_perc',
    'imports_perc': 'IMPORTS_perc', 'biomass_perc': 'BIOMASS_perc', 'other_perc': 'OTHER_perc',
    'solar_perc': 'SOLAR_perc', 'storage_perc': 'STORAGE_perc', 'low_carbon_perc': 'LOW_CARBON_perc',
    'zero_carbon_perc': 'ZERO_CARBON_perc', 'renewable_perc': 'RENEWABLE_perc', 'fossil_perc': 'FOSSIL_perc',
}


def num(row: dict, key: str) -> float:
    value = row.get(key, '')
    return float(value) if value not in ('', None) else 0.0


def convert(src: Path, dest: Path, from_year: int, to_year: int) -> int:
    fields = ['date_time', 'uk_wind', 'wind_perc', 'generation_perc', *INTS, *PERCS]
    count = 0
    with src.open(newline='') as f_in, dest.open('w', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fields)
        writer.writeheader()
        for row in csv.DictReader(f_in):
            when = datetime.fromisoformat(row['DATETIME'].replace('Z', ''))
            if not from_year <= when.year <= to_year:
                continue
            out = {
                'date_time': when.strftime('%Y-%m-%d %H:%M:%S') + '+00:00',  # NESO times are UTC
                # transmission plus embedded (distribution-connected) wind
                'uk_wind': round(num(row, 'WIND') + num(row, 'WIND_EMB')),
                'wind_perc': round(num(row, 'WIND_perc') + num(row, 'WIND_EMB_perc'), 1),
                'generation_perc': round(num(row, 'GENERATION_perc')),
            }
            out.update({k: round(num(row, v)) for k, v in INTS.items()})
            out.update({k: round(num(row, v), 1) for k, v in PERCS.items()})
            writer.writerow(out)
            count += 1
    return count


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source', type=Path, help="NESO's df_fuel_ckan.csv")
    ap.add_argument('-o', '--output', type=Path, default=ROOT / 'energy_data.csv')
    ap.add_argument('--from-year', type=int, default=2020)
    ap.add_argument('--to-year', type=int, default=2023)
    args = ap.parse_args()
    rows = convert(args.source, args.output, args.from_year, args.to_year)
    print(f'Wrote {rows} rows to {args.output}')


if __name__ == '__main__':
    main()
