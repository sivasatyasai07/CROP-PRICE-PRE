import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ForecastButton } from '../components/forecast/ForecastButton';

describe('ForecastButton Component', () => {
  it('triggers click callback when clicked', () => {
    const handleClick = vi.fn();
    render(<ForecastButton onClick={handleClick} loading={false} />);
    
    const btn = screen.getByRole('button');
    fireEvent.click(btn);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disables button and shows spinner during loading state', () => {
    render(<ForecastButton onClick={() => {}} loading={true} loadingStep="Checking selected date..." />);
    const btn = screen.getByRole('button');
    expect(btn.hasAttribute('disabled')).toBe(true);
    expect(screen.getByText('Checking selected date...')).toBeTruthy();
  });
});
