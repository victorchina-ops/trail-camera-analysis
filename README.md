# Trail Camera Analysis Pipeline

Automated detection and classification of humans and activities in trail camera images using two different methodologies.

**Process trail camera images to extract:**
- Human counts (total, adults, children)
- Activities (bicycles, dogs, backpacks)
- Vehicles (cars, motorcycles, ATVs)
- Equipment (strollers, wheelchairs)

## 🚀 Quick Start

### Two Versions Available

| Version | Method | API Required | Cost | Speed | Accuracy |
|---------|--------|--------------|------|-------|----------|
| **Full Pipeline** | Claude MLLM + MegaDetector | ✅ Claude API | ~$0.02/image | Fast | Highest |
| **Pipeline Only** | MegaDetector + CLIP | ❌ None | Free | Fast | Very Good |

### Choose Your Version

**Use Full Pipeline if:**
- You want maximum accuracy
- You have access to Claude API
- Processing cost is not a concern
- You need comprehensive activity detection

**Use Pipeline Only if:**
- You want free, open-source solution
- No API keys required
- Speed is prioritized
- Sufficient accuracy for your use case

## 📋 Requirements

### Both Versions
- Google Colab account (free)
- Google Drive account (free)
- GPU access in Colab (free tier available)

### Full Pipeline Only
- Claude API key (~$0.02 per image)
  - Get key: https://console.anthropic.com
  - Free trial credits available
  - No credit card required to start

## 🎯 Getting Started

### Step 1: Prepare Your Images

1. Upload trail camera images to Google Drive
2. Create folder structure like:
   ```
   My Drive/
   └── trail_camera_images/
       ├── site_1/
       │   ├── image_1.jpg
       │   ├── image_2.jpg
       │   └── ...
       └── site_2/
           ├── image_1.jpg
           └── ...
   ```

### Step 2: Choose Your Method

**Option A: Full Pipeline (Claude + MegaDetector)**
- Most accurate for all activity types
- See: [`notebooks/Trail_Camera_Analysis_Full.ipynb`](notebooks/Trail_Camera_Analysis_Full.ipynb)
- Requires Claude API key

**Option B: Pipeline Only (MegaDetector + CLIP)**
- Free and open-source
- Great for human detection and demographics
- See: [`notebooks/Trail_Camera_Analysis_Pipeline_Only.ipynb`](notebooks/Trail_Camera_Analysis_Pipeline_Only.ipynb)
- No API key needed

### Step 3: Analyze Results (Optional)

**Option C: Compare Results**
- Analyze outputs from both methods side-by-side
- Generate comparison tables and visualizations
- Create spider/radar plots for site characteristics
- See: [`notebooks/Trail_Camera_Analysis_Comparison.ipynb`](notebooks/Trail_Camera_Analysis_Comparison.ipynb)
- Use after running Step 1 or 2

### Step 4: Run in Google Colab

1. Open the notebook (click link above)
2. Click "Open in Colab"
3. Follow the setup cells
4. Configure your folders and parameters
5. Run the analysis
6. Download results from Google Drive

## 📁 Repository Structure

```
trail-camera-analysis/
├── README.md                          (this file)
├── LICENSE                            (MIT)
├── METHOD_COMPARISON.md               (detailed method comparison)
├── CLAUDE_API_SETUP.md                (Claude API authentication guide)
├── code/
│   ├── model_pipeline_claude_and_megadetector.py
│   └── model_pipeline_megadetector_only.py
├── notebooks/
│   ├── Trail_Camera_Analysis_Full.ipynb
│   ├── Trail_Camera_Analysis_Pipeline_Only.ipynb
│   └── Trail_Camera_Analysis_Comparison.ipynb
└── docs/
    ├── SETUP_INSTRUCTIONS.md
    ├── PARAMETER_GUIDE.md
    └── example_config.py
```

## 🔑 Claude API Setup (Full Pipeline Only)

1. **Get API Key:**
   - Visit: https://console.anthropic.com
   - Sign up (free account)
   - Create API key (free trial includes credits)

2. **Add to Colab:**
   - In Colab, click "🔑 Secrets" on left sidebar
   - Click "Add new secret"
   - Name: `CLAUDE_API_KEY`
   - Value: `sk-ant-...` (your API key)
   - Enable "Notebook access"

3. **That's it!** Script automatically authenticates

See detailed guide: [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md)

## ⚙️ Configuration

Both scripts use parameter configuration at the top:

```python
# Input/Output directories
INPUT_FOLDERS = {
    'SITE_1': '/content/drive/MyDrive/your_folder_1',
    'SITE_2': '/content/drive/MyDrive/your_folder_2',
}
OUTPUT_FOLDER = '/content/drive/MyDrive/results'

# Processing settings
VALIDATION_SIZE = 100
MAX_PRODUCTION = 1000
DEVICE = "cuda"  # or "cpu"

# Model parameters
MD_THRESHOLD = 0.35
CLIP_MIN_CONFIDENCE = 0.40
```

See detailed guide: [PARAMETER_GUIDE.md](docs/PARAMETER_GUIDE.md)

## 📊 Output Files

Results are saved as **CSV files** containing:

**Full Pipeline Output:**
```csv
Site,Date,Time,Filename,
Claude_Total,Claude_Adult,Claude_Child,Claude_Bike,Claude_Dog,Claude_Stroller,Claude_Wheelchair,Claude_Backpack,Claude_Car,Claude_Motorcycle,Claude_ATV,
Pipeline_Total,Pipeline_Adult,Pipeline_Child
```

