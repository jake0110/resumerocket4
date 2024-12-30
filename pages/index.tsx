import Layout from '../components/Layout';
import TestComponent from '../components/TestComponent';

const Home = () => {
  return (
    <Layout>
      <h2 className="text-2xl font-bold">Welcome to My Next.js App</h2>
      <p>This is a basic setup with TypeScript and a custom layout.</p>
      <TestComponent />
    </Layout>
  );
};

export default Home; 