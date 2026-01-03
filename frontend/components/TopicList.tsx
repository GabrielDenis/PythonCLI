import styles from './TopicList.module.css';
import { API_URL } from '../config';
import BookList from './BookList';

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

    const deleteTopic = async (topicId: number) => {
        if (!confirm('Are you sure you want to delete this topic? All books inside it will be lost.')) return;
        await fetch(`${API_URL}/topics/${topicId}`, { method: 'DELETE' });
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
                    <div className={styles.cardHeader}>
                        <span className={styles.id}>#{topic.id}</span>
                        <h2>{topic.name}</h2>
                        <button
                            className={styles.deleteTopicBtn}
                            onClick={() => deleteTopic(topic.id)}
                            title="Delete Topic"
                        >
                            🗑️
                        </button>
                    </div>

                    <BookList
                        books={topic.books}
                        topicId={topic.id}
                        onToggleStatus={toggleBookStatus}
                        onDelete={deleteBook}
                        onEnrich={enrichTopic}
                    />
                </div>
            ))}
        </div>
    );
}