# Setup Instructions

Complete step-by-step guide to set up and run the trail camera analysis pipeline.

**⏱️ Total time**: 15-20 minutes  
**📊 Skill level**: Beginner (no coding required)

---

## Overview

The pipeline runs entirely in **Google Colab** (free cloud notebook environment). You need:
1. ✅ Google account (you likely have this)
2. ✅ Google Drive account (free, same as Google account)
3. ✅ Trail camera images
4. ✅ Claude API key (for Full Pipeline only)

---

## Part 1: Prepare Your Images

### Step 1a: Organize Images in Google Drive

1. Go to: https://drive.google.com
2. Create a folder for your images:
   - Right-click → "New Folder"
   - Name: "trail_camera_images"
   - Inside create subfolders for each site:
     - "site_1" 
     - "site_2"
     - etc.

### Step 1b: Upload Images

1. For each site folder:
   - Click the folder
   - Click "Upload" or drag-drop images
   - Wait for upload to complete

2. Supported formats:
   - ✓ JPG, JPEG
   - ✓ PNG
   - ✗ TIFF, RAW (convert first)

3. Folder structure should look like:
   ```
   Google Drive/
   └── trail_camera_images/
       ├── site_1/
       │   ├── image_001.jpg
       │   ├── image_002.jpg
       │   └── ...
       └── site_2/
           └── ...
   ```

---

## Part 2: Choose Your Method

### Pipeline Only (Recommended for beginners)

**Good for:** Free, no API key, simple setup

1. Skip Claude API setup (below)
2. Go to Step 3 directly
3. Use notebook: `Trail_Camera_Analysis_Pipeline_Only.ipynb`

### Full Pipeline (Requires API key)

**Good for:** Activity detection, highest accuracy

1. Do Claude API setup (Step 2)
2. Then proceed to Step 3
3. Use notebook: `Trail_Camera_Analysis_Full.ipynb`

---

## Part 3: Claude API Setup (Full Pipeline Only)

### ⏭️ If using Pipeline Only: SKIP this section

### Step 2a: Get API Key (5 minutes)

1. Go to: https://console.anthropic.com
2. Click "Sign Up"
3. Create account with email
4. Verify email
5. Click "API Keys" on left sidebar
6. Click "Create Key"
7. Name it: "Colab Trail Camera"
8. **COPY THE KEY** (click copy icon)
   - Format: `sk-ant-abc123...`
   - Keep it safe!

See detailed guide: [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md)

### Step 2b: Add to Colab (2 minutes)

1. Open Colab notebook (see Step 3)
2. Left sidebar → Click 🔑 **Secrets**
3. Click "Add new secret"
4. **Name:** `CLAUDE_API_KEY`
5. **Value:** Paste your API key
6. Toggle **"Notebook access"** to ON
7. Click "Save"

---

## Part 3: Open & Run Colab Notebook

### Step 3a: Choose Notebook

**Option A: Pipeline Only (No API key)**
- Open: https://colab.research.google.com/github/yourusername/trail-camera-analysis/blob/main/notebooks/Trail_Camera_Analysis_Pipeline_Only.ipynb

**Option B: Full Pipeline (With Claude)**
- Open: https://colab.research.google.com/github/yourusername/trail-camera-analysis/blob/main/notebooks/Trail_Camera_Analysis_Full.ipynb

(Or download notebook and open in Colab)

### Step 3b: Copy to Your Drive

1. In Colab, click "File" (top menu)
2. Click "Save a copy in Drive"
3. Now you have your own copy
4. Can edit parameters without affecting original

### Step 3c: Mount Google Drive

1. Find cell with:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

2. Click ▶️ (play button) to run cell
3. Click auth link when prompted
4. Select your Google account
5. Click "Allow"
6. You'll see: "Mounted at /content/drive" ✓

---

## Part 4: Configure Parameters

### Step 4a: Set Input Folders

Find cell with configuration:

```python
INPUT_FOLDERS = {
    'SITE_1': '/content/drive/MyDrive/your_folder_1',
    'SITE_2': '/content/drive/MyDrive/your_folder_2',
}
```

Replace with YOUR paths. Example:

