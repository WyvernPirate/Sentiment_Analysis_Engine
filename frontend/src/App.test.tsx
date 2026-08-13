import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the dashboard shell without crashing', () => {
  render(<App />);
  const brandElement = screen.getByText(/COMMAND_CENTER/i);
  expect(brandElement).toBeInTheDocument();
});
