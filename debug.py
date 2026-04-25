import os
import sys

# Add services and models to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from services.logic_service import predict_npk
from services.crop_service import predict_crop_top5
import random

soil_types = ['Black Soil', 'Cinder Soil', 'Laterite Soil', 'Peat Soil', 'Yellow Soil']
lat = 20.0
lon = 80.0
temp = 25.0
humidity = 60.0
rainfall = 100.0

for soil in soil_types:
    N, P, K = predict_npk(soil)
    print(f"Soil: {soil} -> NPK: ({N}, {P}, {K})")
    crops = predict_crop_top5(N, P, K, temp, humidity, rainfall)
    print(f"  Top crop: {crops[0]}")
