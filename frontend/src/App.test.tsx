import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders main app heading', () => {
  render(<App />);
  const headingElement = screen.getByText(/Sentiment Analysis Engine/i);
  expect(headingElement).toBeInTheDocument();
});
