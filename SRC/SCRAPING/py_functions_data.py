import os
import requests 
import pandas as pd
import dask.dataframe as dd
from google.cloud import storage
from urllib.parse import urlencode
import warnings
warnings.filterwarnings("ignore")

def fetch_data(api_token, query, start=0, rows=2000, params=None, sort=None, subset=None, **kwargs):
    # API query
    encoded_query = urlencode({
        "q": query,
        "fl": params,
        "rows": rows,
        "start": start,
        "sort": sort,
        "fq": subset
    })

    # API request
    results = requests.get(f"https://api.adsabs.harvard.edu/v1/search/query?{encoded_query}",
                           headers={'Authorization': 'Bearer ' + api_token})

    # Extract relevant information
    docs = results.json()['response']['docs']

    return docs

def fetch_and_update_dataframe(api_token, query, max_rows, start, params=None, sort=None, subset=None, percentile_filtering=False, percentile_metric='read_count', percentile_value=0.75, instruction_text=""):
    chunk_size = 2000
    dataframe = pd.DataFrame()

    while len(dataframe) < max_rows:
        # Fetch data
        docs = fetch_data(api_token, query, start=start, rows=chunk_size, params=params, sort=sort, subset=subset)

        # Break the loop if no more data is available
        if not docs:
            break

        # Update the DataFrame
        dataframe = pd.concat([dataframe, pd.DataFrame(docs)], ignore_index=True)

        # Increment start for the next API call
        start += chunk_size

        # Break the loop if the maximum number of rows is reached
        if len(dataframe) >= max_rows:
            break

    # Add a new column with arXiv PDF download link
    dataframe['arXiv_PDF_Link'] = dataframe['bibcode'].apply(lambda x: f"https://ui.adsabs.harvard.edu/link_gateway/{x}/EPRINT_PDF")

    # Save DataFrame to CSV
    dask_df = dd.from_pandas(dataframe, npartitions=10)

    filtered_df = dask_df.dropna(subset=['bibcode', 'title', 'abstract', 'keyword', percentile_metric], how='any')
    os.makedirs('data', exist_ok=True)
    filtered_df.compute().to_csv("data/output/Cleaned.csv", index=False)

    if percentile_filtering:
        metric_threshold = filtered_df[percentile_metric].quantile(percentile_value)
        # Filter the DataFrame to keep rows with the specified metric above the threshold
        filtered_df = filtered_df.loc[filtered_df[percentile_metric] >= metric_threshold]

    pattern = r"[^a-zA-Z0-9\s\.]"
    filtered_df['title'] = filtered_df['title'].str.replace(pattern, '', regex=True)
    filtered_df['abstract'] = filtered_df['abstract'].str.replace(pattern, '', regex=True)

    df_model_dataset = filtered_df.loc[:, ['title', 'abstract']]

    # Function to add a constant column
    def add_constant_column(df, column_name, text):
        df[column_name] = text
        return df

    # Add the instruction column
    df_training = df_model_dataset.map_partitions(add_constant_column, column_name='Instruction', text=instruction_text)
    df_training.compute().to_csv("data/output/Modeling.csv", index=False)

    return 


# 4. Define a special function
def upload_to_storage(bucket_name: str, source_file_path: str, destination_blob_path: str):
  """Uploads a file to the bucket."""
  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(destination_blob_path)
  blob.upload_from_filename(source_file_path)
  print(f'The file {source_file_path} is uploaded to GCP bucket path: {destination_blob_path}')
  return None


def upload_directory_to_gcp(bucket_name, source_directory, destination_blob_prefix):
    """Uploads a directory to the GCP bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for local_file in os.listdir(source_directory):
        if not os.path.isfile(os.path.join(source_directory, local_file)):
            continue

        local_file_path = os.path.join(source_directory, local_file)
        blob_name = os.path.join(destination_blob_prefix, local_file)
        blob = bucket.blob(blob_name)

        blob.upload_from_filename(local_file_path)
        print(f"{local_file_path} uploaded to {blob_name}.")







