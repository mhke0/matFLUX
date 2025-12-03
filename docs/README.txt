                  _    ______ _    _    _ __  __
 _ __ ___   __ _ | |_ |  ____| |  | |  | |\ \/ /
| '_ ` _ \ / _` || __|| |__  | |  | |  | | \  / 
| | | | | | (_| || |_ |  __| | |_ | |__| | /  \ 
|_| |_| |_|\__,_| \__||_|    |___| \____/ /_/\_\


Tutorial for matFLUX 1.0
========================

Two variants:
  - Matlab App file (.mlapp).
  - Installer for Standalone Version with Matlab Runtime (Mac, Windows, Linux).


matFLUX is a MATLAB-based application designed for processing 3D MINFLUX localization data.
It provides tools for DBSCAN-based clustering, multi-channel alignment, and the analysis of nanoscale structures.
This guide will walk you through the entire workflow—from launching the app to exporting your results.

----------------------------------------------------------------
Overview
----------------------------------------------------------------

matFLUX is designed to work with MINFLUX .mat files containing localization data from Abberior MINFLUX systems.
The application provides a graphical user interface (GUI) featuring multiple tabs for:
  - Field of View Overview & DBSCAN adjustment
  - Analysis of Single Nanoscale Structures
  - Alignment & Correction of Multi-Channel Data
  - Multicolor Data Analysis for Single and Multiple Clusters
  - Line Profile & Distance Analysis
  - Radial Distribution Analysis
  - Cluster Statistics
  - Multi-Channel Summary
  - Quality Control & Trace Statistics
  - Localization Precision Analysis

The app includes interactive controls for loading data, adjusting DBSCAN clustering parameters (Epsilon and MinPts), applying drift corrections via bead data, and exporting processed data and figures.

WORKFLOW:
One-Target:
  - Load > Cluster > Inspect > Analyze > Export (Figures or Data)
Multi-Target:
  - Load Main Channel > Cluster > Alignment > Load Additional Channels >Cluster > Inspect > Analyze > Export (Figures or Data)

----------------------------------------------------------------
0. Requirements
----------------------------------------------------------------
To run matFLUX 1.0, ensure your system meets the following requirements:

1. **MATLAB Version:**
   - MATLAB R2018b or later is recommended. Some functions are only available starting with MATLAB R2020a.
   - App Designer must be available (included in recent MATLAB releases).

2. **MATLAB Toolboxes:**
   - **Statistics and Machine Learning Toolbox:**  
     Required for DBSCAN clustering (`dbscan` function).
   - **Image Processing Toolbox:**  
     Required for image filtering (e.g., `imgaussfilt3`), volume visualization (`volshow`), and other image-based operations.

3. **Python:** ONLY FOR THE ALIGNMENT FEATURE
   - A Python executable must be installed and accessible in your system path.  
     This is needed for running an integrated script (e.g., `zarr_extract.py`) to process bead correction data.
   - Python version has to be compatible with MATLAB (Python 3.8 or 3.10 is recommended).
   - Needed modules: numpy, zarr and scipy.

4. **External Files:**
   - This should automatically be installed with the .mLapp and the standalone version, but if not:
   - The python script called "zarr_extract.py" is included in the installation and should be in the "resources" folder of your app. 
!!!IN CASE IT IS NOT FOUND, THE SCRIPT LOCATION CAN BE ADDED MANUALLY IN THE APPS SETTINGS.!!!
   - Any image files (such as `camera.svg` for the export button) should be in the appropriate resource directory or in the same folder as the app.

----------------------------------------------------------------
1. Launching the Application
----------------------------------------------------------------
When you start matFLUX, the startup routine displays a welcome message:

  Welcome to matFLUX 1.0!

  Steps to begin:
  1. Click "Load/New" to load your MINFLUX file.
  2. Adjust DBSCAN (Epsilon, MinPts) as needed.
  3. Inspect your single clusters.
  4. Load bead corrections from your ZARR folders or skip directly to the multi-channel tab.
  5. Add additional channels and adjust x/y/z shifts.
  6. Explore the tabs for various analyses.

For detailed help, click the Help menu.

----------------------------------------------------------------
2. Loading Your Primary Data
----------------------------------------------------------------
- Click "New/Reset": Use the “New/Reset” button to load your primary MINFLUX .mat file.
	 The file should be exported from the Abberior MINFLUX software and contain the expected fields (e.g., itr.loc). If not, an error dialog will provide details. Both new and old data format are supported.

- After loading, the file name appears in the File Name label.

----------------------------------------------------------------
3. Adjusting Clustering Parameters (DBSCAN)
----------------------------------------------------------------
matFLUX uses the DBSCAN algorithm to cluster your data (Esther et al. 1996).

Key Parameters:
  - Epsilon: Defines the neighborhood radius. (Default ~35)
  - MinPts: Minimum number of points required to form a cluster. (Default 5)

How to Adjust:
  - Use the spinner controls at the top to change these values.
  - The cluster visualization in the “Cluster Overview” and “Data Field of View” tabs updates immediately.

** Clusters will appear color-coded. Check for separation. Adjust the color-map in Settings. Color coding for z-scale, trc and loc numbers available.
** Noise filtered-out by DBSCAN can be removed with via the button 'Remove Noise'.

----------------------------------------------------------------
4. Inspecting Single Clusters
----------------------------------------------------------------
Switch to the "Single Cluster Analysis" tab.

What You Can Do Here:
  - View Clusters: Clusters are visualized color-coded. Optional displays like ellipsoid fitting or alpha shapes show boundaries.
  - Use the list box to select specific clusters for a detailed view. 
  - Select multiple clusters at once and generate overlay.

----------------------------------------------------------------
5. Alignment & Drift Correction (Optional)
----------------------------------------------------------------
THIS STEP CAN BE SKIPPED, IF NO ALIGNMENT IS WANTED
In the "Alignment & Drift Correction" tab:

Before:
  - Export Folders with Bead Data Files (Zarr format) completely from your Abberior MINFLUX setup. All folders should be named after their respective channel and placed into one Bead Data parent folder. The Alignment then continues automatically.

Workflow:
  - Load Bead Correction Data: Click “Load Bead Data” and select the Bead Data parent folder.
    (If skipped, the app uses the primary data without correction.)
  - Visualization: Two panels display original bead localization and the correction.
  - The correction factors and respective channel names are already transferred into the 'Multi-Channel Overlay' tab.


----------------------------------------------------------------
6. Multi-Channel Overview
----------------------------------------------------------------
Multicolor Data & Corrections Tab:
  - Adding Channels: Use the “Add/Refresh Channel” button to load additional channels.
  - Optional: Manual Adjustments: Use the Channel Details panel to adjust x, y, and z shifts.
  - Turn DBSCAN on and off for data inspection.

Combined Channel Analysis Tab:
  - Overview: Compare multiple channels using overlaid scatter plots showing data after alignment.

Data Export:
  - You can export your combined and aligned multi-channel MINFLUX data as either .mat data file or as .tif for further use (e.g. ImageJ, Imaris, Matlab)

----------------------------------------------------------------
7. Detailed Analysis Tabs
----------------------------------------------------------------
Each additional tab focuses on a specific analysis:

  - Histogram/Line Profile & Distance Analysis:
      Generates line profiles and histograms of distances from cluster centroids. Also for multiple channels.

  - Radial Distribution Analysis:
      Uses a polar plot representation to analyze radial distributions relative to centroids.

  - Quality Control & Trace Statistics:
      Displays trace statistics (e.g., average localizations per trace) along with histograms.

  - Cluster Statistics:
      Presents numerical summaries including cluster volume, surface area, and nearest neighbor distances.

  - Multi-Channel Summary:
      Provides a summary of localization counts and trace data across all channels.

  - Localization Precision Analysis:
      Evaluates the precision of localization data (e.g., standard deviations and errors for x, y, and z).

Each tab includes helpful tooltips or info icons that explain its purpose.

----------------------------------------------------------------
8. Exporting Data and Figures
----------------------------------------------------------------
When your analysis is complete:

- Export Data: 
  Click the “Export .mat/.tif” button (located in the Multi-Channel tab) to save your processed data.
  After successful export, a confirmation message appears.

- Saving Figures:
  Use the camera button to save currently displayed plots as PDF or PNG files.
  A file dialog will prompt you for a save location, and the figure will be saved with vector content if possible.

----------------------------------------------------------------
9. Accessing Help and Additional Information
----------------------------------------------------------------
- Help Menu: 
  Click the Help menu for a dedicated help window containing an overview, instructions, FAQs, and troubleshooting tips.
- About Menu: 
  Provides version, developer, contact information and licensing details.

----------------------------------------------------------------
Summary
----------------------------------------------------------------
matFLUX 1.0 offers a comprehensive workflow for 3D MINFLUX data processing—from data loading and clustering to alignment and multi-channel analysis.
Its user-friendly controls, detailed tooltips, and clear visual feedback help you extract meaningful insights from your localization data.

Easy to use with MATLAB or standalone, and fully documented.

Keep this README handy as you are using the app. Refer to the Help menu or contact: moritz.hacke@med.uni-heidelberg.de
___________________________________________________
MIT License

Copyright (c) 2025 Moritz Hacke

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell      
copies of the Software, and to permit persons to whom the Software is         
furnished to do so, subject to the following conditions:                       

The above copyright notice and this permission notice shall be included in    
all copies or substantial portions of the Software.                           

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR    
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,      
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE   
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER        
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN     
THE SOFTWARE.
___________________________________________________
Moritz Hacke, Heidelberg, 04/25
