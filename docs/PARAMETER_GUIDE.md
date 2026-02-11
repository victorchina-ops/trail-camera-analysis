# Parameter Guide

Complete reference for all configurable parameters in the pipeline scripts.

---

## Quick Reference Table

| Parameter | Type | Default | Range | Full | Pipeline |
|-----------|------|---------|-------|------|----------|
| INPUT_FOLDERS | dict | - | any | ✓ | ✓ |
| OUTPUT_FOLDER | str | - | path | ✓ | ✓ |
| VALIDATION_SIZE | int | 100 | 10-500 | ✓ | ✓ |
| MAX_PRODUCTION | int/None | 1000 | 1-∞ | ✓ | ✓ |
| DEVICE | str | auto | cuda/cpu | ✓ | ✓ |
| MD_THRESHOLD | float | 0.35 | 0.0-1.0 | ✓ | ✓ |
| CLIP_MIN_CONFIDENCE | float | 0.40 | 0.0-1.0 | ✓ | ✓ |
| VALIDATION_SHEETS | bool | True | True/False | ✓ | ✓ |
| SAVE_INTERVAL | int | 50 | 10-500 | ✓ | ✓ |
| CLAUDE_API_KEY_NAME | str | CLAUDE_API_KEY | any | ✓ | - |
| CLAUDE_MODEL | str | haiku-4-5 | various | ✓ | - |
| CLAUDE_MAX_TOKENS | int | 400 | 100-4096 | ✓ | - |

---

## Directory Parameters

### INPUT_FOLDERS

**Type:** Dictionary (Python)

**Purpose:** Specifies where your trail camera images are located

**Syntax:**
```python
INPUT_FOLDERS = {
    'SiteName1': '/path/to/folder1',
    'SiteName2': '/path/to/folder2',
    'SiteName3': '/path/to/folder3',
}
```

**Example:**
```python
INPUT_FOLDERS = {
    'Carmel': '/content/drive/MyDrive/trail_images/carmel',
    'BG_Tomb': '/content/drive/MyDrive/trail_images/bg_tomb',
}
```

