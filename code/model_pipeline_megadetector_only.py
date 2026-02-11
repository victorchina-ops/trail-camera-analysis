# -*- coding: utf-8 -*-
"""Trail Camera Analysis: Pipeline Only (MegaDetector+CLIP)

This script processes trail camera images with MegaDetector v5a + CLIP only.
NO Claude API required - completely free and open-source!

Lighter weight and faster than the full pipeline version.

Parameterized for easy configuration. Run in Google Colab with your own Google Drive.

Usage:
    1. Set parameters in CONFIGURATION section below
    2. Mount Google Drive
    3. Run script
"""

import os
import sys
import subprocess
import warnings
import json
import random
from datetime import datetime
from PIL import Image, ExifTags
import pandas as pd
import matplotlib.pyplot as plt
import requests
import torch

# ===========================================================================
# CONFIGURATION - SET YOUR PARAMETERS HERE
# ===========================================================================

# Input/Output directories (relative to Google Drive root or absolute paths)
INPUT_FOLDERS = {
    'SITE_1': '/content/drive/MyDrive/your_images_folder_1',
    'SITE_2': '/content/drive/MyDrive/your_images_folder_2',
    # Add more sites as needed
}

OUTPUT_FOLDER = '/content/drive/MyDrive/trail_camera_results'

# Processing settings
VALIDATION_SIZE = 100              # Number of images for validation phase
MAX_PRODUCTION = 1000              # Max images to process (None = all)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Model parameters
MD_THRESHOLD = 0.35                # MegaDetector confidence threshold
CLIP_MIN_CONFIDENCE = 0.40         # CLIP classification confidence

# Output settings
VALIDATION_SHEETS = True           # Generate visual validation sheets
SAVE_INTERVAL = 50                 # Save checkpoint every N images
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# ===========================================================================
# SETUP & INITIALIZATION
# ===========================================================================

print("="*70)
print("TRAIL CAMERA ANALYSIS - PIPELINE ONLY (MegaDetector+CLIP)")
print("="*70)
print("✓ No API key required - completely free!")

# Create output directory
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
print(f"✓ Output directory: {OUTPUT_FOLDER}")

# Install required packages
print("\n🛠️ Installing dependencies...")
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])

packages = ["urllib3<2.0.0", "ultralytics", "transformers", "requests"]
for pkg in packages:
    try:
        __import__(pkg.split('[')[0].replace('-', '_'))
    except ImportError:
        print(f"  Installing {pkg}...")
        install(pkg)

from transformers import CLIPProcessor, CLIPModel

warnings.filterwarnings("ignore")
print(f"✓ Dependencies installed")
print(f"✓ Device: {DEVICE.upper()}")

# ===========================================================================
# UTILITY FUNCTIONS
# ===========================================================================

def get_exif_data(image_path):
    """Extract date and time from image EXIF data."""
    try:
        img = Image.open(image_path)
        exif = img._getexif()
        if not exif:
            return "Unknown", "Unknown"
        
        for tag, value in ExifTags.TAGS.items():
            if value == 'DateTimeOriginal':
                if tag in exif:
                    dt = str(exif[tag]).split(' ')
                    if len(dt) == 2:
                        return dt[0].replace(':', '/'), dt[1]
    except:
        pass
    
    return "Unknown", "Unknown"

# ===========================================================================
# MEGADETECTOR + CLIP PIPELINE CLASS
# ===========================================================================

