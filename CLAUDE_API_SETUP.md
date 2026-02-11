# Claude API Setup Guide

Complete guide to obtaining and authenticating Claude API key in Google Colab.

**⏱️ Time required**: 5-10 minutes  
**💰 Cost**: Free (includes trial credits)  
**🎯 Skill level**: Beginner friendly

---

## Step 1: Create Anthropic Account

### Visit Console

1. Go to: https://console.anthropic.com
2. Click **"Sign Up"** (top right)

### Sign Up

1. Enter email address
2. Create password (strong)
3. Click **"Sign up"**
4. Check email for verification link
5. Click verification link in email

### Verify Email

- Email opens Anthropic console
- You now have a free account ✅

---

## Step 2: Create API Key

### Navigate to Keys

1. In console, click **"API Keys"** (left sidebar)
2. Or go to: https://console.anthropic.com/account/keys

### Create New Key

1. Click **"Create Key"** (button)
2. Give it a name (e.g., "Colab - Trail Camera")
3. Click **"Create"**

### Copy Your Key

1. Your API key appears (starts with `sk-ant-...`)
2. **Copy it** (click copy icon)
3. ⚠️ **DO NOT SHARE** - keep it secret!
4. Can't be recovered if lost - must create new one

### Save Location

You'll need this key in next step. Keep it nearby.

**Example key:**
```
sk-ant-abcdefghijklmnopqrstuvwxyz123456...
```

---

## Step 3: Add Key to Google Colab

### Open Colab Notebook

