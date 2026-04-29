# Soil Type Mapping - Quick Reference

## Mapping Summary (TL;DR)

```
Clay     → Black Soil      (Moisture-retentive, clay-based)
Silt     → Black Soil      (Similar moisture retention to clay)
Sandy    → Yellow Soil     (Sandy, less fertile)
Saline   → Cinder Soil     (Poor fertility, barren)
Peaty    → Peat Soil       (Organic-rich, excellent water retention)
Loamy    → Laterite Soil   (Iron oxide rich, good drainage)
```

---

## Quick Usage

### Get Mapped Soil Type
```python
from services.soil_mapping_service import get_mapped_soil_type

mapped = get_mapped_soil_type('clay')          # Returns 'Black Soil'
mapped = get_mapped_soil_type('sandy')         # Returns 'Yellow Soil'
mapped = get_mapped_soil_type('loamy')         # Returns 'Laterite Soil'
```

### Predict Soil from Image
```python
from services.image_service import predict_soil

soil_type = predict_soil('path/to/soil/image.jpg')
print(soil_type)  # e.g., 'Black soil'
```

### Convert Dataset
```python
from services.soil_mapping_service import convert_npk_dataset

# Converts CSV with original soil types to mapped types
df = convert_npk_dataset('input.csv', 'output.csv')
```

### Print All Mappings
```python
from services.soil_mapping_service import print_mapping_info

print_mapping_info()
```

### Validate Soil Type
```python
from services.soil_mapping_service import validate_soil_type

valid, mapped, msg = validate_soil_type('clay')
if valid:
    print(f"✓ {msg}")
else:
    print(f"✗ {msg}")
```

---

## Model Information

- **Type:** Random Forest Classifier
- **File:** `models/soil_model.pkl`
- **Accuracy:** 100% (on training set of 158 images)
- **Classes:** 5 soil types
  - Black soil
  - Cinder soil
  - Laterite Soil
  - Peat Soil
  - Yellow Soil

---

## Files Reference

| File | Purpose |
|------|---------|
| `models/train_soil_model_sklearn.py` | Train the soil classification model |
| `services/soil_mapping_service.py` | Soil type mapping utilities |
| `services/image_service.py` | Image-based soil prediction |
| `SOIL_MAPPING_GUIDE.md` | Detailed documentation |
| `IMPLEMENTATION_SUMMARY.md` | Complete implementation report |

---

## Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Train model (if not already trained)
python models/train_soil_model_sklearn.py

# Or use the TensorFlow version (if TensorFlow is available)
# python models/train_soil_model.py
```

---

## Final Categories (5 Total)

1. **Black Soil** (Clay + Silt)
   - Color: Deep black/brown
   - Properties: Moisture-retentive, fertile
   - Best for: Cotton, sugarcane, wheat

2. **Yellow Soil** (Sandy)
   - Color: Yellowish
   - Properties: Sandy, less fertile
   - Best for: Crops with low fertility requirements

3. **Cinder Soil** (Saline)
   - Color: Light gray/white
   - Properties: Poor fertility, barren
   - Best for: Limited agricultural use

4. **Peat Soil** (Peaty)
   - Color: Dark brown/black
   - Properties: Organic-rich, excellent water retention
   - Best for: Vegetables, fruits, drainage crops

5. **Laterite Soil** (Loamy)
   - Color: Reddish/brown
   - Properties: Iron oxide rich, loamy
   - Best for: General agriculture, good drainage

---

## Key Features

✅ Standardized soil categorization  
✅ Automatic type mapping  
✅ Image-based soil prediction  
✅ Dataset conversion utilities  
✅ Robust machine learning model  
✅ Python 3.13 compatible  
✅ No GPU required  
✅ Comprehensive documentation  

---

## Support

For more details, see:
- `SOIL_MAPPING_GUIDE.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- Source code comments in respective service files
