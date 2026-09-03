import { useState } from 'react';

const API_URL = 'https://my-boardgame-helper.onrender.com'; // БЕЗ СЛЕША В КОНЦЕ!

export function useApiSearch() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [games, setGames] = useState([]);
  const [selectedGame, setSelectedGame] = useState('all');

  const loadGames = async () => {
    try {
      const response = await fetch(`${API_URL}/games`);
      if (!response.ok) throw new Error('Ошибка загрузки списка игр');
      const data = await response.json();
      setGames(data);
    } catch (err) {
      console.error('Ошибка загрузки игр:', err);
    }
  };

  const search = async (query, gameName = selectedGame) => {
    if (!query || query.trim() === '') {
      setResults([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: query.trim(),
          game_name: gameName === 'all' ? null : gameName
        })
      });

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      console.error('Ошибка поиска:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return { 
    results, 
    isLoading, 
    error, 
    search,
    games,
    selectedGame,
    setSelectedGame,
    loadGames
  };
}