class PipelineModel:
    """MegaDetector v5a + CLIP for activity detection."""
    
    def __init__(self):
        """Initialize MegaDetector and CLIP models."""
        print("Loading MegaDetector...")
        self.weights = "md_v5a.0.0.pt"
        
        # Download weights if needed
        if not os.path.exists(self.weights):
            print("  Downloading MegaDetector weights (~330MB)...")
            r = requests.get(
                "https://github.com/ecologize/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt"
            )
            with open(self.weights, 'wb') as f:
                f.write(r.content)
        
        # Load YOLOv5 with MegaDetector weights
        self.md = torch.hub.load(
            'ultralytics/yolov5', 'custom',
            path=self.weights, trust_repo=True
        )
        self.md.conf = MD_THRESHOLD
        
        # Load CLIP for classification
        print("Loading CLIP model...")
        self.clip_model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32"
        ).to(DEVICE)
        self.clip_proc = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32"
        )
        
        self.labels = ["a photo of a child", "a photo of a man", "a photo of a woman"]
        self.label_map = {0: "Child", 1: "Adult", 2: "Adult"}
        
        print("✓ Pipeline models loaded")
    
    def analyze(self, image_path):
        """Analyze image with MegaDetector + CLIP."""
        try:
            # Run MegaDetector
            results = self.md(image_path)
            df = results.pandas().xyxy[0]
            
            # Filter for people (class 1)
            person_boxes = df[df['class'] == 1][
                ['xmin', 'ymin', 'xmax', 'ymax']
            ].values.tolist()
            
            if len(person_boxes) == 0:
                return {
                    'Total': 0,
                    'Adult': 0,
                    'Child': 0
                }
            
            # Classify with CLIP
            counts = {'Adult': 0, 'Child': 0}
            img = Image.open(image_path).convert("RGB")
            
            for box in person_boxes:
                x1, y1, x2, y2 = map(int, box)
                crop = img.crop((
                    max(0, x1), max(0, y1),
                    min(img.width, x2), min(img.height, y2)
                ))
                
                inputs = self.clip_proc(
                    text=self.labels,
                    images=crop,
                    return_tensors="pt",
                    padding=True
                ).to(DEVICE)
                
                with torch.no_grad():
                    probs = self.clip_model(**inputs).logits_per_image.softmax(dim=1)
                
                label = self.label_map[probs.cpu().numpy()[0].argmax()]
                counts[label] += 1
            
            return {
                'Total': len(person_boxes),
                'Adult': counts['Adult'],
                'Child': counts['Child']
            }
        
        except Exception as e:
            print(f"   ❌ Pipeline error: {e}")
            return {
                'Total': 0,
                'Adult': 0,
                'Child': 0
            }

# ===========================================================================
# MAIN PROCESSING
# ===========================================================================

def process_image(item, pipeline_model):
    """Process single image with pipeline."""
    # Extract metadata
    date, time = get_exif_data(item['path'])
    
    # Run pipeline
    result = pipeline_model.analyze(item['path'])
    
    # Compile results
    row = {
        'Site': item['site'],
        'Date': date,
        'Time': time,
        'Filename': item['name'],
        
        # Pipeline outputs
        'Pipeline_Total': result['Total'],
        'Pipeline_Adult': result['Adult'],
        'Pipeline_Child': result['Child'],
    }
    
    return row, item['path']

def generate_validation_sheets(results, timestamp):
    """Generate visual validation sheets with results."""
    if not VALIDATION_SHEETS or not results:
        return
    
    print(f"\n📊 Generating validation sheets...")
    
    # Process in chunks of 10
    chunks = [results[i:i+10] for i in range(0, len(results), 10)]
    
    for page_num, chunk in enumerate(chunks):
        fig, axes = plt.subplots(5, 2, figsize=(14, 18))
        axes = axes.flatten()
        fig.suptitle(f"Validation Batch {page_num+1} of {len(chunks)}", fontsize=16, fontweight='bold')
        
        for idx, (res, img_path) in enumerate(chunk):
            ax = axes[idx]
            try:
                ax.imshow(Image.open(img_path))
                
                # Create label
                label = (
                    f"{res['Filename']} | {res['Date']} {res['Time']}\n"
                    f"PIPELINE: People:{res['Pipeline_Total']} "
                    f"(Adults:{res['Pipeline_Adult']} Children:{res['Pipeline_Child']})"
                )
                
                ax.set_title(label, fontsize=9, backgroundcolor='lightyellow', pad=5)
            except Exception as e:
                ax.text(0.5, 0.5, f"Error loading image:\n{str(e)}", 
                       ha='center', va='center', transform=ax.transAxes)
            
            ax.axis('off')
        
        # Hide unused subplots
        for j in range(len(chunk), 10):
            axes[j].axis('off')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        output_path = os.path.join(
            OUTPUT_FOLDER,
            f"Validation_Sheet_Page{page_num+1}_{timestamp}.png"
        )
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Validation sheet {page_num+1}/{len(chunks)} saved")

