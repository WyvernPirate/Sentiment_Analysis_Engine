import React, { useEffect, useState } from 'react';
import { sentimentApi } from '../services/sentimentApi';
import { SentimentResult, TestExample } from '../types/sentiment';

const SENTIMENT_BG: Record<string, string> = {
  positive: 'bg-secondary/10 text-secondary border-secondary/30',
  neutral: 'bg-on-surface-variant/10 text-on-surface-variant border-outline-variant/30',
  negative: 'bg-tertiary/10 text-tertiary border-tertiary/30',
};

const ManualAnalyzer: React.FC = () => {
  const [input, setInput] = useState('');
  const [result, setResult] = useState<SentimentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [examples, setExamples] = useState<TestExample[]>([]);

  useEffect(() => {
    void sentimentApi.loadTestExamples().then(setExamples);
  }, []);

  const runAnalysis = async (text: string) => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const res = await sentimentApi.analyzeText(text);
      setResult(res);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void runAnalysis(input);
  };

  const tryExample = (text: string) => {
    setInput(text);
    void runAnalysis(text);
  };

  return (
    <>
      <div className="p-6 space-y-6">
        <div className="flex items-end justify-between border-b border-outline-variant/10 pb-4">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">Manual Analyzer</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-2">
              SINGLE_TEXT_ANALYSIS // LANGUAGE_DETECTION_AND_MODEL_ROUTING
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <section className="bg-surface-container-low border border-outline-variant/10 p-5 space-y-4">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest text-primary">
              Input Text
            </h2>
            <form onSubmit={handleSubmit} className="space-y-3">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Enter English, Setswana, or mixed text to analyze..."
                rows={6}
                className="w-full bg-surface-container-lowest border border-outline-variant/20 px-4 py-3 text-sm font-mono outline-none transition-colors placeholder:text-on-surface-variant/40 focus:border-primary"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="w-full bg-primary text-on-primary text-[11px] font-headline uppercase font-bold py-3 hover:brightness-110 disabled:opacity-50 transition-all"
              >
                {loading ? 'Analyzing...' : 'Analyze Sentiment'}
              </button>
            </form>

            <div>
              <h3 className="font-mono text-[10px] uppercase tracking-widest text-on-surface-variant mb-3">
                Try an example
              </h3>
              <div className="space-y-2">
                {examples.map((example, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => tryExample(example.text)}
                    className="w-full text-left bg-surface-container-high hover:bg-surface-bright border border-outline-variant/10 p-3 transition-colors"
                  >
                    <p className="text-sm text-on-surface">"{example.text}"</p>
                    <p className="font-mono text-[9px] text-on-surface-variant mt-1 uppercase">
                      {example.description} — expected: {example.expected}
                    </p>
                  </button>
                ))}
                {examples.length === 0 && (
                  <p className="font-mono text-[10px] text-on-surface-variant/50 italic">Loading examples...</p>
                )}
              </div>
            </div>
          </section>

          <section className="bg-surface-container-low border border-outline-variant/10 p-5">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest text-primary mb-4">
              Result
            </h2>

            {loading && (
              <p className="font-mono text-[10px] text-on-surface-variant animate-pulse">ANALYZING...</p>
            )}

            {!loading && !result && (
              <p className="font-mono text-[10px] text-on-surface-variant">
                Enter text or click an example to see results.
              </p>
            )}

            {!loading && result && result.error && (
              <p className="font-mono text-[10px] text-tertiary">{result.error}</p>
            )}

            {!loading && result && !result.error && (
              <div className="space-y-5">
                <div className="flex flex-wrap items-center gap-3">
                  <span
                    className={`px-3 py-1.5 border font-headline text-sm font-bold uppercase ${
                      SENTIMENT_BG[result.sentiment] || SENTIMENT_BG.neutral
                    }`}
                  >
                    {result.sentiment} ({Math.round(result.confidence * 100)}%)
                  </span>
                  <span className="px-3 py-1.5 bg-surface-container-high border border-outline-variant/20 font-mono text-[10px] uppercase text-on-surface-variant">
                    {result.language_detected}
                    {result.code_switching ? ' (code-switched)' : ''}
                  </span>
                </div>

                <div className="font-mono text-[10px] text-on-surface-variant space-y-1">
                  <p>MODEL: <span className="text-on-surface">{result.model_used}</span></p>
                  <p>WORD_COUNT: <span className="text-on-surface">{result.word_count}</span></p>
                </div>

                {result.matched_political_words.length > 0 && (
                  <div>
                    <h3 className="font-mono text-[10px] uppercase tracking-widest text-on-surface-variant mb-2">
                      Matched Political Words
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {result.matched_political_words.map((word, i) => (
                        <span
                          key={`${word.term}-${i}`}
                          title={word.meaning}
                          className="px-2 py-1 bg-primary/10 text-primary border border-primary/20 font-mono text-[10px] uppercase"
                        >
                          {word.term}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {(result.sentiment_words.positive.length > 0 || result.sentiment_words.negative.length > 0) && (
                  <div>
                    <h3 className="font-mono text-[10px] uppercase tracking-widest text-on-surface-variant mb-2">
                      Trigger Words
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {result.sentiment_words.positive.map((word) => (
                        <span key={`pos-${word}`} className="px-2 py-1 bg-secondary/10 text-secondary border border-secondary/20 font-mono text-[10px]">
                          + {word}
                        </span>
                      ))}
                      {result.sentiment_words.negative.map((word) => (
                        <span key={`neg-${word}`} className="px-2 py-1 bg-tertiary/10 text-tertiary border border-tertiary/20 font-mono text-[10px]">
                          - {word}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {result.political_context.entities.length > 0 && (
                  <div>
                    <h3 className="font-mono text-[10px] uppercase tracking-widest text-on-surface-variant mb-2">
                      Political Entities
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {result.political_context.entities.map((entity, i) => (
                        <span
                          key={`${entity.entity}-${i}`}
                          className="px-2 py-1 bg-surface-container-high border border-outline-variant/20 font-mono text-[10px] uppercase text-on-surface"
                        >
                          {entity.entity}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>
        </div>
      </div>
    </>
  );
};

export default ManualAnalyzer;
