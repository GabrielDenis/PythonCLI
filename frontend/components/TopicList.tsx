import styles from './TopicList.module.css';
import { API_URL } from '../config';

interface TopicListProps {
    topics: any[];
    onRefresh: () => void;
}

export default function TopicList({ topics, onRefresh }: TopicListProps) {
    const toggleBookStatus = async (bookId: number, currentStatus: string) => {
        const newStatus = currentStatus === 'unread' ? 'read' : 'unread';
        await fetch(`${API_URL}/books/${bookId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        onRefresh();
    };

    const deleteBook = async (bookId: number) => {
        if (!confirm('Are you sure you want to remove this book?')) return;
        await fetch(`${API_URL}/books/${bookId}`, { method: 'DELETE' });
        onRefresh();
    };

    const enrichTopic = async (topicId: number) => {
        const btn = document.getElementById(`enrich-btn-${topicId}`) as HTMLButtonElement;
        if (btn) { btn.disabled = true; btn.innerText = "Searching..."; }

        await fetch(`${API_URL}/topics/${topicId}/enrich`, { method: 'POST' });
        onRefresh();
    };

    return (
        <div className={styles.grid}>
            {topics.map((topic: any) => (
                <div key={topic.id} className={styles.card}>
                    <span className={styles.id}>#{topic.id}</span>
                    <h2>{topic.name}</h2>

                    <div className={styles.bookList}>
                        {topic.books && topic.books.length > 0 ? (
                            topic.books.map((book: any) => (
                                <div key={book.id} className={styles.bookItem}>
                                    <input
                                        type="checkbox"
                                        checked={book.status === 'read'}
                                        onChange={() => toggleBookStatus(book.id, book.status || 'unread')}
                                    />
                                    <span style={{
                                        textDecoration: book.status === 'read' ? 'line-through' : 'none',
                                        color: book.status === 'read' ? '#666' : '#fff'
                                    }}>
                                        {book.title}
                                    </span>
                                    <button
                                        onClick={() => deleteBook(book.id)}
                                        style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: '#ff4444' }}
                                    >
                                        ×
                                    </button>
                                </div>
                            ))
                        ) : (
                            <div style={{ textAlign: 'center', marginTop: '10px' }}>
                                <p style={{ fontSize: '0.8rem', color: '#666', marginBottom: '10px' }}>No books explored yet.</p>
                                <button
                                    id={`enrich-btn-${topic.id}`}
                                    onClick={() => enrichTopic(topic.id)}
                                    style={{
                                        padding: '0.5rem 1rem',
                                        background: 'var(--primary)',
                                        border: 'none',
                                        borderRadius: '4px',
                                        color: 'white',
                                        cursor: 'pointer',
                                        fontSize: '0.9rem'
                                    }}
                                >
                                    🔍 Find Suggestions
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}