```python
INPUT_FOLDERS = {
    'Carmel': '/content/drive/MyDrive/trail_camera_images/site_1',
    'BG_Tomb': '/content/drive/MyDrive/trail_camera_images/site_2',
}
```

**How to find correct path:**
1. Go to Google Drive: https://drive.google.com
2. Navigate to your image folder
3. Right-click → "Get link"
4. Link shows: `/MyDrive/trail_camera_images/site_1`
5. Full path: `/content/drive` + link path

### Step 4b: Set Output Folder

```python
OUTPUT_FOLDER = '/content/drive/MyDrive/trail_camera_results'
```

This is where results CSV files save. Can create new folder.

### Step 4c: Optional: Adjust Settings

Defaults are fine, but you can adjust:

```python
VALIDATION_SIZE = 100        # Number of validation images
MAX_PRODUCTION = 1000        # Max total images (None = all)
DEVICE = "cuda"              # Use GPU (faster)
VALIDATION_SHEETS = True     # Generate visual sheets
```

For quick test, use:
```python
VALIDATION_SIZE = 10
MAX_PRODUCTION = 50
```

See [PARAMETER_GUIDE.md](docs/PARAMETER_GUIDE.md) for details.

---

## Part 5: Run Analysis

### Step 5a: Install Dependencies

Run cell that says:

```python
# 🛠️ Installing dependencies...
# (or similar)
```

Wait for completion (1-2 minutes).

Should show:
```
✓ Dependencies installed
✓ Device: CUDA
```

### Step 5b: Run Main Analysis

Scroll to cell with:

```python
if __name__ == "__main__":
    print("INITIALIZING MODELS")
    # ... rest of analysis
```

Click ▶️ to start.

### Step 5c: Monitor Progress

Script shows real-time progress:

```
[  1/100] image_001.jpg ...................... ✓
[  2/100] image_002.jpg ...................... ✓
[  3/100] image_003.jpg ...................... ✓
```

### Step 5d: Wait for Completion

Full Pipeline: ~45 min for 1,000 images
Pipeline Only: ~25 min for 1,000 images

Colab can stay running. Don't close browser.

---

## Part 6: Get Results

### Step 6a: Results Saved

When complete, you'll see:

```
✅ COMPLETE!
✓ Results saved: Results_Full_Pipeline_20260211.csv
✓ Total images processed: 1,000
```

### Step 6b: Download Results

1. Go to Google Drive: https://drive.google.com
2. Navigate to OUTPUT_FOLDER you set
3. Right-click CSV file → Download
4. Also download validation sheets (PNG files) if generated

### Step 6c: Verify Results

Open CSV file in Excel/Google Sheets:

**Full Pipeline columns:**
- Site, Date, Time, Filename
- Claude_Total, Claude_Adult, Claude_Child
- Claude_Bike, Claude_Dog, Claude_Backpack, Claude_Car, etc.
- Pipeline_Total, Pipeline_Adult, Pipeline_Child

**Pipeline Only columns:**
- Site, Date, Time, Filename
- Pipeline_Total, Pipeline_Adult, Pipeline_Child

---

## Troubleshooting

### Problem: "Folder not found"

**Error:**
```
⚠ Folder not found: /content/drive/MyDrive/...
❌ No images found
```

**Solution:**
1. Check folder path is correct
2. Verify folder exists in Google Drive
3. Make sure images are inside (not empty)
4. Use exact path from "Get link"
5. Restart kernel and try again

### Problem: "No module named 'X'"

**Error:**
```
ModuleNotFoundError: No module named 'anthropic'
```

**Solution:**
1. Run the "Install dependencies" cell
2. Wait for completion
3. Restart kernel: Runtime → Restart
4. Run again

### Problem: "API key not found"

**Error:**
```
⚠ Claude API key not found in Colab secrets
```

**Solution (Full Pipeline only):**
1. Left sidebar → 🔑 Secrets
2. Click "Add new secret"
3. Name: `CLAUDE_API_KEY` (exact!)
4. Value: `sk-ant-...` (your API key)
5. Toggle "Notebook access" ON
6. Save
7. Restart kernel

### Problem: "GPU not available"

**Error:**
```
❌ CUDA device not available
```

