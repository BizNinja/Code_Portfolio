# Code_Portfolio
Arduino GCP POC
  - The goal of this project was to create a proof on concept connection between an arduino board and the cloud. The code here is for a load to an arduino board. Also requires Google IoT and Google Cloud Pub/Sub

Google Cloud Big Query ETL
  - The goal of this project was to provide low cost ETL leveraging google cloud Big Query and it's free tier.
  - Tecnology spans batch scripting, python, and BQ SQL syntax to perform data movement.

Informatica Axon API
  - The goal of this project was to automate a load into Informatica Axon Data Governance using the API leveraging Python.
  - The API must be called to obtain a token, and then sent a file to process, then sent a field mapping to finalize processing.

Iterate Files and Load
  - This leverages Python to iterate over a directory, and load all csv's into a local SQL DB.
  - Files are then sent to an archive after processing.

Pandas
  - Duplicate of some code within the Google Cloud Big Query ETL project.
  - This code adds a date column to the data frame leveraging an extract date listed in the document.
  - This was need because the Months would come across without any year distinction.

Python SQL Connection
  - This is a generic Python SQL connection that exports data to a CSV from a SQL query.
  - Leverages pyodbc
