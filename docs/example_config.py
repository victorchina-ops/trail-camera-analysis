# -*- coding: utf-8 -*-
"""
Example Configuration File
==========================

This file shows the parameters you can customize in the scripts.
Copy these sections to the top of the script to configure for your needs.

All parameters are optional - scripts have sensible defaults.
"""

# ===========================================================================
# EXAMPLE 1: Single Site with 1,000 images
# ===========================================================================

# Simple configuration for one site
INPUT_FOLDERS = {
    'Hiking_Trail': '/content/drive/MyDrive/TrailCamera/hiking_trail',
}

OUTPUT_FOLDER = '/content/drive/MyDrive/TrailCamera/results'

VALIDATION_SIZE = 100
MAX_PRODUCTION = 1000
DEVICE = "cuda"  # Use GPU (faster)


# ===========================================================================
# EXAMPLE 2: Multiple Sites
# ===========================================================================

# Configuration for multiple monitoring sites
INPUT_FOLDERS = {
    'Carmel_Ridge': '/content/drive/MyDrive/Monitoring/carmel',
    'Ben_Gurion_Tomb': '/content/drive/MyDrive/Monitoring/bg_tomb',
    'Ein_Aquev': '/content/drive/MyDrive/Monitoring/ein_aquev',
    'Research_Site_A': '/content/drive/MyDrive/Monitoring/site_a',
    'Research_Site_B': '/content/drive/MyDrive/Monitoring/site_b',
}

OUTPUT_FOLDER = '/content/drive/MyDrive/Monitoring/results'

VALIDATION_SIZE = 50  # 50 per site for validation
MAX_PRODUCTION = 5000  # Process 5,000 total images


# ===========================================================================
# EXAMPLE 3: Quick Test / Small Sample
# ===========================================================================

# Use this to test the pipeline quickly before full run
INPUT_FOLDERS = {
    'Test_Site': '/content/drive/MyDrive/test_images',
}

OUTPUT_FOLDER = '/content/drive/MyDrive/test_results'

VALIDATION_SIZE = 10  # Small validation set
MAX_PRODUCTION = 50   # Process only 50 images for testing
DEVICE = "cpu"  # Use CPU if low on VRAM


# ===========================================================================
# EXAMPLE 4: Large Scale Processing (3,000+ images)
# ===========================================================================

# Configuration for large batch processing
INPUT_FOLDERS = {
    'Site_1': '/content/drive/MyDrive/LargeScale/site_1',
    'Site_2': '/content/drive/MyDrive/LargeScale/site_2',
    'Site_3': '/content/drive/MyDrive/LargeScale/site_3',
    'Site_4': '/content/drive/MyDrive/LargeScale/site_4',
    'Site_5': '/content/drive/MyDrive/LargeScale/site_5',
}

OUTPUT_FOLDER = '/content/drive/MyDrive/LargeScale/results'

VALIDATION_SIZE = 200  # Larger validation for reliability
MAX_PRODUCTION = None  # Process ALL images in folders
DEVICE = "cuda"

SAVE_INTERVAL = 100  # Save checkpoint every 100 images


# ===========================================================================
# EXAMPLE 5: Conservation Organization (Cost-Conscious)
# ===========================================================================

# Use Pipeline Only version (free) for conservation NGOs
# This example wouldn't use Claude API

INPUT_FOLDERS = {
    'Protected_Area_1': '/content/drive/MyDrive/Conservation/pa_1',
    'Protected_Area_2': '/content/drive/MyDrive/Conservation/pa_2',
    'Protected_Area_3': '/content/drive/MyDrive/Conservation/pa_3',
}

OUTPUT_FOLDER = '/content/drive/MyDrive/Conservation/results'

VALIDATION_SIZE = 50
MAX_PRODUCTION = 2000
DEVICE = "cuda"
VALIDATION_SHEETS = True  # Generate visual validation


# ===========================================================================
# EXAMPLE 6: Research Project (High Accuracy Required)
# ===========================================================================

# Use Full Pipeline with stricter thresholds for research
INPUT_FOLDERS = {
    'Research_Plot_A': '/content/drive/MyDrive/Research/plot_a',
    'Research_Plot_B': '/content/drive/MyDrive/Research/plot_b',
}

OUTPUT_FOLDER = '/content/drive/MyDrive/Research/results'

VALIDATION_SIZE = 200  # Larger validation set
MAX_PRODUCTION = 1000

# Stricter detection thresholds
MD_THRESHOLD = 0.40  # Higher = stricter
CLIP_MIN_CONFIDENCE = 0.50

DEVICE = "cuda"
VALIDATION_SHEETS = True


# ===========================================================================
# PARAMETER EXPLANATIONS
# ===========================================================================

