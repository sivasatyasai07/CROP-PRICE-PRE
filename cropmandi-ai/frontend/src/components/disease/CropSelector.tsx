import React from 'react';
import { Sprout, Tag } from 'lucide-react';

export type PlantPart = 'Leaf' | 'Stem' | 'Fruit' | 'Root' | 'Flower' | 'Whole plant' | 'Unknown';

export const SUPPORTED_CROPS = [
  'Tomato',
  'Potato',
  'Brinjal',
  'Carrot',
  'Cabbage',
  'Beetroot',
  'Chilli',
  'Capsicum',
  'Okra',
  'Onion',
  'Garlic',
  'Coriander',
  'Spinach',
  'Drumstick',
  'Cucumber',
  'Pumpkin',
  'Bottle gourd',
  'Bitter gourd',
  'Ridge gourd',
  'Beans',
  'Peas',
  'Cauliflower',
  'Radish',
  'Turnip',
  'Sweet potato',
  'Yam',
  'Banana',
  'Mango',
  'Papaya',
  'Guava',
  'Grapes',
  'Pomegranate',
  'Watermelon',
  'Muskmelon',
  'Rice',
  'Wheat',
  'Maize',
  'Sorghum',
  'Pearl millet',
  'Finger millet',
  'Groundnut',
  'Soybean',
  'Cotton',
  'Sugarcane',
  'Sunflower',
  'Sesame',
  'Red gram',
  'Green gram',
  'Black gram',
  'Chickpea',
  'Turmeric',
  'Ginger',
  'Black pepper',
  'Tea',
  'Coffee',
  'Coconut',
  'Arecanut'
];

export const PLANT_PARTS: PlantPart[] = [
  'Leaf',
  'Stem',
  'Fruit',
  'Root',
  'Flower',
  'Whole plant',
  'Unknown',
];

export interface CropSelectorProps {
  selectedCrop: string;
  onSelectCrop: (crop: string) => void;
  plantPart?: string;
  onSelectPlantPart?: (part: PlantPart) => void;
  disabled?: boolean;
}

export const CropSelector: React.FC<CropSelectorProps> = ({
  selectedCrop,
  onSelectCrop,
  plantPart = 'Leaf',
  onSelectPlantPart,
  disabled = false,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div>
          <label
            htmlFor="crop-select"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              fontSize: '0.82rem',
              fontWeight: 700,
              color: '#334155',
              marginBottom: '0.35rem',
            }}
          >
            <Sprout size={15} color="#16a34a" />
            <span>Optional Crop Hint (Open-Set Recognition Supported)</span>
          </label>
          <select
            id="crop-select"
            value={selectedCrop}
            onChange={(e) => onSelectCrop(e.target.value)}
            disabled={disabled}
            style={{
              width: '100%',
              padding: '0.65rem 0.85rem',
              borderRadius: '10px',
              border: '1px solid #cbd5e1',
              fontSize: '0.9rem',
              fontWeight: 600,
              color: '#0f172a',
              background: '#ffffff',
            }}
          >
            <option value="">-- Auto-Detect Any Agricultural Crop --</option>
            {SUPPORTED_CROPS.map((crop) => (
              <option key={crop} value={crop}>
                {crop}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="plant-part-select"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              fontSize: '0.82rem',
              fontWeight: 700,
              color: '#334155',
              marginBottom: '0.35rem',
            }}
          >
            <Tag size={15} color="#0284c7" />
            <span>Plant Part (Optional)</span>
          </label>
          <select
            id="plant-part-select"
            value={plantPart}
            onChange={(e) => onSelectPlantPart && onSelectPlantPart(e.target.value as PlantPart)}
            disabled={disabled}
            style={{
              width: '100%',
              padding: '0.65rem 0.85rem',
              borderRadius: '10px',
              border: '1px solid #cbd5e1',
              fontSize: '0.9rem',
              fontWeight: 600,
              color: '#0f172a',
              background: '#ffffff',
            }}
          >
            {PLANT_PARTS.map((part) => (
              <option key={part} value={part}>
                {part}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};
