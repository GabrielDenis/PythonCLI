import TopicList from '@/components/TopicList';
import TopicForm from '@/components/TopicForm';

export default function Home() {
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
      <TopicForm />
      <TopicList />
    </main>
  );
}