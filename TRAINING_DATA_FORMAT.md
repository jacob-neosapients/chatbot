# Training Data Format

## Overview
The chatbot automatically collects all prompts during runtime in `training_data.jsonl` for future model training and improvement.

## File Format
The data is stored in **JSONL** (JSON Lines) format, where each line is a valid JSON object. This format is:
- Easy to append to (no need to load entire file)
- Easy to stream and process line-by-line
- Compatible with most ML/AI training pipelines

## Data Structure
Each entry contains the following fields:

```json
{
  "timestamp": "2025-11-11T14:10:47.451802",
  "prompt": "How risky is Senthil Kumar's portfolio?",
  "predicted_class": 0,
  "label": "SAFE",
  "confidence": 0.9931,
  "processing_time": 0.028
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 formatted timestamp of when the prompt was processed |
| `prompt` | string | The actual user input text |
| `predicted_class` | integer | Numeric class (0 = SAFE, 1 = MISUSE) |
| `label` | string | Human-readable label ("SAFE" or "MISUSE") |
| `confidence` | float | Model's confidence score (0.0 to 1.0) |
| `processing_time` | float | Time taken to classify in seconds |

## Loading the Data

### Python Example
```python
import json

# Load all training data
with open('training_data.jsonl', 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f]

# Process each entry
for entry in data:
    prompt = entry['prompt']
    label = entry['label']
    confidence = entry['confidence']
    # Use for training...
```

### Pandas Example
```python
import pandas as pd
import json

# Load into DataFrame
data = []
with open('training_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

df = pd.DataFrame(data)
print(df.head())
```

### PyTorch Dataset Example
```python
import json
from torch.utils.data import Dataset

class PromptDataset(Dataset):
    def __init__(self, jsonl_file):
        self.data = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                self.data.append(json.loads(line))
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        entry = self.data[idx]
        return {
            'text': entry['prompt'],
            'label': entry['predicted_class']
        }

# Usage
dataset = PromptDataset('training_data.jsonl')
```

## Data Statistics
The Streamlit app automatically displays real-time statistics in the sidebar:
- Total prompts collected
- Number of SAFE classifications
- Number of MISUSE classifications

## Use Cases

1. **Model Fine-tuning**: Use collected prompts to fine-tune the model on your specific use case
2. **Data Augmentation**: Identify edge cases and add to training set
3. **Performance Analysis**: Analyze confidence scores and processing times
4. **Bias Detection**: Review predictions to identify potential biases
5. **Quality Assurance**: Manual review of classifications for accuracy

## Data Privacy
⚠️ **Important**: This file contains all user prompts. Ensure:
- The file is added to `.gitignore` (already done)
- Proper access controls are in place
- Compliance with data protection regulations (GDPR, etc.)
- User consent is obtained if required

## Backup and Maintenance
Consider implementing:
- Regular backups of `training_data.jsonl`
- Periodic rotation (e.g., monthly archives)
- Data validation and cleaning pipelines
- Duplicate detection and removal
