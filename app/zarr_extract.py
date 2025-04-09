import os
import numpy as np
from scipy.io import savemat
import sys

try:
    import zarr
except ImportError:
    print("Error: zarr module not found. Please install with: pip install zarr")
    sys.exit(1)

def save_localizations_to_common_mat(parent_directory, output_file=None):
    all_data = {}  # Dictionary to hold all the data from all Zarr archives
    subfolders = []  # List to hold names of subfolders

    # Iterate over all subdirectories in the parent directory
    for subdir in os.listdir(parent_directory):
        subdir_path = os.path.join(parent_directory, subdir)
        if os.path.isdir(subdir_path) and subdir != '__pycache__':  # Skip __pycache__ directories
            subfolders.append(subdir)  # Collect subfolder names
            zarr_path = os.path.join(subdir_path, 'zarr', 'grd', 'mbm')  # Adjust the sub-path as necessary
            
            # Try alternate paths if the default doesn't exist
            if not os.path.exists(zarr_path):
                alternate_paths = [
                    os.path.join(subdir_path, 'zarr'),
                    os.path.join(subdir_path, 'data', 'zarr'),
                    os.path.join(subdir_path, 'mbm')
                ]
                
                for alt_path in alternate_paths:
                    if os.path.exists(alt_path):
                        zarr_path = alt_path
                        print(f"Using alternate zarr path: {zarr_path} for {subdir}")
                        break
            
            if os.path.exists(zarr_path):
                try:
                    archive = zarr.open(zarr_path, mode='r')
                    subdir_data = {}  # Dictionary to hold data from this specific archive
                    
                    for dataset_name in archive.keys():
                        if dataset_name.startswith('R'):
                            try:
                                if isinstance(archive[dataset_name], zarr.Array):
                                    subdir_data[dataset_name] = archive[dataset_name][:]
                                elif hasattr(archive[dataset_name], 'get'):
                                    subdir_data[dataset_name] = archive[dataset_name].get()
                            except Exception as e:
                                print(f"Error reading dataset {dataset_name}: {e}")
                    
                    if subdir_data:
                        all_data[subdir] = subdir_data  # Add this archive's data under its subdir name
                        print(f"Data from {subdir} added to the MAT file structure.")
                    else:
                        print(f"No valid data found to save in {subdir}")
                except Exception as e:
                    print(f"Error opening zarr archive for {subdir}: {e}")
            else:
                print(f"Zarr archive not found at {zarr_path}")
        else:
            if subdir != '__pycache__':  # Don't print message for __pycache__
                print(f"Skipping non-directory item: {subdir}")

    if all_data:
        # Use the provided output path or create a default one in a writable location
        if output_file:
            output_mat_file = output_file
        else:
            # Use user's home directory if no output file specified
            user_home = os.path.expanduser("~")
            subfolder_str = "_".join(sorted(subfolders))
            output_mat_file = os.path.join(user_home, f'correction_{subfolder_str}.mat')
        
        # Ensure the directory exists
        output_dir = os.path.dirname(output_mat_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Created directory: {output_dir}")
            except Exception as e:
                print(f"Warning: Couldn't create directory {output_dir}: {e}")
                # Fall back to user's home directory
                output_mat_file = os.path.join(os.path.expanduser("~"), 'correction.mat')
                print(f"Using fallback location: {output_mat_file}")
        
        try:
            savemat(output_mat_file, {'data': all_data})
            print(f"All data has been saved to {output_mat_file}")
            return output_mat_file
        except Exception as e:
            print(f"Error saving data to {output_mat_file}: {e}")
            # Attempt to save to user's home directory as a fallback
            fallback_path = os.path.join(os.path.expanduser("~"), 'correction.mat')
            try:
                savemat(fallback_path, {'data': all_data})
                print(f"Data saved to fallback location: {fallback_path}")
                return fallback_path
            except Exception as e2:
                print(f"Fatal error: Could not save data to fallback location: {e2}")
                return None
    else:
        print("No data collected from any subdirectories.")
        return None

# Helper function to find a valid data directory
# Helper function to find a valid data directory
def find_valid_directory():
    possible_directories = [
        os.path.join(os.getcwd(), 'example'),
        os.getcwd(),  # Current directory
        os.path.join(os.getcwd(), 'data'),
        os.path.join(os.path.dirname(os.getcwd()), 'example'),
        os.path.join(os.path.dirname(os.getcwd()), 'data'),
    ]
    
    # Check if any command-line arguments are provided for directory path
    if len(sys.argv) > 1:
        possible_directories.insert(0, sys.argv[1])  # Add user-provided path as first priority

    # Find first valid directory with subdirectories
    for directory in possible_directories:
        if os.path.exists(directory) and os.path.isdir(directory):
            # Check if it has subdirectories (potential round data)
            subdirs = [d for d in os.listdir(directory) 
                      if os.path.isdir(os.path.join(directory, d)) 
                      and not d.startswith('.') 
                      and not d == '__pycache__']
            if subdirs:
                print(f"Using directory: {directory}")
                print(f"Found {len(subdirs)} potential data directories: {', '.join(subdirs[:5])}" + 
                      ("..." if len(subdirs) > 5 else ""))
                return directory
    
    print("Error: Could not find a valid directory with data.")
    print("Please either:")
    print("1. Run this script from a directory containing data subdirectories, or")
    print("2. Provide a path to your data directory as a command-line argument:")
    print("   python zarr_data_processor.py /path/to/your/data")
    return None

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) >= 3:
        # If two arguments are provided, use them as input and output paths
        parent_directory = sys.argv[1]
        output_file = sys.argv[2]
        print(f"Using directory: {parent_directory}")
        print(f"Output will be saved to: {output_file}")
    elif len(sys.argv) == 2:
        # If only one argument, use it as input path and default output
        parent_directory = sys.argv[1]
        output_file = None
        print(f"Using directory: {parent_directory}")
        print("Output will be saved to default location")
    else:
        # No arguments, try to find a valid directory
        parent_directory = find_valid_directory()
        output_file = None
    
    if parent_directory:
        # If output_file is None, the function will use a default location
        result_file = save_localizations_to_common_mat(parent_directory, output_file)
        if result_file:
            print(f"Data processed and saved to {result_file}")
        else:
            print("Failed to save data")
            sys.exit(1)
    else:
        sys.exit(1)