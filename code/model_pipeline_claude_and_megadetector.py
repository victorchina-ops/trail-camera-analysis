# -*- coding: utf-8 -*-
"""Trail Camera Analysis: Full Pipeline (Claude MLLM + MegaDetector+CLIP)

This script processes trail camera images with two detection methods:
1. Claude MLLM (vision AI) - requires API key
2. MegaDetector v5a + CLIP (open-source) - free

Parameterized for easy configuration. Run in Google Colab with your own Google Drive.

Usage:
    1. Set parameters in CONFIGURATION section below
    2. Authenticate Claude API via userdata in Colab
    3. Mount Google Drive
    4. Run script
"""

import os
import sys
import subprocess
import warnings
import json
import base64
import random
import time
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

# Claude API settings
CLAUDE_API_KEY_NAME = 'CLAUDE_API_KEY'  # Name of userdata key in Colab
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
CLAUDE_MAX_TOKENS = 400

# Output settings
VALIDATION_SHEETS = True           # Generate visual validation sheets
SAVE_INTERVAL = 50                 # Save checkpoint every N images
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# ===========================================================================
# SETUP & INITIALIZATION
# ===========================================================================

print("="*70)
print("TRAIL CAMERA ANALYSIS - FULL PIPELINE (Claude + MegaDetector+CLIP)")
print("="*70)

# Check environment
try:
    from google.colab import userdata
    IN_COLAB = True
    print("✓ Running in Google Colab")
except:
    IN_COLAB = False
    print("⚠ Not in Google Colab (will need manual API key setup)")

# Create output directory
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
print(f"✓ Output directory: {OUTPUT_FOLDER}")

# Install required packages
print("\n🛠️ Installing dependencies...")
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])

packages = ["urllib3<2.0.0", "ultralytics", "anthropic", "transformers", "requests"]
for pkg in packages:
    try:
        __import__(pkg.split('[')[0].replace('-', '_'))
    except ImportError:
        print(f"  Installing {pkg}...")
        install(pkg)

from transformers import CLIPProcessor, CLIPModel
try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    print("⚠ Anthropic library not available - Claude will be skipped")
    CLAUDE_AVAILABLE = False

warnings.filterwarnings("ignore")
print(f"✓ Dependencies installed")
print(f"✓ Device: {DEVICE.upper()}")

# ===========================================================================
# UTILITY FUNCTIONS
# ===========================================================================

def encode_image(image_path):
    """Encode image to base64 for API."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def resize_for_api(image_path, max_dim=1500):
    """Resize image if needed for API processing."""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim))
            temp_path = "/tmp/temp_resized.jpg"
            img.save(temp_path, quality=85)
            return temp_path
        return image_path
    except Exception as e:
        print(f"Error resizing {image_path}: {e}")
        return None

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
# CLAUDE MODEL CLASS
# ===========================================================================

class ClaudeModel:
    """Claude MLLM for activity detection."""
    
    def __init__(self, api_key=None):
        """Initialize Claude client."""
        self.ready = False
        self.client = None
        
        if not CLAUDE_AVAILABLE:
            print("⚠ Anthropic library not available")
            return
        
        try:
            if IN_COLAB:
                from google.colab import userdata
                api_key = userdata.get(CLAUDE_API_KEY_NAME)
                if not api_key:
                    print(f"⚠ Claude API key not found in Colab secrets")
                    print(f"  Please add your key as '{CLAUDE_API_KEY_NAME}' in Colab Secrets")
                    return
            elif not api_key:
                api_key = os.environ.get('CLAUDE_API_KEY')
                if not api_key:
                    print("⚠ Claude API key not provided")
                    return
            
            self.client = Anthropic(api_key=api_key)
            self.model = CLAUDE_MODEL
            self.ready = True
            print("✓ Claude API initialized")
        except Exception as e:
            print(f"⚠ Claude initialization failed: {e}")
    
    def predict(self, image_path):
        """Analyze image with Claude."""
        if not self.ready:
            return self._empty_result()
        
        prompt = """Analyze this trail camera image for wildlife monitoring.
Return a valid JSON object with integer counts for:
- total_people: total number of people visible
- adults: number of adult people
- children: number of children
- bicycles: number of bicycles
- dogs: number of dogs
- strollers: number of strollers/pushchairs
- wheelchairs: number of wheelchairs
- big_backpacks: number of large backpacks (hiking gear)
- cars: number of cars/vehicles
- motorcycles: number of motorcycles
- atvs: number of ATVs/off-road vehicles

