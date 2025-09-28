import React, { type ReactNode } from 'react';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ 
        fontFamily: 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial',
        margin: 0,
        padding: 0,
        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        color: '#1f2937',
        minHeight: '100vh'
      }}>
        <div style={{ 
          maxWidth: 1200, 
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
              fontSize: '3rem', 
              fontWeight: '900', 
              margin: '0 0 0.5rem 0',
              color: '#000000',
              letterSpacing: '-0.025em',
              textShadow: '0 2px 4px rgba(255,255,255,0.8)'
            }}>
              Multimodal Marketing Content Generator
            </h1>
            <p style={{ 
              fontSize: '1.25rem', 
              color: 'rgba(255,255,255,0.95)',
              margin: 0,
              textShadow: '0 2px 4px rgba(0,0,0,0.3)',
              fontWeight: '500'
            }}>
              Generate professional marketing content across multiple channels
            </p>
          </header>
          <main>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
