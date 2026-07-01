import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import re

from roman_hlis_l2_driver.fullfovexport.fullfov import FullFoVImage


def process_single_observation(obs_id, input_dir, output_dir):
    """Processes a single observation ID into a FullFoV image."""
    try:
        # Note: Keeping your exact logic here, but make sure FullFoVImage 
        # internally handles the '{:d}' string formatting if that's expected by the library.
        FullFoVImage(
            f"{input_dir}/sim_L2_H158_{obs_id}_{{:d}}.asdf",
            maskfile=f"{input_dir}/sim_L2_H158_{obs_id}_{{:d}}_mask.fits"
        ).to_file(f"{output_dir}/ffov_{obs_id}.fits", overwrite=True)
        print(f"Successfully processed observation ID: {obs_id}")
    except Exception as exc:
        print(f"Observation ID {obs_id} generated an exception: {exc}")


def extract_obs_ids(input_dir):
    """Scans the input directory and extracts unique observation IDs from filenames."""
    obs_ids = set()
    # Matches files like: sim_L2_H158_12345_0.asdf -> extracts '12345'
    pattern = re.compile(r"sim_L2_H158_([a-zA-Z0-9_-]+)_\d+\.asdf")
    
    for file_path in Path(input_dir).glob("*.asdf"):
        match = pattern.match(file_path.name)
        if match:
            obs_ids.add(match.group(1))
            
    return list(obs_ids)


def main():
    parser = argparse.ArgumentParser(description="Process L2 files into ffov images")
    parser.add_argument("--input-dir", default="input", help="Directory containing the L2 files")
    parser.add_argument("--output-dir", default="output", help="Directory to save the resulting ffov images")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of parallel threads")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # Automatically find all unique observation IDs in the directory
    obs_ids = extract_obs_ids(args.input_dir)
    
    if not obs_ids:
        print(f"No valid L2 files found in '{args.input_dir}'. Exiting.")
        return

    print(f"Starting pipeline for {len(obs_ids)} observation(s) using {args.max_workers} worker threads...")
    
    # Run the pipeline concurrently across different observation IDs
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(process_single_observation, obs_id, args.input_dir, args.output_dir): obs_id 
            for obs_id in obs_ids
        }
        
        for future in as_completed(futures):
            obs_id = futures[future]
            # Exceptions inside the thread are raised when calling .result()
            future.result()


if __name__ == "__main__":
    main()