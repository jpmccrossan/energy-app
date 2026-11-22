# Django Energy API

A REST API for half-hourly UK electricity data (2020 to 2023): demand, generation by fuel, interconnector flows
and carbon intensity. Built with Django, Django REST framework, django-filter and PostgreSQL.

- `GET /api/v1/energy/`: filter, order and paginate the data (see the examples below).
- `POST /api/v1/energy/upload/`: load a CSV through the ETL pipeline (`api/etl.py`).
- `python manage.py import_energy_data`: the same import from the command line, reading `energy_data.csv` in the current folder.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then set your own values and export them (or use your shell's env tooling)
python manage.py migrate
python manage.py runserver
```

Settings come from environment variables (`DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD` and the rest in
`.env.example`), so no secrets live in the code. The data CSV is not included in the repo; the example data comes
from the Kaggle dataset linked below.

---

API Usage and Examples
Updating the Database via ETL
To update the database with a new CSV file, you can use the curl command to send a POST request to the upload endpoint.

curl -X POST -H "Content-Type: multipart/form-data" -F "file=@energy_data.csv" http://127.0.0.1:8000/api/v1/energy/upload/

Note: The -F "file=@energy_data.csv" part assumes that the energy_data.csv file is located in the same directory from which you are running the curl command.


(Example data from:
https://www.kaggle.com/datasets/danielparke/uk-energy-data-2020-23?select=UK_Fuel_Mix.csv)



Example API Calls
Here are several examples demonstrating how to combine filtering, pagination, and other parameters to make powerful and complex requests.




1. The "Cleanest Hour" Report
Goal: Find the top 10 moments in all of 2023 with the lowest carbon intensity. This is perfect for finding the most environmentally friendly periods.

API Request URL:

http://127.0.0.1:8000/api/v1/energy/?date_time__year=2023&ordering=carbon_intensity&total_limit=10

Why it's cool: This query filters for a whole year, then uses a new ordering parameter to sort the results by carbon_intensity in ascending order, and finally uses total_limit=10 to slice off just the top 10 results.

Note: For this to work, you'd add ordering to the filter_backends and ordering_fields to the view, a great next step!




2. "Fossil Fuel Dependency" Deep Dive
Goal: You want to analyze the 50 moments in June 2023 when the system relied most heavily on gas (over 13,000 MW), but you want to examine this data in small, manageable chunks of 5 records per page. This is great for detailed analysis without being overwhelmed.

API Request for Page 2:

http://127.0.0.1:8000/api/v1/energy/?date_time__year=2023&date_time__month=6&gas__gt=13000&total_limit=50&page_size=5&page=2

Why it's cool: It combines four powerful features:

Filters by date (year, month).

Filters by a data value (gas__gt).

Limits the entire investigation to a set of 50 records (total_limit=50).

Paginates through that smaller set in "micro-batches" of 5 (page_size=5).




3. "Get All Solar Peak Data for Summer"
Goal: You need every single data point from June, July, and August of 2023 where solar power generation was exceptionally high (over 7,000 MW), and you want it all in one single list for a script to process.

API Request URL:

http://127.0.0.1:8000/api/v1/energy/?date_time__year=2023&date_time__month__in=6,7,8&solar__gt=7000&total_limit=0

Why it's cool: It uses __in for the month to query a range, filters by a high solar value, and then uses total_limit=0 to bypass pagination entirely, delivering a complete, raw dataset for your specific query.

Note: month__in requires a small tweak to your filterset_fields to allow list-based filtering, another great potential enhancement!




4. "Low Nuclear, High Wind Anomaly"
Goal: Find if there were ever times in 2023 when nuclear power was running low (e.g., < 5300 MW) while wind power's contribution was simultaneously very high (e.g., > 20%). Let's get the first 20 such events.

API Request URL:

http://127.0.0.1:8000/api/v1/energy/?date_time__year=2023&nuclear__lt=5300&wind_perc__gt=20&total_limit=20

Why it's cool: This is a classic anomaly detection query. It correlates two separate conditions across a vast dataset and uses total_limit=20 to neatly package the first 20 occurrences for investigation.




5. Post-ETL Data "Spot Check"
Goal: You've just uploaded a new CSV using your ETL endpoint. You need to quickly verify that the data looks correct. You can do this by fetching the very first record and the 10,000th record to check for data integrity at different points in the file.

Get the first record:

http://127.0.0.1:8000/api/v1/energy/?total_limit=1

Get the 10,000th record:

http://127.0.0.1:8000/api/v1/energy/?page_size=1&page=10000

Why it's cool: This shows a practical, real-world use case for your API. The first query confirms the start of the dataset. The second query uses pagination in a clever way—by setting the page size to 1 and jumping to a specific page number—to precisely sample a single record from deep within the dataset.