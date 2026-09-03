import React, { useState, useEffect } from 'react';
import { useApiSearch } from './hooks/useApiSearch';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const { 
    results, 
    isLoading, 
    error, 
    search,
    games,
    selectedGame,
    setSelectedGame,
    loadGames
  } = useApiSearch();

  useEffect(() => {
    loadGames();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    search(query, selectedGame);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🎲 Помощник по правилам</h1>
        <p>Поиск по правилам — показываем страницы</p>
      </header>

      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Введите слово или фразу из правил..."
          className="search-input"
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Поиск...' : 'Найти'}
        </button>
      </form>

      {/* Выбор игры */}
      {games.length > 0 && (
        <div className="game-selector">
          <label>Искать в правилах:</label>
          <select value={selectedGame} onChange={(e) => setSelectedGame(e.target.value)}>
            <option value="all">📚 Все игры</option>
            {games.map((game, index) => (
              <option key={index} value={game}>🎮 {game}</option>
            ))}
          </select>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}

      {/* Отображение страниц */}
      {results.length > 0 && (
        <div className="results-container">
          <p className="results-count">📖 Найдено на {results.length} страницах</p>
          
          {results.map((hit, index) => (
            <div key={index} className="result-item">
              <div className="result-header">
                <span>🎮 {hit.game} — 📄 Страница {hit.page}</span>
              </div>
              
              {/* Картинка страницы */}
              {hit.image ? (
                <div className="page-image-container">
                  <img 
                    src={`data:image/png;base64,${hit.image}`}
                    alt={`Страница ${hit.page} игры ${hit.game}`}
                    className="page-image"
                    loading="lazy"
                    onClick={() => window.open(`data:image/png;base64,${hit.image}`, '_blank')}
                  />
                  <div className="image-hint">👆 Нажмите для увеличения</div>
                </div>
              ) : (
                <div className="no-image">
                  <p>⚠️ Изображение страницы недоступно</p>
                </div>
              )}
              
              {/* Найденные фрагменты текста */}
              {hit.snippets && hit.snippets.length > 0 && (
                <div className="snippets">
                  <p className="snippets-label">🔍 Найденные фрагменты:</p>
                  {hit.snippets.map((snippet, idx) => (
                    <div key={idx} className="snippet-item">...{snippet}</div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {!isLoading && !error && results.length === 0 && query && (
        <div className="no-results">
          <p>😕 Ничего не найдено</p>
        </div>
      )}

      {!isLoading && !error && !query && (
        <div className="welcome-message">
          <p>💡 Введите слово из правил</p>
          <p className="hint">Например: "action", "turn", "player"</p>
        </div>
      )}
    </div>
  );
}

export default App;