**Requirements:**
- ✓ Each key (name) becomes "Site" value in CSV
- ✓ Each value must be valid folder path
- ✓ Folder must exist (script won't create it)
- ✓ Folder must contain images (.jpg, .png, .jpeg)
- ✓ Use absolute paths: `/content/drive/MyDrive/...`

**Finding Correct Path:**
1. Go to Google Drive: https://drive.google.com
2. Navigate to your folder
3. Right-click → "Get link"
4. Link format: `https://drive.google.com/drive/folders/[ID]`
5. Full path: `/content/drive/MyDrive` + remaining path

**Rules:**
- Site names can't have special characters
- Use underscores instead of spaces: `Site_1` not `Site 1`
- Names appear exactly as given in CSV output
- Example names: `Trail_A`, `Conservation_Area`, `Research_Plot_1`

**Edge Cases:**
```python
# Single site
INPUT_FOLDERS = {
    'MyTrail': '/content/drive/MyDrive/images',
}

# Many sites
INPUT_FOLDERS = {
    'Site_' + str(i): f'/content/drive/MyDrive/Site{i}' 
    for i in range(1, 11)  # Creates Site_1 through Site_10
}

# Nested folders
INPUT_FOLDERS = {
    'Region_A': '/content/drive/MyDrive/2025/Region_A/January',
}
```

---

### OUTPUT_FOLDER

**Type:** String (path)

**Purpose:** Where to save results CSV and validation sheets

**Syntax:**
```python
OUTPUT_FOLDER = '/content/drive/MyDrive/results'
```

**Requirements:**
- ✓ Use absolute path: `/content/drive/MyDrive/...`
- ✓ Folder will be created if doesn't exist
- ✓ Must be writable (not in read-only location)

**Output Files:**
Results saved as:
- `Results_Full_Pipeline_[timestamp].csv` (Full version)
- `Results_Pipeline_Only_[timestamp].csv` (Pipeline version)
- `Validation_Sheet_Page1_[timestamp].png` (if enabled)
- `checkpoint_[N]_[timestamp].csv` (auto-saves)

**Example:**
```python
OUTPUT_FOLDER = '/content/drive/MyDrive/TrailCamera/results_2026'
```

---

## Processing Parameters

### VALIDATION_SIZE

**Type:** Integer

**Default:** 100

**Range:** 10-500 (typically)

**Purpose:** How many images to use for validation phase

**Behavior:**
```
Total images: 1000
VALIDATION_SIZE: 100
├─ Validation set: 100 images (generates visual sheets)
└─ Production set: 900 images (batch processed)
```

**Guidelines:**

| Use Case | Value | Reason |
|----------|-------|--------|
| Quick test | 10 | Fast validation |
| Small project | 50 | Good balance |
| Default | 100 | Recommended |
| Large project | 200 | More validation |
| Research | 300+ | High confidence |

**Notes:**
- Images randomly selected for validation
- Validation sheets generated only for this set
- Production set processed after validation
- Larger = more confidence in quality, but slower

**Example:**
```python
VALIDATION_SIZE = 50   # Just want to check quality
VALIDATION_SIZE = 200  # Research - need high confidence
```

---

### MAX_PRODUCTION

**Type:** Integer or None

**Default:** 1000

**Purpose:** Maximum total images to process (validation + production)

**Examples:**

```python
MAX_PRODUCTION = 100        # Process only 100 images total
MAX_PRODUCTION = 1000       # Process 1,000 images max
MAX_PRODUCTION = 5000       # Process 5,000 images
MAX_PRODUCTION = None       # Process ALL images in folders
```

**Behavior:**
```
Images available: 5,000
MAX_PRODUCTION: 1000
Result: Only 1,000 randomly selected images processed
(4,000 skipped)

Images available: 500
MAX_PRODUCTION: 1000
Result: All 500 processed (less than max)
```

**Use Cases:**

| Scenario | Setting | Why |
|----------|---------|-----|
| Testing pipeline | 50 | Quick verification |
| Proof of concept | 100-200 | Check if works on your data |
| Pilot study | 500-1000 | Representative sample |
| Full analysis | None | Process everything |
| Cost control (Full) | 500 | Limit API spending |

**Cost Calculation (Full Pipeline):**
```python
MAX_PRODUCTION = 1000
Cost = 1000 images × $0.02/image = $20

MAX_PRODUCTION = 5000
Cost = 5000 images × $0.02/image = $100

MAX_PRODUCTION = None
Cost = ∞ (depends on actual image count)
```

**Performance:**
```python
VALIDATION_SIZE = 100
MAX_PRODUCTION = 1000
# Total processing time: ~45 min (Full) or ~25 min (Pipeline)

MAX_PRODUCTION = 100
# Total processing time: ~10 min

MAX_PRODUCTION = 10000
# Total processing time: ~7 hours
```

---

### DEVICE

**Type:** String

**Options:** `"cuda"` or `"cpu"`

**Default:** Auto-detect (cuda if available)

**Purpose:** Which processor to use for AI models

**GPU (cuda) vs CPU:**

| Aspect | GPU (cuda) | CPU |
|--------|-----------|-----|
| Speed | 1-2 sec/image | 5-10 sec/image |
| Memory | 2-4 GB | 1-2 GB |
| Availability | Free tier includes | Always available |
| Cost | Included in Colab | Included in Colab |
| Best for | Normal use | Low memory |

**How to Check:**
```python
import torch
print(torch.cuda.is_available())  # True if GPU available
print(torch.cuda.get_device_name(0))  # GPU model name
```

**Examples:**

```python
DEVICE = "cuda"      # Use GPU (faster, recommended)
DEVICE = "cpu"       # Use CPU (slower, less memory)
```

**When to Use GPU:**
- ✓ Running normally
- ✓ Processing 100+ images
- ✓ Time is important

**When to Use CPU:**
- ✓ Out of GPU memory error
- ✓ GPU not available
- ✓ Low-memory Colab environment

**Enable GPU in Colab:**
1. Click "Runtime" (top menu)
2. "Change runtime type"
3. Hardware accelerator: Select "GPU"
4. Restart kernel

---

## Model Parameters

### MD_THRESHOLD

**Type:** Float

**Default:** 0.35

**Range:** 0.0 to 1.0

**Purpose:** MegaDetector confidence threshold for person detection

**What it means:**
```
Threshold = 0.35
├─ Detections with confidence ≥ 0.35: ✓ Keep
└─ Detections with confidence < 0.35: ✗ Discard
```

**Effect on Results:**

| Value | Effect | Use When |
|-------|--------|----------|
| 0.10 | Very lenient (many false positives) | Too permissive |
| 0.25 | Lenient | Crowded scenes |
| **0.35** | **Balanced (default)** | **Most cases** |
| 0.45 | Strict | Need accuracy |
| 0.55 | Very strict | Few false positives needed |

**False Positive Examples:**
```
Threshold too LOW (0.10):
├─ Detects: People ✓
├─ Detects: Shadows (false positive) ✗
└─ Detects: Reflections (false positive) ✗

Threshold too HIGH (0.55):
├─ Detects: People ✓
├─ Misses: Distant people (false negative)
└─ Misses: Obscured people (false negative)
```

**How to Choose:**

1. **Start with default:** 0.35
2. **Test on sample:** Process 10 validation images
3. **Check results:** Look at validation sheets
4. **Adjust if needed:**
   - Too many people in empty images? → Increase to 0.40-0.45
   - Missing people in crowded images? → Decrease to 0.25-0.30
5. **Re-run full analysis**

**Examples:**

```python
MD_THRESHOLD = 0.35    # Default - good for most cases
MD_THRESHOLD = 0.25    # Loose - catch more (some noise)
MD_THRESHOLD = 0.50    # Strict - fewer false positives
```

---

### CLIP_MIN_CONFIDENCE

**Type:** Float

**Default:** 0.40

**Range:** 0.0 to 1.0

**Purpose:** CLIP confidence for adult/child classification

**What it affects:**
- Only affects distinguishing adults from children
- NOT used by Claude (Full Pipeline)
- Only used by MegaDetector + CLIP pipeline

**Effect:**
```
Confidence < threshold: Use default "Adult"
Confidence ≥ threshold: Use CLIP prediction
```

**Guidelines:**

| Value | Effect |
|-------|--------|
| 0.20 | Classify all uncertain cases |
| **0.40** | **Default - good balance** |
| 0.60 | Only classify confident cases |

**Usually keep at default (0.40) unless:**
- Lots of children misclassified as adults → Decrease to 0.30
- Lots of false adult classifications → Increase to 0.50

**Examples:**
```python
CLIP_MIN_CONFIDENCE = 0.40  # Default
CLIP_MIN_CONFIDENCE = 0.50  # Stricter classification
```

---

## Output Parameters

### VALIDATION_SHEETS

**Type:** Boolean

**Default:** True

**Options:** `True` or `False`

**Purpose:** Whether to generate visual validation sheets (PNG images with results overlaid)

**What it creates:**
```
Validation_Sheet_Page1_20260211.png (2-3 MB each)
├─ 10 images per page
├─ Image + detected counts overlaid
└─ One page per 10 images
```

**When to Enable:**
- ✓ Quality control needed
- ✓ Want to see sample results
- ✓ Sharing with team
- ✓ Manual validation

**When to Disable:**
- ✗ Testing (slow down)
- ✗ Large jobs (save storage)
- ✗ Storage limited
- ✗ Don't need visual validation

**Storage Impact:**
```python
VALIDATION_SHEETS = True
# 100 validation images → ~30 MB PNG files

VALIDATION_SHEETS = False
# 100 validation images → no PNG files
```

**Time Impact:**
```
With sheets: +5 minutes for 100 images
Without sheets: Normal speed
```

**Examples:**
```python
VALIDATION_SHEETS = True   # Generate visual validation
VALIDATION_SHEETS = False  # Skip for speed
```

---

### SAVE_INTERVAL

**Type:** Integer

**Default:** 50

**Range:** 10-200 (typically)

**Purpose:** Auto-save checkpoint every N images

**What it does:**
```
Processing 500 images with SAVE_INTERVAL = 50:
├─ Process 1-50 → save checkpoint
├─ Process 51-100 → save checkpoint
├─ Process 101-150 → save checkpoint
└─ ... continue until done
```

**Benefits:**
- ✓ Recover progress if Colab crashes
- ✓ Check partial results mid-processing
- ✓ Stop early if not working well

**Checkpoints saved as:**
```
checkpoint_50_20260211_034520.csv
checkpoint_100_20260211_034520.csv
checkpoint_150_20260211_034520.csv
```

**Choose Value:**

| Images | Interval | Why |
|--------|----------|-----|
| 100 | Disable (20 points) | Too many files |
| 500 | 50 | 10 checkpoints |
| 1000 | 100 | 10 checkpoints |
| 5000 | 200 | 25 checkpoints |

**Examples:**
```python
SAVE_INTERVAL = 50        # Save every 50 images
SAVE_INTERVAL = 100       # Save every 100 images
SAVE_INTERVAL = 200       # Save every 200 images
```

---

## Claude-Specific Parameters (Full Pipeline Only)

### CLAUDE_API_KEY_NAME

**Type:** String

**Default:** `'CLAUDE_API_KEY'`

**Purpose:** Name of the secret in Colab where API key is stored

**Setup:**
1. In Colab, click 🔑 Secrets
2. Add new secret
3. **Name:** `CLAUDE_API_KEY` (must match this parameter)
4. **Value:** Your API key (sk-ant-...)
5. Toggle "Notebook access" ON

**Only change if:**
- You named your secret differently in Colab
- Example: `'MY_ANTHROPIC_KEY'`

**Example:**
```python
CLAUDE_API_KEY_NAME = 'CLAUDE_API_KEY'  # Default
CLAUDE_API_KEY_NAME = 'MY_API_KEY'      # If named differently
```

---

### CLAUDE_MODEL

**Type:** String

**Default:** `'claude-haiku-4-5-20251001'`

**Purpose:** Which Claude model to use

**Available Models:**
```
'claude-haiku-4-5-20251001'      # Fast, cheap (default)
'claude-sonnet-4-5-20250929'     # Balanced
'claude-opus-4-5-20251101'       # Slowest, most accurate
```

**Comparison:**

| Model | Speed | Cost | Accuracy |
|-------|-------|------|----------|
| **Haiku** | Fast | Cheap | Good |
| **Sonnet** | Medium | Medium | Better |
| **Opus** | Slow | Expensive | Best |

**Haiku (default) is best for:**
- Trail camera analysis (sufficient accuracy)
- Cost control
- Speed important

**Only change if:**
- Want highest accuracy (use Sonnet/Opus)
- Haiku giving poor results (unlikely)
- Have specific requirements

**Example:**
```python
CLAUDE_MODEL = 'claude-haiku-4-5-20251001'      # Default
CLAUDE_MODEL = 'claude-sonnet-4-5-20250929'     # Better accuracy
CLAUDE_MODEL = 'claude-opus-4-5-20251101'       # Best accuracy
```

---

### CLAUDE_MAX_TOKENS

**Type:** Integer

**Default:** 400

**Range:** 100-4096

**Purpose:** Maximum output tokens for Claude response

**What it means:**
```
Tokens ≈ words (very roughly)
400 tokens ≈ 300 words

Prompt: "Count people in image"
Response: {"total_people": 10, "adults": 8, ...}
Tokens used: ~50
Max allowed: 400
```

**Don't change unless:**
- Claude response getting cut off (rare)
- Increase to 500-800 if needed
- Decreasing saves cost (not recommended)

**Example:**
```python
CLAUDE_MAX_TOKENS = 400  # Default - sufficient
CLAUDE_MAX_TOKENS = 600  # If response gets truncated
```

---

## Advanced: Creating Parameter Variations

### Test Different Settings

```python
# Run 1: Default settings
VALIDATION_SIZE = 100
MAX_PRODUCTION = 1000
DEVICE = "cuda"
MD_THRESHOLD = 0.35

# Run 2: Conservative (fewer false positives)
VALIDATION_SIZE = 100
MAX_PRODUCTION = 1000
DEVICE = "cuda"
MD_THRESHOLD = 0.45  # Higher threshold

# Run 3: Aggressive (catch more, some noise)
VALIDATION_SIZE = 100
MAX_PRODUCTION = 1000
DEVICE = "cuda"
MD_THRESHOLD = 0.25  # Lower threshold
```

### Automated Parameter Sweep

```python
thresholds = [0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

for threshold in thresholds:
    MD_THRESHOLD = threshold
    # Run analysis for each threshold
    # Compare results
```

---

## Common Parameter Sets

### Quick Test
```python
VALIDATION_SIZE = 10
MAX_PRODUCTION = 50
DEVICE = "cuda"
VALIDATION_SHEETS = False
```

### Production (Normal)
```python
VALIDATION_SIZE = 100
MAX_PRODUCTION = 1000
DEVICE = "cuda"
VALIDATION_SHEETS = True
SAVE_INTERVAL = 50
```

### Large Scale
```python
VALIDATION_SIZE = 200
MAX_PRODUCTION = None  # All images
DEVICE = "cuda"
VALIDATION_SHEETS = True
SAVE_INTERVAL = 100
```

### Research (High Quality)
```python
VALIDATION_SIZE = 300
MAX_PRODUCTION = 5000
DEVICE = "cuda"
MD_THRESHOLD = 0.40  # Stricter
VALIDATION_SHEETS = True
SAVE_INTERVAL = 100
```

### Budget Conscious (Pipeline Only)
```python
VALIDATION_SIZE = 50
MAX_PRODUCTION = 2000
DEVICE = "cuda"
VALIDATION_SHEETS = False  # Save storage
SAVE_INTERVAL = 100
```

---

## Troubleshooting Parameters

### "Too many false detections"
→ Increase `MD_THRESHOLD` (0.40 or higher)

### "Missing people in images"
→ Decrease `MD_THRESHOLD` (0.25 or lower)

### "Slow processing"
→ Set `DEVICE = "cuda"` or reduce `MAX_PRODUCTION`

### "Out of memory"
→ Set `DEVICE = "cpu"` or reduce `MAX_PRODUCTION`

### "Cost too high"
→ Use `Pipeline Only` or reduce `MAX_PRODUCTION`

### "Validation sheets too large"
→ Set `VALIDATION_SHEETS = False` or reduce `VALIDATION_SIZE`

---

## Summary

**Minimum Required:**
```python
INPUT_FOLDERS = {'Site1': '/path/to/images'}
OUTPUT_FOLDER = '/path/to/output'
```

**Recommended:**
```python
INPUT_FOLDERS = {
    'Site1': '/content/drive/MyDrive/images/site1',
    'Site2': '/content/drive/MyDrive/images/site2',
}
OUTPUT_FOLDER = '/content/drive/MyDrive/results'
VALIDATION_SIZE = 100
MAX_PRODUCTION = 1000
DEVICE = "cuda"
VALIDATION_SHEETS = True
```

**For Cost Control:**
```python
MAX_PRODUCTION = 500  # Process fewer images
# or use Pipeline Only (free)
```

**For Speed:**
```python
DEVICE = "cuda"
VALIDATION_SHEETS = False
SAVE_INTERVAL = 100
```

---

See [example_config.py](../example_config.py) for more examples.