**Pipeline Only Output:**
```csv
Site,Date,Time,Filename,
Pipeline_Total,Pipeline_Adult,Pipeline_Child
```

Plus:
- **Validation sheets** (visual PNG with overlaid results)
- **Checkpoints** (auto-saved every 50 images)
- **Summary statistics** (printed to console)

## 📈 Analysis & Comparison

After running the pipelines, use the **Comparison notebook** to:
- Compare method accuracy and agreement
- Generate site characteristic tables
- Create spider plots for multi-variable comparison
- Analyze detection sensitivity by crowd size
- Export publication-ready figures and tables

See: [Trail_Camera_Analysis_Comparison.ipynb](notebooks/Trail_Camera_Analysis_Comparison.ipynb)

## 🔬 Method Comparison

| Aspect | Claude MLLM | MegaDetector+CLIP |
|--------|-------------|------------------|
| **Human Detection** | Excellent | Excellent |
| **Demographics** | Adult/Child/Gender | Adult/Child only |
| **Activities** | Bikes, Dogs, Backpacks, Vehicles | People only |
| **Speed** | ~1 sec/image | ~0.5 sec/image |
| **Cost** | ~$0.015/image | Free |
| **API Required** | Yes | No |
| **Accuracy** | Very High | High |

See full comparison: [METHOD_COMPARISON.md](METHOD_COMPARISON.md)

## 📈 Example Results

After processing 1,000 images:

```
CLAUDE METHOD:
  Total humans: 3,050 (3.05/image avg)
  Vehicles detected: 350 (cars, motorcycles, ATVs)
  Activity gear: 450 backpacks, 280 bikes

PIPELINE METHOD:
  Total humans: 3,010 (3.01/image avg)
  Method agreement: r=0.890 (very strong)
```

## 🎓 How It Works

### Full Pipeline

```
Trail Camera Image
    ↓
    ├─→ Claude MLLM Analysis
    │   └─→ Detects: humans, activities, vehicles
    │
    └─→ MegaDetector v5a
        ├─→ Detects: person bounding boxes
        └─→ CLIP Classification
            └─→ Adult/Child demographics
    
    ↓ (Comparison & Validation)
    
CSV Results + Validation Sheets
```

### Pipeline Only

```
Trail Camera Image
    ↓
    └─→ MegaDetector v5a
        ├─→ Detects: person bounding boxes
        └─→ CLIP Classification
            └─→ Adult/Child demographics
    
    ↓
    
CSV Results + Validation Sheets
```

## 🐛 Troubleshooting

### "No module named 'anthropic'"
- **Full Pipeline:** Run setup cells in notebook (auto-installs)
- **Pipeline Only:** Should not occur (not needed)

### "API key not found"
- Full Pipeline only
- Ensure you added `CLAUDE_API_KEY` to Colab Secrets
- Restart kernel and re-run

### "Folder not found"
- Check that folder path is correct
- Ensure you mounted Google Drive
- Use absolute paths: `/content/drive/MyDrive/...`

### "Out of memory"
- Reduce `MAX_PRODUCTION` (process fewer images)
- Use `DEVICE = "cpu"` (slower but uses less VRAM)
- Process in smaller batches

### GPU not available
- Free Colab sometimes gives CPU only
- Use Pipeline Only version (faster)
- Or request GPU in Colab runtime settings

### Comparison notebook results
- Results save to your RESULTS_FOLDER in Google Drive
- Check notebook output for saved file paths
- Download tables and figures directly from Google Drive

See detailed troubleshooting: [SETUP_INSTRUCTIONS.md](docs/SETUP_INSTRUCTIONS.md)

## 📝 Citation

If you use this code in research, please cite:

```bibtex
@software{trail_camera_analysis,
  title={Trail Camera Analysis: Automated Detection Pipeline},
  author={Victor China},
  year={2026},
  url={https://github.com/victorchina-ops/trail-camera-analysis}
}
```

## 📚 References

- **Claude API:** https://docs.anthropic.com
- **MegaDetector:** https://github.com/ecologize/CameraTraps
- **CLIP:** https://github.com/openai/CLIP
- **YOLOv5:** https://github.com/ultralytics/yolov5

## 💬 Contributing

Found a bug? Want to improve the code?
- Create an issue
- Submit a pull request
- Share results and feedback

## ⚖️ License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is provided as-is for trail camera image analysis. Results depend on image quality, lighting, and scene complexity. Always validate results manually, especially for critical applications like wildlife monitoring or property security.

---

**Questions?** See the detailed documentation:
- Setup: [SETUP_INSTRUCTIONS.md](docs/SETUP_INSTRUCTIONS.md)
- Parameters: [PARAMETER_GUIDE.md](docs/PARAMETER_GUIDE.md)
- Methods: [METHOD_COMPARISON.md](METHOD_COMPARISON.md)
- Claude: [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md)

**Ready to start?** Open a notebook:
- **Full Pipeline:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/victorchina-ops/trail-camera-analysis/blob/main/notebooks/Trail_Camera_Analysis_Full.ipynb)
- **Pipeline Only:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/victorchina-ops/trail-camera-analysis/blob/main/notebooks/Trail_Camera_Analysis_Pipeline_Only.ipynb)
- **Compare Results:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/victorchina-ops/trail-camera-analysis/blob/main/notebooks/Trail_Camera_Analysis_Comparison.ipynb)