**Solution:**
1. Click "Runtime" → "Change runtime type"
2. GPU → Select GPU
3. Click Save
4. Restart kernel and run again
5. Or use `DEVICE = "cpu"` (slower)

### Problem: "Timeout / Kernel died"

**Error:**
```
The kernel appears to have died
```

**Cause:**
- Out of memory
- Took too long
- Colab session limit

**Solution:**
1. Click "Runtime" → "Restart session"
2. Reduce `MAX_PRODUCTION` to smaller number
3. Run with fewer images first
4. Use `DEVICE = "cpu"` to save memory

### Problem: "Validation sheets are huge"

**Error:**
- Validation sheets are 50+ MB
- Slow to download

**Solution:**
```python
VALIDATION_SHEETS = False  # Disable sheets
# or
VALIDATION_SIZE = 10        # Generate fewer
```

### Problem: "Results CSV is empty"

**Error:**
```
Results_*.csv exists but has no data
```

**Solution:**
1. Check INPUT_FOLDERS paths
2. Verify images are in folders
3. Check image formats (.jpg, .png)
4. Run with smaller sample first
5. Check Colab console for errors

### Problem: "Claude API costs too much"

**Error:**
- Bill higher than expected
- Running out of credits

**Solution:**
1. Switch to Pipeline Only (free)
2. Use Batch API (cheaper)
3. Reduce image resolution before processing
4. Process smaller batches
5. Set spending limit in API console

---

## Quick Start Checklist

- [ ] Created Google Drive account (free)
- [ ] Created folder structure for images
- [ ] Uploaded trail camera images
- [ ] (Full Pipeline) Got Claude API key
- [ ] (Full Pipeline) Added API key to Colab Secrets
- [ ] Opened Colab notebook
- [ ] Mounted Google Drive
- [ ] Set INPUT_FOLDERS path
- [ ] Set OUTPUT_FOLDER path
- [ ] Ran setup/install cells
- [ ] Ran main analysis cell
- [ ] Downloaded results CSV
- [ ] Verified results in Excel/Sheets

---

## Performance Tips

### Speed Up Processing

1. Use GPU: `DEVICE = "cuda"`
2. Use Pipeline Only (free version)
3. Reduce image size before upload
4. Increase `MAX_PRODUCTION` (batch efficiency)

### Reduce Costs (Full Pipeline)

1. Switch to Pipeline Only (free)
2. Process smaller sample first (100 images)
3. Use Batch API (50% discount)
4. Compress images before sending

### Better Quality

1. Use Full Pipeline (Claude)
2. Increase VALIDATION_SIZE
3. Review validation sheets
4. Manually check uncertain cases

---

## Next Steps

After getting results:

1. **Analyze Results**
   - Open CSV in Excel/Sheets
   - Calculate summary statistics
   - Plot trends over time

2. **Validate Accuracy**
   - Review validation sheets
   - Manually check sample images
   - Estimate accuracy for your data

3. **Scale Up**
   - If satisfied, process all images
   - Set `MAX_PRODUCTION = None`
   - Run on full dataset

4. **Use in Research**
   - Export to analysis software
   - Combine with other data
   - Write up methods section

5. **Share Code**
   - Save Colab notebook
   - Share link with collaborators
   - Document your configuration

---

## Support & Help

### Documentation

- README: [README.md](README.md)
- Method Comparison: [METHOD_COMPARISON.md](METHOD_COMPARISON.md)
- Parameter Guide: [PARAMETER_GUIDE.md](docs/PARAMETER_GUIDE.md)
- Claude Setup: [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md)

### Community

- GitHub Issues: Report bugs
- GitHub Discussions: Ask questions
- Stack Overflow: Tag `trail-camera` for general help

### Anthropic Support

- Docs: https://docs.anthropic.com
- Email: support@anthropic.com

---

**Ready to start?** Open a notebook:
- **Pipeline Only** (free): [Trail_Camera_Analysis_Pipeline_Only.ipynb](../notebooks/Trail_Camera_Analysis_Pipeline_Only.ipynb)
- **Full Pipeline** (Claude): [Trail_Camera_Analysis_Full.ipynb](../notebooks/Trail_Camera_Analysis_Full.ipynb)

**Estimated time to first results**: 20-30 minutes ⏱️
