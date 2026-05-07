import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AnalyticsContextType {
  startDate: string;
  endDate: string;
  setStartDate: (date: string) => void;
  setEndDate: (date: string) => void;
  isFilterVisible: boolean;
  setIsFilterVisible: (visible: boolean) => void;
}

const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

export const AnalyticsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [isFilterVisible, setIsFilterVisible] = useState(false);

  return (
    <AnalyticsContext.Provider value={{ 
      startDate, 
      endDate, 
      setStartDate, 
      setEndDate,
      isFilterVisible,
      setIsFilterVisible
    }}>
      {children}
    </AnalyticsContext.Provider>
  );
};

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  if (context === undefined) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};
