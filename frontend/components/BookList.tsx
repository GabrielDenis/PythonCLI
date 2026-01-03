import styles from './BookList.module.css';

interface Book {
    id: number;
    title: string;
    author: string;
    status: string;
}

interface BookListProps {
    books: Book[];
    topicId: number;
    onToggleStatus: (bookId: number, currentStatus: string) => void;
    onDelete: (bookId: number) => void;
    onEnrich: (topicId: number) => void;
}

export default function BookList({ books, topicId, onToggleStatus, onDelete, onEnrich }: BookListProps) {
    if (!books || books.length === 0) {
        return (
            <div className={styles.emptyState}>
                <p className={styles.emptyText}>No books explored yet.</p>
                <button
                    id={`enrich-btn-${topicId}`}
                    onClick={() => onEnrich(topicId)}
                    className={styles.enrichBtn}
                >
                    🔍 Find Suggestions
                </button>
            </div>
        );
    }

    return (
        <div className={styles.list}>
            {books.map((book) => (
                <div key={book.id} className={styles.item}>
                    <div className={styles.titleGroup}>
                        <input
                            type="checkbox"
                            checked={book.status === 'read'}
                            onChange={() => onToggleStatus(book.id, book.status || 'unread')}
                            className={styles.checkbox}
                        />
                        <span className={`${styles.title} ${book.status === 'read' ? styles.read : ''}`}>
                            {book.title}
                        </span>
                    </div>
                    <button
                        onClick={() => onDelete(book.id)}
                        className={styles.deleteBtn}
                        aria-label="Delete book"
                    >
                        ×
                    </button>
                </div>
            ))}
        </div>
    );
}
