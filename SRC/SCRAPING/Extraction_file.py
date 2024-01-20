from py_functions_data import  fetch_and_update_dataframe, upload_to_storage, upload_directory_to_gcp
import os
import warnings
warnings.filterwarnings("ignore")
import dotenv 
dotenv.load_dotenv()

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

# 2. Set JSON key as environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.getenv("key_path")

# # 3. Specify a bucket name and other details
bucket_name = os.getenv("bucket_name")

upload_directory_to_gcp(bucket_name =bucket_name , source_directory =f"/data/output", destination_blob_prefix = "new/data/")
