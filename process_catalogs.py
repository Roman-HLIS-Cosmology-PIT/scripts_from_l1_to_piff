import io
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3
from botocore import UNSIGNED
from botocore.config import Config
import pandas as pd

# Constants for the OpenUniverse 2024 S3 bucket layout
BUCKET_NAME = "nasa-irsa-simulations"
BASE_PREFIX = "openuniverse2024/roman/full/RomanWAS/truth/H158/"

def process_single_observation(obs_id, output_dir="output"):
    """
    Downloads and processes all catalog .txt files for a single observation ID,
    filters for stars, extracts specific columns, and saves as a single parquet file.
    """
    print(f"[Start] Processing Observation ID: {obs_id}")
    
    # Instantiate an anonymous S3 client (thread-safe inside the worker)
    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    prefix = f"{BASE_PREFIX}{obs_id}/"
    
    # 1. List all files inside the observation directory
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix)
        
        txt_keys = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'].endswith('.txt'):
                        txt_keys.append(obj['Key'])
    except Exception as e:
        print(f"[Error] Failed to list objects for Observation {obs_id}: {e}")
        return False

    if not txt_keys:
        print(f"[Warning] No .txt files found for Observation {obs_id}")
        return False

    dfs = []
    required_cols = ['object_id', 'ra', 'dec', 'mag']
    
    # 2. Process each text file catalog found for this observation ID
    for key in txt_keys:
        file_name = os.path.basename(key)
        try:
            # Stream the file content directly into pandas from memory
            response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
            
            # Wrap the stream so we can read it line-by-line as text safely
            file_stream = io.TextIOWrapper(response['Body'], encoding='utf-8')
            
            # Step A: Loop through the stream to isolate the correct header line
            columns = None
            for line in file_stream:
                clean_line = line.strip()
                if clean_line.startswith('#'):
                    # Strip the comment character and split into clean column tokens
                    tokens = clean_line.replace('#', '').split()
                    #print(tokens)
                    # Confirm this is the main header line by matching expected keywords
                    if 'object_id' in tokens and 'obj_type' in tokens:
                        columns = tokens
                        break # Stop reading line-by-line; the stream is now parked at row 1 of data
            
            if columns is None:
                print(f"  [{obs_id}] Could not find a valid header line in {file_name}. Skipping.")
                continue
            
            # Step B: Read the rest of the file utilizing our explicit column list
            # Passing 'names' tells pandas exactly how to map data left-to-right
            df = pd.read_csv(file_stream, sep=r'\s+', names=columns, comment='#')
            
            # Filter rows where obj_type is 'star'
            df_stars = df[df['obj_type'] == 'star']
            
            # Extract only the specified columns if they exist
            cols_to_extract = [col for col in required_cols if col in df_stars.columns]
            df_stars = df_stars[cols_to_extract]
            
            if not df_stars.empty:
                dfs.append(df_stars)
                
        except Exception as e:
            print(f"  [{obs_id}] Error processing file {file_name}: {e}")

    if not dfs:
        print(f"[Finished] No star records found for Observation {obs_id}")
        return False

    # 3. Concatenate all pieces into a single dataframe for the observation ID
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Reindex to ensure the final output strictly adheres to requested schema order
    combined_df = combined_df.reindex(columns=required_cols)
    
    # 4. Save to Parquet
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"stars_{obs_id}.parquet")
    
    try:
        combined_df.to_parquet(output_file, index=False)
        print(f"[Success] Saved parquet file for Observation {obs_id} -> {output_file}")
        return True
    except Exception as e:
        print(f"[Error] Failed to save parquet file for {obs_id}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Process OpenUniverse 2024 S3 Catalogs for Stars.")
    parser.add_argument("obs_ids", nargs="+", help="One or more Observation IDs separated by spaces")
    parser.add_argument("--output-dir", default="output", help="Directory to save the resulting Parquet files")
    parser.add_argument("--max-workers", type=int, default=4, help="Number of parallel workers (Observation IDs processed at once)")
    
    args = parser.parse_args()
    
    print(f"Starting pipeline for {len(args.obs_ids)} observation(s) using {args.max_workers} worker threads...")
    
    # Run the pipeline concurrently across different observation IDs
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(process_single_observation, obs_id, args.output_dir): obs_id 
            for obs_id in args.obs_ids
        }
        
        for future in as_completed(futures):
            obs_id = futures[future]
            try:
                future.result()
            except Exception as exc:
                print(f"Observation ID {obs_id} generated an exception: {exc}")

if __name__ == "__main__":
    main()