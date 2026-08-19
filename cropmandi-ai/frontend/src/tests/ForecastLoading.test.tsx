import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { ForecastLoadingState } from '../components/forecast/ForecastLoadingState';

describe('ForecastLoadingState Component', () => {
  it('renders active fetching status text correctly', () => {
    render(<ForecastLoadingState loadingStep="Fetching latest official mandi data..." />);
    expect(screen.getByText('Fetching latest official mandi data...')).toBeTruthy();
  });
});