Return ONLY valid JSON, no other text:
{"total_people":0, "adults":0, "children":0, "bicycles":0, "dogs":0, "strollers":0, "wheelchairs":0, "big_backpacks":0, "cars":0, "motorcycles":0, "atvs":0}
"""
        try:
            processed_path = resize_for_api(image_path)
            if not processed_path:
                return self._empty_result()
            
            msg = self.client.messages.create(
                model=self.model,
                max_tokens=CLAUDE_MAX_TOKENS,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": encode_image(processed_path)
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            
            txt = msg.content[0].text
            json_str = txt[txt.find('{'):txt.rfind('}')+1]
            return json.loads(json_str)
        
        except Exception as e:
            print(f"   ❌ Claude error: {e}")
            return self._empty_result()
    
    @staticmethod
    def _empty_result():
        """Return empty result dict."""
        return {
            'total_people': 0, 'adults': 0, 'children': 0,
            'bicycles': 0, 'dogs': 0, 'strollers': 0,
            'wheelchairs': 0, 'big_backpacks': 0,
            'cars': 0, 'motorcycles': 0, 'atvs': 0
        }

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
            print("  Downloading MegaDetector weights...")
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
                    'Pipeline_Total': 0,
                    'Pipeline_Adult': 0,
                    'Pipeline_Child': 0
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
                'Pipeline_Total': len(person_boxes),
                'Pipeline_Adult': counts['Adult'],
                'Pipeline_Child': counts['Child']
            }
        
        except Exception as e:
            print(f"   ❌ Pipeline error: {e}")
            return {
                'Pipeline_Total': 0,
                'Pipeline_Adult': 0,
                'Pipeline_Child': 0
            }

# ===========================================================================
# MAIN PROCESSING
# ===========================================================================

def process_image(item, claude_model, pipeline_model):
    """Process single image with both models."""
    # Extract metadata
    date, time = get_exif_data(item['path'])
    
    # Run models
    claude_result = claude_model.predict(item['path']) if claude_model.ready else ClaudeModel._empty_result()
    pipeline_result = pipeline_model.analyze(item['path'])
    
    # Compile results
    row = {
        'Site': item['site'],
        'Date': date,
        'Time': time,
        'Filename': item['name'],
        
        # Claude outputs
        'Claude_Total': claude_result.get('total_people', 0),
        'Claude_Adult': claude_result.get('adults', 0),
        'Claude_Child': claude_result.get('children', 0),
        'Claude_Bike': claude_result.get('bicycles', 0),
        'Claude_Dog': claude_result.get('dogs', 0),
        'Claude_Stroller': claude_result.get('strollers', 0),
        'Claude_Wheelchair': claude_result.get('wheelchairs', 0),
        'Claude_Backpack': claude_result.get('big_backpacks', 0),
        'Claude_Car': claude_result.get('cars', 0),
        'Claude_Motorcycle': claude_result.get('motorcycles', 0),
        'Claude_ATV': claude_result.get('atvs', 0),
        
        # Pipeline outputs
        'Pipeline_Total': pipeline_result['Pipeline_Total'],
        'Pipeline_Adult': pipeline_result['Pipeline_Adult'],
        'Pipeline_Child': pipeline_result['Pipeline_Child'],
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
                
                # Create comprehensive label
                label = (
                    f"{res['Filename']} | {res['Date']} {res['Time']}\n"
                    f"CLAUDE: Ppl:{res['Claude_Total']} "
                    f"(Ad:{res['Claude_Adult']} Ch:{res['Claude_Child']}) "
                    f"Bikes:{res['Claude_Bike']} Dogs:{res['Claude_Dog']} "
                    f"Bags:{res['Claude_Backpack']}\n"
                    f"Vehicles: Car:{res['Claude_Car']} Moto:{res['Claude_Motorcycle']} ATV:{res['Claude_ATV']} | "
                    f"Stroller:{res['Claude_Stroller']} Wheelchair:{res['Claude_Wheelchair']}\n"
                    f"PIPELINE: Ppl:{res['Pipeline_Total']} "
                    f"(Ad:{res['Pipeline_Adult']} Ch:{res['Pipeline_Child']})"
                )
                
                ax.set_title(label, fontsize=8, backgroundcolor='lightyellow', pad=5)
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
    
    # Initialize models
    claude = ClaudeModel()
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
            row, img_path = process_image(item, claude, pipeline)
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
                row, _ = process_image(item, claude, pipeline)
                all_results.append(row)
                print("✓")
                
                # Save checkpoint
                if i % SAVE_INTERVAL == 0:
                    checkpoint_path = os.path.join(
                        OUTPUT_FOLDER,
                        f"checkpoint_{i}_{TIMESTAMP}.csv"
                    )
                    pd.DataFrame(all_results).to_csv(checkpoint_path, index=False)
                    print(f"  💾 Checkpoint saved: {checkpoint_path}")
            
            except Exception as e:
                print(f"✗ {e}")
    
    # Save final results
    print("\n" + "="*70)
    print("SAVING RESULTS")
    print("="*70)
    
    output_path = os.path.join(OUTPUT_FOLDER, f"Results_Full_Pipeline_{TIMESTAMP}.csv")
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✓ Results saved: {output_path}")
    print(f"✓ Total images processed: {len(all_results)}")
    print(f"✓ Output folder: {OUTPUT_FOLDER}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
    print("\nClaude Method:")
    print(f"  Total humans detected: {results_df['Claude_Total'].sum()}")
    print(f"  Average per image: {results_df['Claude_Total'].mean():.2f}")
    print(f"  Images with people: {(results_df['Claude_Total'] > 0).sum()}")
    
    print("\nPipeline Method:")
    print(f"  Total humans detected: {results_df['Pipeline_Total'].sum()}")
    print(f"  Average per image: {results_df['Pipeline_Total'].mean():.2f}")
    print(f"  Images with people: {(results_df['Pipeline_Total'] > 0).sum()}")
    
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