1. Open one of our notebooks in Colab:
   - Full Pipeline: `Trail_Camera_Analysis_Full.ipynb`
   - (Pipeline only doesn't need this)

### Add Secret to Colab

1. In Colab, left sidebar shows file icon 📁
2. Below that, look for **🔑 Secrets** tab
3. Click the **🔑 Secrets** button

### Create New Secret

1. Click **"Add new secret"** button
2. Name: `CLAUDE_API_KEY` (exact spelling!)
3. Value: Paste your API key (sk-ant-...)
4. **Important**: Toggle **"Notebook access"** to ON ✓
5. Click **"Save"** button

### Verify Setup

1. Secret should appear in list
2. Shows `CLAUDE_API_KEY` ✓

**Screenshot locations:**
```
Colab Interface:
├── Left Sidebar
│   ├── 📁 Files
│   ├── 🔑 Secrets  ← Click here
│   └── ...
```

---

## Step 4: Test Authentication

### Run Test Cell

In the Colab notebook, run this test cell:

```python
from google.colab import userdata

# Test Claude API authentication
api_key = userdata.get('CLAUDE_API_KEY')

if api_key:
    print("✅ Claude API Key found!")
    print(f"Key starts with: {api_key[:20]}...")
else:
    print("❌ Claude API Key NOT found")
    print("Please add it to Colab Secrets with name: CLAUDE_API_KEY")
```

### Expected Output

**If working:**
```
✅ Claude API Key found!
Key starts with: sk-ant-...
```

**If not working:**
```
❌ Claude API Key NOT found
Please add it to Colab Secrets with name: CLAUDE_API_KEY
```

### Fix If Not Working

1. **Misspelled name?** Must be exactly `CLAUDE_API_KEY`
2. **Forgot to enable Notebook access?** Re-add secret with toggle ON
3. **Key wrong?** Copy directly from console, don't edit
4. **Restart kernel?** Click `Runtime > Restart Session` and try again

---

## Step 5: Verify API Has Credits

### Check in Console

1. Go to: https://console.anthropic.com/account/overview
2. Look for **"Usage"** or **"Credits"** section
3. Should show available credits (free trial includes some)

### Check API Limits

1. Go to: https://console.anthropic.com/account/limits
2. Should show:
   - Requests per minute: 100,000
   - Daily spend limit: (default $100)
   - Request limits: (very high)

### No Credits?

If you have $0 credits:
- Add payment method (credit card)
- Or wait for free trial to activate
- Or use Pipeline Only version (free)

---

## How It Works in Script

The script automatically authenticates using your secret:

```python
from google.colab import userdata
from anthropic import Anthropic

# Retrieve API key from Colab Secrets
api_key = userdata.get('CLAUDE_API_KEY')

# Create Anthropic client
client = Anthropic(api_key=api_key)

# Now you can make API calls!
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=400,
    messages=[...]
)
```

---

## Troubleshooting

### Problem: "API key not found"

**Cause:** Secret not added to Colab

**Solution:**
1. Click 🔑 Secrets tab (left sidebar)
2. Click "Add new secret"
3. Name: `CLAUDE_API_KEY` (exact!)
4. Value: `sk-ant-...` (your key)
5. Toggle "Notebook access" to ON
6. Click Save
7. Restart Colab kernel

### Problem: "Invalid API key"

**Cause:** Wrong key or typo

**Solution:**
1. Go to https://console.anthropic.com/account/keys
2. Copy full key again (click copy icon)
3. Update Colab Secret with exact value
4. Restart kernel

### Problem: "Rate limit exceeded"

**Cause:** Too many requests per minute

**Solution:**
- Normal limit is 100,000 requests/minute
- This is very high, unlikely to hit
- If it happens:
  - Reduce `MAX_PRODUCTION` in script
  - Add delays between images
  - Contact Anthropic support

### Problem: "Zero credits / out of money"

**Cause:** Free trial expired or spent

**Solution:**
1. Go to https://console.anthropic.com/account/billing
2. Add credit card to continue
3. Or use Pipeline Only version (free)

### Problem: "Rate limit exceeded despite low usage"

**Cause:** API key shared or account compromised

**Solution:**
1. Go to https://console.anthropic.com/account/keys
2. Delete compromised key
3. Create new key
4. Update Colab Secret
5. Restart kernel

### Problem: "Secret works locally but not in Colab"

**Cause:** Running locally without Colab

**Solution:**
1. Set environment variable instead:
   ```bash
   export CLAUDE_API_KEY=sk-ant-...
   ```
2. Or pass directly to script:
   ```python
   os.environ['CLAUDE_API_KEY'] = 'sk-ant-...'
   ```
3. Or modify script to accept API key as parameter

---

## Security Best Practices

### ✅ DO:

- ✅ Keep API key secret (don't share)
- ✅ Use Colab Secrets (not hardcoded)
- ✅ Use environment variables on local machine
- ✅ Rotate key if suspected compromise
- ✅ Use restricted keys if possible

### ❌ DON'T:

- ❌ Paste key into script code
- ❌ Share key in notebooks or repos
- ❌ Commit key to GitHub
- ❌ Use same key across multiple accounts
- ❌ Leave key visible in screenshots

### If Key Compromised:

1. Immediately delete key in console
2. Create new key
3. Update Colab Secret
4. No cost for creating new keys
5. Old key stops working immediately

---

## API Pricing

### Current Pricing (Feb 2026)

**Claude Haiku 4.5** (model used in script):
- Input: $0.80 per million tokens
- Output: $4.00 per million tokens

### Cost Estimate

**Per image:**
- Average image: ~6,400 input tokens
- Average output: ~50 tokens
- Cost per image: ~$0.005 + $0.0002 ≈ **$0.005-0.01**

**Per 1,000 images:**
- Cost: $5-10 (cheaper than Full Pipeline)

**For 3,050 images:**
- Cost: ~$15-30

### Ways to Reduce Cost

1. **Use Batch API** (lower rate)
   - 50% discount on input tokens
   - Can submit batch of images
   - Results available in 24 hours

2. **Reduce image size**
   - Compress before sending
   - Saves bandwidth = cheaper

3. **Cache prompts**
   - Reuse same system prompt
   - Cache gets discounted rate

4. **Process fewer images**
   - Start with small sample (100 images)
   - Validate quality
   - Scale up if good

---

## Free Trial & Credits

### What's Included

- Free account: Unlimited API access
- Free trial: Some credits (varies by signup time)
- Credit details: https://console.anthropic.com/account/overview

### When Credits Expire

1. Free trial credits have expiration date
2. After expiration, need credit card
3. Can set daily/monthly limits
4. Won't charge if you set $0 limit (will decline requests)

### How to Monitor Spending

1. Go to https://console.anthropic.com/account/billing
2. View current month costs
3. View usage by model/date
4. Set spending limits

---

## Alternative: Run Locally

If you prefer to run locally (not Colab):

### 1. Install Python

```bash
python --version  # Python 3.8+
```

### 2. Install Anthropic

```bash
pip install anthropic
```

### 3. Set Environment Variable

**On Mac/Linux:**
```bash
export CLAUDE_API_KEY=sk-ant-...
```

**On Windows (PowerShell):**
```powershell
$env:CLAUDE_API_KEY="sk-ant-..."
```

### 4. Script reads from environment

```python
import os
from anthropic import Anthropic

api_key = os.environ.get('CLAUDE_API_KEY')
client = Anthropic(api_key=api_key)
```

---

## Getting Help

### Anthropic Support

- Docs: https://docs.anthropic.com
- Status: https://status.anthropic.com
- Email: support@anthropic.com
- Community: https://discuss.anthropic.com

### This Project

- GitHub Issues: https://github.com/yourusername/trail-camera-analysis/issues
- Discussion: GitHub Discussions tab

---

## Summary Checklist

- [ ] Created Anthropic account (https://console.anthropic.com)
- [ ] Created API key in account
- [ ] Copied key (starts with `sk-ant-`)
- [ ] Opened Colab notebook
- [ ] Clicked 🔑 Secrets tab
- [ ] Added secret named `CLAUDE_API_KEY`
- [ ] Pasted API key value
- [ ] Toggled "Notebook access" ON
- [ ] Clicked Save
- [ ] Ran test cell in Colab
- [ ] Saw "✅ API Key found" message
- [ ] Ready to process images!

---

**Next Steps:**
1. Proceed with full pipeline notebook: `Trail_Camera_Analysis_Full.ipynb`
2. Or read parameter guide: `PARAMETER_GUIDE.md`
3. Or learn setup details: `SETUP_INSTRUCTIONS.md`

**Estimated time**: 5-10 minutes from start to working pipeline ⏱️
