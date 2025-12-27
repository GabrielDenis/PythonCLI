import styles from './TopicList.module.css';
async function getTopics() {
    const res = await fetch('http://127.0.0.1:8000/topics', {
        cache: 'no-store'
    });
    if (!res.ok) {
        throw new Error('Failed to fetch data');
    }
    return res.json();
}
export default async function TopicList() {
    const topics = await getTopics();
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