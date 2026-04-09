import React, { useEffect, useState } from 'react';
import { sentimentApi } from './services/sentimentApi';
import { PoliticalEntity } from './types/sentiment';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

interface LexiconStats {
  category_stats: Record<string, { word_count: number; recent_additions: number }>;
  metadata: {
    version: string;
    last_updated: string;
    total_words: number;
  };
  total_words: number;
}

interface LexiconEntry {
  word: string;
  category: string;
  details: {
    meaning: string;
  };
}

interface LexiconForm {
  word: string;
  meaning: string;
  category: string;
  context_sentence: string;
}

interface EntityForm {
  entity: string;
  type: string;
  full_name: string;
  description: string;
}

const LexiconManager: React.FC = () => {
  const [stats, setStats] = useState<LexiconStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<LexiconEntry[]>([]);
  const [entry, setEntry] = useState<LexiconForm>({
    word: '',
    meaning: '',
    category: 'political',
    context_sentence: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [entities, setEntities] = useState<PoliticalEntity[]>([]);
  const [entityLoading, setEntityLoading] = useState(false);
  const [entityForm, setEntityForm] = useState<EntityForm>({
    entity: '',
    type: 'party',
    full_name: '',
    description: ''
  });

  useEffect(() => {
    loadStats();
    loadEntities();
  }, []);

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/lexicon/stats`);
      const data = await response.json();
      setStats(data);
    } catch {
      setStats(null);
    }
  };

  const searchLexicon = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/lexicon/search?q=${encodeURIComponent(searchQuery)}`);
      const data = await response.json();
      setSearchResults(Array.isArray(data.results) ? data.results : []);
    } catch {
      setSearchResults([]);
    }
  };

  const addWord = async () => {
    if (!entry.word.trim() || !entry.meaning.trim() || !entry.context_sentence.trim()) {
      setMessage('Word, meaning, and context are required.');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/lexicon/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry)
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`Added "${entry.word}" to the lexicon.`);
        setEntry({ word: '', meaning: '', category: 'political', context_sentence: '' });
        await loadStats();
      } else {
        setMessage(data.error || 'Failed to add word.');
      }
    } catch {
      setMessage('Failed to add word.');
    } finally {
      setLoading(false);
    }
  };

  const loadEntities = async () => {
    const data = await sentimentApi.listPoliticalEntities();
    setEntities(data);
  };

  const addEntity = async () => {
    if (!entityForm.entity.trim() || !entityForm.type.trim()) {
      setMessage('Entity name and type are required.');
      return;
    }

    setEntityLoading(true);
    const result = await sentimentApi.addPoliticalEntity({
      entity: entityForm.entity,
      type: entityForm.type,
      full_name: entityForm.full_name,
      description: entityForm.description,
    });

    if (result.ok) {
      setMessage(`Added political entity "${entityForm.entity}".`);
      setEntityForm({ entity: '', type: 'party', full_name: '', description: '' });
      await loadEntities();
    } else {
      setMessage(result.message);
    }

    setEntityLoading(false);
  };

  const removeEntity = async (id: number) => {
    const ok = await sentimentApi.deletePoliticalEntity(id);
    if (!ok) {
      setMessage('Failed to delete entity.');
      return;
    }

    setMessage('Entity deleted.');
    await loadEntities();
  };

  return (
    <div className="lexicon-shell">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Lexicon manager</p>
          <h2>Political word pool</h2>
        </div>
        <p className="section-note">Add words once and they are available to the next sentiment request immediately.</p>
      </div>

      {message && <div className="status-banner">{message}</div>}

      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-label">Total words</span>
          <strong className="stat-value">{stats?.total_words ?? 0}</strong>
        </div>
        <div className="stat-card">
          <span className="stat-label">Last updated</span>
          <strong className="stat-value">
            {stats?.metadata.last_updated ? new Date(stats.metadata.last_updated).toLocaleString() : 'Unknown'}
          </strong>
        </div>
      </div>

      <div className="lexicon-grid">
        <div className="subpanel">
          <h3>Search</h3>
          <div className="row">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search words or meanings"
            />
            <button type="button" onClick={searchLexicon}>Search</button>
          </div>

          <div className="result-list">
            {searchResults.length === 0 ? (
              <p className="muted">No results yet.</p>
            ) : (
              searchResults.map((item, index) => (
                <div key={`${item.word}-${index}`} className="result-row">
                  <strong>{item.word}</strong>
                  <span>{item.category}</span>
                  <p>{item.details.meaning}</p>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="subpanel">
          <h3>Add word</h3>
          <div className="stack">
            <input
              type="text"
              value={entry.word}
              onChange={(e) => setEntry({ ...entry, word: e.target.value })}
              placeholder="Word"
            />
            <input
              type="text"
              value={entry.meaning}
              onChange={(e) => setEntry({ ...entry, meaning: e.target.value })}
              placeholder="Meaning"
            />
            <select
              value={entry.category}
              onChange={(e) => setEntry({ ...entry, category: e.target.value })}
            >
              <option value="political">Political</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
              <option value="common_words">Common words</option>
              <option value="botswana_specific">Botswana specific</option>
            </select>
            <textarea
              value={entry.context_sentence}
              onChange={(e) => setEntry({ ...entry, context_sentence: e.target.value })}
              placeholder="Example sentence"
              rows={4}
            />
            <button type="button" onClick={addWord} disabled={loading}>
              {loading ? 'Saving...' : 'Add to lexicon'}
            </button>
          </div>
        </div>
      </div>

      <div className="category-grid">
        {Object.entries(stats?.category_stats ?? {}).map(([category, info]) => (
          <div key={category} className="category-card">
            <span>{category}</span>
            <strong>{info.word_count}</strong>
          </div>
        ))}
      </div>

      <div className="section-heading" style={{ marginTop: '2rem' }}>
        <div>
          <p className="eyebrow">Political entities</p>
          <h2>Database-backed entity manager</h2>
        </div>
        <p className="section-note">Entities used in analysis are now loaded from SQLite and can be managed from UI.</p>
      </div>

      <div className="lexicon-grid">
        <div className="subpanel">
          <h3>Add entity</h3>
          <div className="stack">
            <input
              type="text"
              value={entityForm.entity}
              onChange={(e) => setEntityForm({ ...entityForm, entity: e.target.value })}
              placeholder="Entity label (e.g., BDP, Masisi)"
            />
            <select
              value={entityForm.type}
              onChange={(e) => setEntityForm({ ...entityForm, type: e.target.value })}
            >
              <option value="party">Party</option>
              <option value="leader">Leader</option>
              <option value="location">Location</option>
              <option value="institution">Institution</option>
              <option value="other">Other</option>
            </select>
            <input
              type="text"
              value={entityForm.full_name}
              onChange={(e) => setEntityForm({ ...entityForm, full_name: e.target.value })}
              placeholder="Full name (optional)"
            />
            <textarea
              value={entityForm.description}
              onChange={(e) => setEntityForm({ ...entityForm, description: e.target.value })}
              placeholder="Description (optional)"
              rows={3}
            />
            <button type="button" onClick={addEntity} disabled={entityLoading}>
              {entityLoading ? 'Saving...' : 'Add entity'}
            </button>
          </div>
        </div>

        <div className="subpanel">
          <h3>Current entities ({entities.length})</h3>
          <div className="result-list">
            {entities.length === 0 ? (
              <p className="muted">No entities found.</p>
            ) : (
              entities.map((entity) => (
                <div key={entity.id} className="result-row">
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.75rem', alignItems: 'center' }}>
                    <strong>{entity.entity}</strong>
                    <button type="button" onClick={() => removeEntity(entity.id)}>Delete</button>
                  </div>
                  <span>{entity.type}</span>
                  {entity.full_name && <p>{entity.full_name}</p>}
                  {entity.description && <p>{entity.description}</p>}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LexiconManager;