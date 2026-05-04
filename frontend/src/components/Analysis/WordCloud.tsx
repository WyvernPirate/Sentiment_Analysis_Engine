import React, { useMemo } from 'react';

interface WordCloudItem {
  word: string;
  count: number;
  type: string;
}

interface WordCloudProps {
  words: WordCloudItem[];
  maxWords?: number;
}

const WordCloud: React.FC<WordCloudProps> = ({ words, maxWords = 25 }) => {
  const processedWords = useMemo(() => {
    if (!words || words.length === 0) return [];
    
    const sliced = words.slice(0, maxWords);
    const maxCount = Math.max(...sliced.map(w => w.count));
    
    return sliced
      .map((w, idx) => {
        const weight = w.count / maxCount;
        // Classic word cloud logic: 
        // 1. Size scales with weight
        // 2. Random rotation (0 or 90 degrees for classic look)
        // 3. Colors based on sentiment
        const rotate = Math.random() > 0.8 ? 90 : 0; // 20% vertical words
        
        return {
          ...w,
          size: Math.max(0.6, weight * 2.2) + 'rem',
          opacity: Math.max(0.6, weight),
          rotation: rotate + 'deg',
          padding: Math.max(4, weight * 10) + 'px',
        };
      })
      .sort(() => Math.random() - 0.5);
  }, [words, maxWords]);

  if (processedWords.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 border border-dashed border-outline-variant/20 rounded bg-surface-container-lowest/30">
        <p className="font-mono text-[10px] text-on-surface-variant uppercase tracking-widest">
          No trigger data found
        </p>
      </div>
    );
  }

  return (
    <div className="relative flex flex-wrap items-center justify-center content-center gap-1 p-4 min-h-[200px] bg-surface-container-lowest/20 rounded border border-outline-variant/5 shadow-inner overflow-hidden">
      {processedWords.map((item) => (
        <div
          key={item.word}
          className="transition-transform duration-300 hover:scale-125 cursor-default group relative z-10"
          style={{
            fontSize: item.size,
            opacity: item.opacity,
            transform: `rotate(${item.rotation})`,
            padding: item.padding,
          }}
        >
          <span
            className={`
              font-headline font-bold uppercase select-none
              ${item.type === 'positive' ? 'text-secondary' : 'text-tertiary'}
              hover:drop-shadow-[0_0_8px_rgba(var(--md-sys-color-primary-rgb),0.5)]
            `}
          >
            {item.word}
          </span>
          
          <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-on-surface text-surface text-[7px] font-mono px-1 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-20 pointer-events-none uppercase">
            {item.count} mentions
          </div>
        </div>
      ))}
      
      {/* Background grid/pattern for classic feel */}
      <div className="absolute inset-0 opacity-[0.02] pointer-events-none select-none" 
           style={{ backgroundImage: 'radial-gradient(var(--md-sys-color-on-surface) 0.5px, transparent 0.5px)', backgroundSize: '10px 10px' }}>
      </div>
    </div>
  );
};

export default WordCloud;