# ===========================================================================
# EXECUTION
# ===========================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INITIALIZING MODELS")
    print("="*70)
    
    # Initialize pipeline
    pipeline = PipelineModel()
    
    # Gather image files
    print("\n" + "="*70)
    print("GATHERING IMAGE FILES")
    print("="*70)
    
    all_files = []
    for site_name, folder_path in INPUT_FOLDERS.items():
        if os.path.exists(folder_path):
            images = [
                f for f in os.listdir(folder_path)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ]
            print(f"✓ Found {len(images)} images in '{site_name}'")
            
            for img in images:
                all_files.append({
                    'site': site_name,
                    'name': img,
                    'path': os.path.join(folder_path, img)
                })
        else:
            print(f"⚠ Folder not found: {folder_path}")
    
    if not all_files:
        print("❌ No images found. Exiting.")
        sys.exit(1)
    
    # Shuffle and limit
    random.shuffle(all_files)
    if MAX_PRODUCTION:
        all_files = all_files[:MAX_PRODUCTION]
    
    print(f"\n✓ Total images to process: {len(all_files)}")
    
    # Split into validation and production
    validation_set = all_files[:VALIDATION_SIZE]
    production_set = all_files[VALIDATION_SIZE:]
    
    all_results = []
    validation_results = []
    
    # Process validation set
    print("\n" + "="*70)
    print(f"PHASE 1: VALIDATION ({len(validation_set)} images)")
    print("="*70)
    
    for i, item in enumerate(validation_set, 1):
        print(f"[{i:4d}/{len(validation_set)}] {item['name']:<40}", end=" ", flush=True)
        
        try:
            row, img_path = process_image(item, pipeline)
            all_results.append(row)
            validation_results.append((row, img_path))
            print("✓")
        except Exception as e:
            print(f"✗ {e}")
    
    # Generate validation sheets
    if VALIDATION_SHEETS:
        generate_validation_sheets(validation_results, TIMESTAMP)
    
    # Process production set
    if production_set:
        print("\n" + "="*70)
        print(f"PHASE 2: PRODUCTION ({len(production_set)} images)")
        print("="*70)
        
        for i, item in enumerate(production_set, 1):
            print(f"[{i:4d}/{len(production_set)}] {item['name']:<40}", end=" ", flush=True)
            
            try:
                row, _ = process_image(item, pipeline)
                all_results.append(row)
                print("✓")
                
                # Save checkpoint
                if i % SAVE_INTERVAL == 0:
                    checkpoint_path = os.path.join(
                        OUTPUT_FOLDER,
                        f"checkpoint_{i}_{TIMESTAMP}.csv"
                    )
                    pd.DataFrame(all_results).to_csv(checkpoint_path, index=False)
                    print(f"  💾 Checkpoint saved")
            
            except Exception as e:
                print(f"✗ {e}")
    
    # Save final results
    print("\n" + "="*70)
    print("SAVING RESULTS")
    print("="*70)
    
    output_path = os.path.join(OUTPUT_FOLDER, f"Results_Pipeline_Only_{TIMESTAMP}.csv")
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✓ Results saved: {output_path}")
    print(f"✓ Total images processed: {len(all_results)}")
    print(f"✓ Output folder: {OUTPUT_FOLDER}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
    print("\nPipeline Method (MegaDetector + CLIP):")
    print(f"  Total humans detected: {results_df['Pipeline_Total'].sum()}")
    print(f"  Average per image: {results_df['Pipeline_Total'].mean():.2f}")
    print(f"  Images with people: {(results_df['Pipeline_Total'] > 0).sum()}")
    print(f"  Adults detected: {results_df['Pipeline_Adult'].sum()}")
    print(f"  Children detected: {results_df['Pipeline_Child'].sum()}")
    
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
