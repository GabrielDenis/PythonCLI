'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
export default function TopicForm() {
    const [name, setName] = useState('');
    const router = useRouter();
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name) return;
        await fetch('http://127.0.0.1:8000/topics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name }),
        });
        setName('');
        router.refresh();
    };
    return (
        <form onSubmit={handleSubmit} style={{ marginBottom: '2rem', display: 'flex', gap: '1rem' }}>
            <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="What do you want to learn?"
                style={{
                    padding: '0.8rem',
                    borderRadius: '8px',
                    border: '1px solid #333',
                    background: '#111',
                    color: '#fff',
                    width: '300px'
                }}
            />
            <button
                type="submit"
                style={{
                    padding: '0.8rem 1.5rem',
                    borderRadius: '8px',
                    border: 'none',
                    background: 'var(--primary)',
                    color: '#fff',
                    cursor: 'pointer',
                    fontWeight: 'bold'
                }}
            >
                Add Topic 🚀
            </button>
        </form>
    );
}