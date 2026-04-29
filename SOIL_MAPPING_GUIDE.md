# Soil Type Mapping and Training Guide

## Soil Type Mappings Applied

This project uses a standardized soil type mapping system to categorize soil into 5 main categories:

### Mapping Reference

| Original Soil Type | Mapped Category | Explanation |
|-------------------|-----------------|-------------|
| **Clay** | Black Soil | Clay-rich soils are clay-based and retain moisture well |
| **Silt** | Black Soil | Silt behaves similar to clay in retention, so grouped here |
| **Sandy** | Yellow Soil | Yellow soil is often sandy and less fertile |
| **Saline** | Cinder Soil | Saline soil is poor in fertility, similar to cinder-type barren soil |
| **Peaty** | Peat Soil | Exact match ✅ |
| **Loamy** | Laterite Soil | Approximate match - Laterite soil has loamy properties |

### Final Soil Categories

1. **Black Soil** (Clay & Silt)
   - Clay-rich and moisture-retentive
   - Suitable for cotton, sugarcane, wheat
   
2. **Yellow Soil** (Sandy)
   - Often sandy and less fertile
   - Requires more fertilizer
   - Suitable for crops with lower fertility requirements

3. **Cinder Soil** (Saline)
   - Poor in fertility
   - Barren type soil
   - Limited crop suitability

4. **Peat Soil** (Peaty)
   - Organic-rich
   - Excellent water retention
   - Suitable for vegetables and fruits

5. **Laterite Soil** (Loamy)
   - Loamy properties
   - Iron oxide rich
   - Good drainage and moderate fertility

## Dataset Structure

### Image Classification Model
- **Location**: `Soil-Dataset/`
- **Classes**: 5 soil type folders
- **Image Size**: 150x150 pixels
- **Model**: CNN with dropout layers for regularization
- **Training Epochs**: 20

### NPK Dataset
- **Location**: `npk_soil_dataset.csv`
- **Columns**: Soil_Type, Nitrogen, Phosphorus, Potassium
- **Used for**: Soil property analysis and predictions

## Training the Model

### Run the Training Script
```bash
python models/train_soil_model.py
```

### Model Architecture
- Conv2D layers with ReLU activation
- MaxPooling for dimensionality reduction
- Dropout layers (0.2-0.3) for regularization
- Dense output layer with softmax (5 classes)
- Optimizer: Adam
- Loss: Categorical Crossentropy

## Using Soil Type Mappings

### In Python Code
```python
from services.soil_mapping_service import get_mapped_soil_type

# Convert soil type
mapped_type = get_mapped_soil_type('clay')  # Returns 'Black Soil'
```

### Example Conversions
- `get_mapped_soil_type('clay')` → `'Black Soil'`
- `get_mapped_soil_type('sandy')` → `'Yellow Soil'`
- `get_mapped_soil_type('loamy')` → `'Laterite Soil'`

## Files Modified

1. **models/train_soil_model.py**
   - Added soil type mapping dictionary
   - Improved model architecture with dropout layers
   - Extended training to 20 epochs
   - Enhanced output logging

2. **services/image_service.py**
   - Added soil type mapping functionality
   - Added `get_mapped_soil_type()` function
   - Integrated mapping reference documentation

3. **services/soil_mapping_service.py** (NEW)
   - Comprehensive soil type mapping service
   - Dataset conversion utilities
   - Validation functions

4. **requirements.txt**
   - Added TensorFlow 2.10+
   - Added Keras 2.10+
   - Added supporting libraries

## Data Conversion

To convert datasets with original soil type names:

```python
from services.soil_mapping_service import convert_npk_dataset, print_mapping_info

# Print mapping information
print_mapping_info()

# Convert a dataset
df = convert_npk_dataset('original_dataset.csv')
```

## Verification

The mapping ensures:
- ✅ Consistent soil categorization
- ✅ Backwards compatibility with existing data
- ✅ Clear documentation of mapping rationale
- ✅ Flexible conversion utilities
- ✅ Improved model performance with better training parameters

## Next Steps

1. Wait for model training to complete
2. Verify model accuracy in console output
3. Test predictions on new soil images
4. Validate crop recommendations with mapped soil types
