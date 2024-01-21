from py_functions_data import  fetch_and_update_dataframe, upload_directory_to_gcp
import os
import warnings
warnings.filterwarnings("ignore")
import dotenv 
dotenv.load_dotenv()

# the function fetch_and_update_dataframe is defined in the file py_functions_data.py, it creates a dataframe from the ADS API
fetch_and_update_dataframe(
    api_token=os.getenv('API_TOKEN'),
    query=os.getenv('QUERY'), 
    max_rows=int(os.getenv('MAX_ROWS')),
    start=int(os.getenv('START')), 
    params=os.getenv('PARAMS'), 
    sort=os.getenv('SORT'), 
    subset=os.getenv('SUBSET'), 
    percentile_filtering=os.getenv('PERCENTILE_FILTERING'), 
    percentile_metric=os.getenv('PERCENTILE_METRIC'), 
    percentile_value=float(os.getenv('PERCENTILE_VALUE')), 
    instruction_text=os.getenv('INSTRUCTION_TEXT')
)
# The code block is checking the value of the environment variable `upload_to_gcp`. If the value is
# not empty or False, it proceeds to upload a directory to Google Cloud Storage (GCP).
upload_to_gcp = os.getenv('upload_to_gcp')
if upload_to_gcp == 'True':
    # 2. Set JSON key as environment variable
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.getenv("key_path")

    # # 3. Specify a bucket name and other details
    bucket_name = os.getenv("bucket_name")

    upload_directory_to_gcp(bucket_name =bucket_name , source_directory =f"/data/output", destination_blob_prefix = "new/data/")
else:
    print("upload_to_gcp is not set to True, skipping upload to GCP")
