import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { PriceSourceBadge } from '../components/forecast/PriceSourceBadge';

describe('PriceSourceBadge Component', () => {
  it('renders official latest value badge for official_api source', () => {
    render(<PriceSourceBadge priceSource="official_api" />);
    expect(screen.getByText('Official latest value')).toBeTruthy();
  });

  it('renders predicted badge for predicted price source', () => {
    render(<PriceSourceBadge priceSource="predicted" />);
    expect(screen.getByText('Predicted because official value was unavailable')).toBeTruthy();
  });

  it('renders price unavailable badge when unavailable', () => {
    render(<PriceSourceBadge priceSource="unavailable" />);
    expect(screen.getByText('Price unavailable')).toBeTruthy();
  });
});
