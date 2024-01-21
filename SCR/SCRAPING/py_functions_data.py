import os
import requests 
import pandas as pd
import dask.dataframe as dd
from google.cloud import storage
from urllib.parse import urlencode
import warnings
warnings.filterwarnings("ignore")

def fetch_data(api_token, query, start=0, rows=2000, params=None, sort=None, subset=None, **kwargs):
    """
    The `fetch_data` function fetches data from an API using the provided parameters and returns the
    extracted relevant information.
    
    :param api_token: The `api_token` parameter is the access token required to authenticate and
    authorize the API request. It is used to identify and validate the user making the request
    :param query: The query parameter is used to specify the search query for the API. It is a string
    that represents the search query you want to perform
    :param start: The `start` parameter specifies the starting index of the results to be fetched. It is
    used for pagination, allowing you to retrieve results in batches, defaults to 0 (optional)
    :param rows: The "rows" parameter specifies the maximum number of results to be returned by the API.
    In this case, it is set to 2000, meaning that the API will return a maximum of 2000 documents that
    match the query, defaults to 2000 (optional)
    :param params: The `params` parameter is used to specify the fields that you want to retrieve from
    the API response. It should be a comma-separated string of field names. For example, if you want to
    retrieve the title and author fields, you can pass `params="title,author"`
    :param sort: The "sort" parameter is used to specify the sorting order of the results. It can be set
    to a field name to sort the results based on that field in ascending order. To sort in descending
    order, you can prefix the field name with a minus sign (-). For example, if you want
    :param subset: The "subset" parameter is used to filter the results based on a specific subset of
    the data. It is typically used to narrow down the search to a specific category or field. For
    example, if you are searching for articles related to astronomy, you can use the "subset" parameter
    to filter the
    :return: The function `fetch_data` returns the documents retrieved from the API query.
    """
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
    """
    The function fetches data from an API, updates a DataFrame, adds a new column with a link, saves the
    DataFrame to a CSV file, performs filtering and cleaning operations on the DataFrame, and returns
    the final DataFrame.
    
    :param api_token: The `api_token` parameter is the API token required to access the data from the
    API. You need to provide a valid API token to authenticate and fetch the data
    :param query: The query parameter is used to specify the search query for fetching data from the
    API. It is a string that defines the search criteria, such as keywords, authors, or specific fields
    to search within the data
    :param max_rows: The `max_rows` parameter specifies the maximum number of rows to fetch and update
    in the dataframe
    :param start: The `start` parameter is used to specify the starting index for fetching data from the
    API. It determines the position from which the data retrieval should begin
    :param params: The `params` parameter is used to pass additional parameters to the API call. It is a
    dictionary where the keys are the parameter names and the values are the parameter values. These
    parameters can be used to filter or modify the data that is fetched from the API
    :param sort: The "sort" parameter is used to specify the sorting order of the fetched data. It can
    be set to "date" to sort the data by date, "relevance" to sort the data by relevance, or
    "citation_count" to sort the data by citation count
    :param subset: The "subset" parameter is used to specify a subset of the data to fetch. It can be a
    list of field names to include in the fetched data. For example, if you only want to fetch the
    "title" and "abstract" fields, you can pass subset=['title', 'abstract
    :param percentile_filtering: The parameter "percentile_filtering" is a boolean value that determines
    whether or not to filter the DataFrame based on a percentile threshold. If set to True, the
    DataFrame will be filtered to keep only the rows with a specified metric (defined by
    "percentile_metric") above the threshold (defined by, defaults to False (optional)
    :param percentile_metric: The `percentile_metric` parameter is used to specify the column in the
    DataFrame that will be used for percentile filtering. This column should contain numerical values,
    defaults to read_count (optional)
    :param percentile_value: The `percentile_value` parameter is a value between 0 and 1 that determines
    the threshold for percentile filtering. It is used to filter the DataFrame to keep rows with a
    specified metric above the threshold. For example, if `percentile_value` is set to 0.75, it
    :param instruction_text: The `instruction_text` parameter is a string that represents the
    instruction or label for the data. It is used to add a new column called "Instruction" to the
    DataFrame. This column will contain the same instruction text for all rows in the DataFrame
    :return: the final filtered and processed DataFrame.
    """
   
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

    if percentile_filtering == 'True':
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





def upload_directory_to_gcp(bucket_name, source_directory, destination_blob_prefix):
    """
    The function `upload_directory_to_gcp` uploads a directory to a Google Cloud Storage bucket.
    
    :param bucket_name: The name of the GCP bucket where you want to upload the directory
    :param source_directory: The source_directory parameter is the path to the directory on your local
    machine that you want to upload to the GCP bucket
    :param destination_blob_prefix: The `destination_blob_prefix` parameter is a string that represents
    the prefix to be added to the destination blob name. It is used to specify the directory structure
    within the GCP bucket where the files will be uploaded. For example, if the
    `destination_blob_prefix` is set to "data/files",
    """
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







