import './globals.css';

export const metadata = {
  title: 'AgentZero',
  description: 'AI-powered administrative assistant',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ height: '100vh', overflow: 'hidden' }}>{children}</body>
    </html>
  );
}
