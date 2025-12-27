'use client';

import { useEffect, useState } from 'react';
import styles from './TopicList.module.css';
import { API_URL } from '../config';

export default function TopicList() {
    const [topics, setTopics] = useState<any[]>([]);

    useEffect(() => {
        // Fetch data when the component loads in the browser
        fetch(`${API_URL}/topics`)
            .then(res => res.json())
            .then(data => setTopics(data))
            .catch(err => console.error("Error fetching topics:", err));
    }, []);

    return (
        <div className={styles.grid}>
            {topics.map((topic: any) => (
                <div key={topic.id} className={styles.card}>
                    <span className={styles.id}>#{topic.id}</span>
                    <h2>{topic.name}</h2>
                    <p>Books: {topic.books ? topic.books.length : 0}</p>
                </div>
            ))}
        </div>
    );
}