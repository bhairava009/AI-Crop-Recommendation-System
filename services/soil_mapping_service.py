"""
Soil Type Mapping Service
Handles conversion of soil types according to specified mappings
"""

import pandas as pd
import os
from pathlib import Path

# Soil Type Mapping Dictionary
SOIL_TYPE_MAPPING = {
    'clay': 'Black Soil',
    'silt': 'Black Soil',
    'sandy': 'Yellow Soil',
    'saline': 'Cinder Soil',
    'peaty': 'Peat Soil',
    'loamy': 'Laterite Soil'
}

# Mapping Descriptions
MAPPING_DESCRIPTIONS = {
    'clay': 'Clay → Black Soil (Clay-rich soils are clay-based and retain moisture well)',
    'silt': 'Silt → Black Soil (Silt behaves similar to clay in retention, so grouped here)',
    'sandy': 'Sandy → Yellow Soil (Yellow soil is often sandy and less fertile)',
    'saline': 'Saline → Cinder Soil (Saline soil is poor in fertility, similar to cinder-type barren soil)',
    'peaty': 'Peaty → Peat Soil (Exact match ✅)',
    'loamy': 'Loamy → Laterite Soil (Approximate match - Laterite soil has loamy properties)'
}

def get_mapped_soil_type(original_soil_type):
    """
    Convert original soil type to mapped category.
    
    Args:
        original_soil_type (str): Original soil type (e.g., 'clay', 'silt', 'sandy')
    
    Returns:
        str: Mapped soil type category, or original if no mapping exists
    """
    return SOIL_TYPE_MAPPING.get(original_soil_type.lower(), original_soil_type)


def convert_npk_dataset(input_csv, output_csv=None):
    """
    Convert NPK soil dataset from original soil types to mapped categories.
    
    Args:
        input_csv (str): Path to input CSV file with original soil types
        output_csv (str): Path to output CSV file (default: input_csv with '_mapped' suffix)
    
    Returns:
        pd.DataFrame: Converted dataset
    """
    # Load the dataset
    df = pd.read_csv(input_csv)
    
    # Create output path if not specified
    if output_csv is None:
        base, ext = os.path.splitext(input_csv)
        output_csv = f"{base}_mapped{ext}"
    
    # Convert soil types if the column exists
    if 'Soil_Type' in df.columns:
        df['Soil_Type'] = df['Soil_Type'].apply(get_mapped_soil_type)
    
    # Save the converted dataset
    df.to_csv(output_csv, index=False)
    print(f"Dataset converted and saved to: {output_csv}")
    
    return df


def print_mapping_info():
    """Print information about soil type mappings."""
    print("=" * 70)
    print("SOIL TYPE MAPPING REFERENCE")
    print("=" * 70)
    
    for soil_type, description in MAPPING_DESCRIPTIONS.items():
        print(f"  {description}")
    
    print("=" * 70)


def get_soil_categories():
    """Get list of final soil categories."""
    return list(set(SOIL_TYPE_MAPPING.values()))


def validate_soil_type(soil_type):
    """
    Check if a soil type is valid (exists in mappings or target categories).
    
    Args:
        soil_type (str): Soil type to validate
    
    Returns:
        tuple: (is_valid, mapped_type, info_message)
    """
    soil_type_lower = soil_type.lower()
    
    # Check if it's an original soil type
    if soil_type_lower in SOIL_TYPE_MAPPING:
        mapped = SOIL_TYPE_MAPPING[soil_type_lower]
        return True, mapped, f"'{soil_type}' maps to '{mapped}'"
    
    # Check if it's already a final category
    final_categories = get_soil_categories()
    if soil_type in final_categories:
        return True, soil_type, f"'{soil_type}' is already a final category"
    
    return False, None, f"'{soil_type}' is not a recognized soil type"


if __name__ == "__main__":
    # Print mapping information
    print_mapping_info()
    
    # Get soil categories
    categories = get_soil_categories()
    print(f"\nFinal Soil Categories: {', '.join(sorted(categories))}")
    
    # Example validation
    test_types = ['clay', 'sandy', 'loamy', 'Black Soil', 'unknown']
    print("\nValidation Examples:")
    for soil_type in test_types:
        valid, mapped, msg = validate_soil_type(soil_type)
        status = "✓" if valid else "✗"
        print(f"  {status} {msg}")
