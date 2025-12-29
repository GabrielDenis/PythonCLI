'use client';

import TopicList from '@/components/TopicList';
import TopicForm from '@/components/TopicForm';
import { useState, useEffect } from 'react';
import { API_URL } from '../config';

export default function Home() {
  const [topics, setTopics] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Función para obtener los temas
  const fetchTopics = async () => {
    try {
      setIsLoading(true);
      const res = await fetch(`${API_URL}/topics`);
      const data = await res.json();
      setTopics(data);
    } catch (error) {
      console.error("Error fetching topics:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Cargar temas al iniciar
  useEffect(() => {
    fetchTopics();
  }, []);

  return (
    <main style={{
      padding: "2rem",
      display: "flex",
      flexDirection: "column",
      alignItems: "center"
    }}>
      <h1 style={{
        fontSize: "3rem",
        marginBottom: "2rem",
        background: "linear-gradient(to right, #fff, #3b82f6)",
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent"
      }}>
        Learning Tracker
      </h1>
      <TopicForm onTopicAdded={fetchTopics} />

      {isLoading ? (
        <p style={{ color: '#888', marginTop: '2rem' }}>Loading awesome topics...</p>
      ) : (
        <TopicList topics={topics} onRefresh={fetchTopics} />
      )}
    </main>
  );
}