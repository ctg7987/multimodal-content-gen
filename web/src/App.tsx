import MarketingForm from './components/MarketingForm';

function App() {
  return (
    <div style={{ 
      maxWidth: '95vw', 
      width: '100%',
      margin: '0 auto', 
      padding: '2rem 1rem',
      minHeight: '100vh'
    }}>
      <header style={{ 
        textAlign: 'center', 
        marginBottom: '3rem',
        paddingBottom: '2rem'
      }}>
        <h1 style={{ 
          fontSize: '4rem', 
          fontWeight: '900', 
          margin: '0 0 0.5rem 0',
          color: '#000000',
          letterSpacing: '-0.025em',
          textShadow: '0 2px 4px rgba(255,255,255,0.8)'
        }}>
          Multimodal Marketing Content Generator
        </h1>
        <p style={{ 
          fontSize: '1.5rem', 
          color: 'rgba(255,255,255,0.95)',
          margin: 0,
          textShadow: '0 2px 4px rgba(0,0,0,0.3)',
          fontWeight: '500'
        }}>
          Generate professional marketing content across multiple channels
        </p>
      </header>
      <main>
        <MarketingForm />
      </main>
    </div>
  );
}

export default App;

