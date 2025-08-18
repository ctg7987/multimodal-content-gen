import React, { type ReactNode } from 'react';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial' }}>
        <div style={{ maxWidth: 900, margin: '2rem auto', padding: '0 1rem' }}>
          <h1>Multimodal Marketing Content Generator</h1>
          {children}
        </div>
      </body>
    </html>
  );
}