"""
INPUT_FOLDERS (dictionary):
    Keys: Site name (string) - appears in CSV "Site" column
    Values: Full path to folder containing images
    Example:
        'Carmel': '/content/drive/MyDrive/images/carmel'
    Notes:
        - Use absolute paths (/content/drive/MyDrive/...)
        - Folder can contain .jpg, .jpeg, .png files
        - Must already exist (script won't create it)

OUTPUT_FOLDER (string):
    Path where results CSV and validation sheets saved
    Example: '/content/drive/MyDrive/results'
    Notes:
        - Script creates folder if doesn't exist
        - Results saved as: Results_[timestamp].csv
        - Validation sheets: Validation_Sheet_[page].png

VALIDATION_SIZE (integer):
    Number of images to process in validation phase
    Default: 100
    Notes:
        - First N images are validation set
        - Generates visual validation sheets
        - Remaining images go to production
        - Recommended: 50-200

MAX_PRODUCTION (integer or None):
    Maximum total images to process (validation + production)
    Default: 1000
    Options:
        - 1000: Process 1,000 total images
        - None: Process ALL images in INPUT_FOLDERS
    Notes:
        - Images processed in random order
        - Limits useful for testing
        - Set to None for full dataset processing

DEVICE (string):
    Which processor to use for ML models
    Options:
        - "cuda": GPU (faster, ~1-2 sec/image)
        - "cpu": CPU (slower, ~5-10 sec/image)
    Default: Auto-detect (cuda if available)
    Notes:
        - GPU ~5x faster than CPU
        - Colab free tier includes GPU
        - Check: Click Runtime > Change Runtime Type

VALIDATION_SHEETS (boolean):
    Whether to generate visual validation sheets
    Default: True
    Notes:
        - True: Creates PDF with images + results overlaid
        - False: Skips sheet generation (saves time)
        - Useful for quality control

SAVE_INTERVAL (integer):
    Save checkpoint CSV every N images
    Default: 50
    Notes:
        - Saves progress in case of interruption
        - Creates checkpoint_[number]_[timestamp].csv
        - Useful for large jobs (100+ images)

MD_THRESHOLD (float):
    MegaDetector confidence threshold (0.0-1.0)
    Default: 0.35
    Notes:
        - Higher = stricter (fewer false positives)
        - Lower = more lenient (catches more people)
        - 0.35 is good balance
        - Increase to 0.40-0.50 if too many false positives

CLIP_MIN_CONFIDENCE (float):
    CLIP classification confidence (0.0-1.0)
    Default: 0.40
    Notes:
        - Only affects adult/child classification
        - Higher = stricter classification
        - Lower = classify more uncertain cases
        - Usually OK to leave default

TIMESTAMP (string):
    Auto-generated timestamp for output files
    Generated as: datetime.now().strftime("%Y%m%d_%H%M%S")
    Example: "20260211_034520"
    Notes:
        - Used in output filenames to avoid overwrites
        - Don't modify this - auto-generated
"""


# ===========================================================================
# USAGE INSTRUCTIONS
# ===========================================================================

"""
HOW TO USE THIS FILE:

1. Copy the example that matches your needs (Examples 1-6 above)

2. Modify the paths to YOUR Google Drive locations:
   - INPUT_FOLDERS: Point to YOUR image folders
   - OUTPUT_FOLDER: Point to YOUR output folder

3. Paste the configuration into your Colab cell (before running script)

4. Or modify the parameters directly in the script

EXAMPLE WORKFLOW:
    # Cell 1: Mount Google Drive
    from google.colab import drive
    drive.mount('/content/drive')
    
    # Cell 2: Set configuration
    INPUT_FOLDERS = {
        'MyTrail': '/content/drive/MyDrive/images',
    }
    OUTPUT_FOLDER = '/content/drive/MyDrive/results'
    
    # Cell 3: Run script
    exec(open('model_pipeline_claude_and_megadetector.py').read())
"""


# ===========================================================================
# TIPS & BEST PRACTICES
# ===========================================================================

"""
FOLDER ORGANIZATION:

Recommended structure:
    Google Drive/
    ├── TrailCameras/
    │   ├── Site_1/
    │   │   ├── image1.jpg
    │   │   ├── image2.jpg
    │   │   └── ...
    │   ├── Site_2/
    │   └── ...
    └── Results/
        ├── Results_20260211_034520.csv
        ├── Validation_Sheet_1.png
        └── ...

This makes it easy to configure:
    INPUT_FOLDERS = {
        'Site_1': '/content/drive/MyDrive/TrailCameras/Site_1',
        'Site_2': '/content/drive/MyDrive/TrailCameras/Site_2',
    }
    OUTPUT_FOLDER = '/content/drive/MyDrive/Results'

NAMING CONVENTIONS:

Good folder names:
    ✓ 'Carmel_Ridge'
    ✓ 'Conservation_Area_1'
    ✓ 'Field_Study_A'
    ✓ 'site_1_2025'

Avoid:
    ✗ 'My Trail' (spaces)
    ✗ 'camera-trap#1' (special chars)
    ✗ '' (empty name)
    ✗ 'Site' (too generic)

PERFORMANCE OPTIMIZATION:

For faster processing:
    - Use DEVICE = "cuda" (GPU)
    - Increase MAX_PRODUCTION (batch efficiency)
    - Reduce VALIDATION_SHEETS if not needed
    - Use Pipeline Only version (faster)

For more accuracy:
    - Increase VALIDATION_SIZE
    - Increase MD_THRESHOLD (stricter)
    - Use Full Pipeline (Claude)
    - Reduce MAX_PRODUCTION (more careful)

For lower cost:
    - Use Pipeline Only version (free)
    - Reduce MAX_PRODUCTION
    - Use Batch API (if available)

For educational/testing:
    - Start with MAX_PRODUCTION = 50
    - Use VALIDATION_SIZE = 10
    - Test configuration before full run
    - Validate results manually
"""
