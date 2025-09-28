'use client';

import React, { useCallback, useMemo, useState } from 'react';

type JobResponse = {
  job_id: string;
  status: string;
  progress: number;
  result?: {
    copy: string[];
    images: string[];
    meta?: Record<string, unknown>;
  } | null;
};

const API_BASE = 'http://localhost:8000'; // TODO: make env-based

export default function Page() {
  const [title, setTitle] = useState('');
  const [brief, setBrief] = useState('');
  const [channels, setChannels] = useState<string[]>([]);
  const [brandFile, setBrandFile] = useState<File | null>(null);

  const [job, setJob] = useState<JobResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] ?? null;
    setBrandFile(f);
  }, []);

  const onChannelChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const opts = Array.from(e.target.selectedOptions, (o: HTMLOptionElement) => o.value);
    setChannels(opts);
  }, []);

  const brandProfileIdPromise = useMemo(() => async () => {
    if (!brandFile) return 'demo';
    try {
      const txt = await brandFile.text();
      const json = JSON.parse(txt);
      return json.id ?? json.brand_id ?? 'demo';
    } catch {
      return 'demo';
    }
  }, [brandFile]);

  const submit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setJob(null);
    try {
      const brand_profile_id = await brandProfileIdPromise();
      const res = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, brief, brand_profile_id, channels }),
      });
      if (!res.ok) throw new Error(`Generate failed: ${res.status}`);
      const initial: JobResponse = await res.json();
      setJob(initial);

      // poll up to ~10 tries, 1s apart
      let tries = 0;
      let latest = initial;
      while (tries < 10 && latest.status !== 'completed' && latest.status !== 'failed') {
        tries += 1;
        await new Promise(r => setTimeout(r, 1000));
        const r2 = await fetch(`${API_BASE}/jobs/${initial.job_id}`);
        if (!r2.ok) throw new Error(`Job fetch failed: ${r2.status}`);
        latest = await r2.json();
        setJob(latest);
      }
    } catch (err: any) {
      setError(err?.message ?? 'Something went wrong');
    } finally {
      setIsSubmitting(false);
    }
  }, [title, brief, channels, brandProfileIdPromise]);

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <form onSubmit={submit} style={{ 
        backgroundColor: 'white',
        padding: '2.5rem',
        borderRadius: '20px',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        backdropFilter: 'blur(10px)',
        background: 'rgba(255, 255, 255, 0.95)'
      }}>
        <div style={{ display: 'grid', gap: '1.5rem' }}>
          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '1rem', 
              fontWeight: '700', 
              color: '#1f2937',
              marginBottom: '0.75rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              🎯 Campaign Title
            </label>
            <input 
              value={title} 
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTitle(e.target.value)} 
              required 
              placeholder="Summer Sale" 
              style={{ 
                width: '100%',
                padding: '1rem', 
                border: '2px solid #e5e7eb', 
                borderRadius: '12px',
                fontSize: '1.1rem',
                outline: 'none',
                transition: 'all 0.3s ease',
                boxSizing: 'border-box',
                backgroundColor: '#f8fafc',
                focus: {
                  borderColor: '#667eea',
                  boxShadow: '0 0 0 3px rgba(102, 126, 234, 0.1)'
                }
              }} 
            />
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '1rem', 
              fontWeight: '700', 
              color: '#1f2937',
              marginBottom: '0.75rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              📝 Campaign Brief
            </label>
            <textarea 
              value={brief} 
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setBrief(e.target.value)} 
              required 
              placeholder="50% off all items" 
              rows={4} 
              style={{ 
                width: '100%',
                padding: '1rem', 
                border: '2px solid #e5e7eb', 
                borderRadius: '12px',
                fontSize: '1.1rem',
                outline: 'none',
                transition: 'all 0.3s ease',
                resize: 'vertical',
                boxSizing: 'border-box',
                backgroundColor: '#f8fafc'
              }} 
            />
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '1rem', 
              fontWeight: '700', 
              color: '#1f2937',
              marginBottom: '0.75rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              📱 Marketing Channels
            </label>
            <select 
              multiple 
              value={channels} 
              onChange={onChannelChange} 
              style={{ 
                width: '100%',
                padding: '1rem', 
                border: '2px solid #e5e7eb', 
                borderRadius: '12px',
                height: '140px',
                fontSize: '1.1rem',
                outline: 'none',
                transition: 'all 0.3s ease',
                boxSizing: 'border-box',
                backgroundColor: '#f8fafc'
              }}
            >
              <option value="email">📧 Email Marketing</option>
              <option value="instagram">📸 Instagram</option>
              <option value="facebook">👥 Facebook</option>
              <option value="twitter">🐦 Twitter</option>
            </select>
            <p style={{ 
              fontSize: '0.875rem', 
              color: '#6b7280',
              margin: '0.5rem 0 0 0',
              fontWeight: '500'
            }}>
              Hold Ctrl/Cmd to select multiple channels
            </p>
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '1rem', 
              fontWeight: '700', 
              color: '#1f2937',
              marginBottom: '0.75rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              🏢 Brand Profile (Optional)
            </label>
            <input 
              type="file" 
              accept="application/json" 
              onChange={onFileChange}
              style={{
                width: '100%',
                padding: '1rem',
                border: '2px solid #e5e7eb',
                borderRadius: '12px',
                fontSize: '1rem',
                outline: 'none',
                transition: 'all 0.3s ease',
                boxSizing: 'border-box',
                backgroundColor: '#f8fafc'
              }}
            />
            <p style={{ 
              fontSize: '0.875rem', 
              color: '#6b7280',
              margin: '0.5rem 0 0 0',
              fontWeight: '500'
            }}>
              Upload a JSON file with brand information (optional)
            </p>
          </div>

          <button 
            type="submit" 
            disabled={isSubmitting} 
            style={{ 
              width: '100%',
              padding: '1.25rem 2rem', 
              borderRadius: '16px', 
              border: 'none',
              background: isSubmitting 
                ? 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)' 
                : 'linear-gradient(135deg, #10b981 0%, #059669 100%)', 
              color: 'white', 
              fontSize: '1.25rem',
              fontWeight: '700',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              marginTop: '2rem',
              boxShadow: isSubmitting 
                ? '0 4px 15px rgba(156, 163, 175, 0.4)' 
                : '0 8px 25px rgba(16, 185, 129, 0.4)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}
          >
            {isSubmitting ? '🚀 Generating Content...' : '✨ Generate Marketing Content'}
          </button>
        </div>
      </form>

      {error && (
        <div style={{ 
          marginTop: '2rem',
          padding: '1.5rem',
          background: 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)',
          border: '2px solid #fecaca',
          borderRadius: '16px',
          color: '#dc2626',
          boxShadow: '0 4px 15px rgba(220, 38, 38, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '1.25rem' }}>⚠️</span>
            <strong style={{ fontSize: '1.1rem' }}>Error:</strong>
          </div>
          <div style={{ fontSize: '1rem' }}>{error}</div>
        </div>
      )}

      {job && (
        <div style={{ 
          marginTop: '2rem',
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '2.5rem',
          borderRadius: '20px',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.05)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{ 
              fontSize: '2rem', 
              fontWeight: '800', 
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              margin: '0 0 1.5rem 0',
              textAlign: 'center'
            }}>
              🎉 Generation Results
            </h2>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
              gap: '1.5rem',
              marginBottom: '2rem'
            }}>
              <div style={{ 
                padding: '1.5rem', 
                background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)', 
                borderRadius: '16px',
                border: '2px solid #10b981',
                boxShadow: '0 4px 15px rgba(16, 185, 129, 0.2)'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#166534', marginBottom: '0.5rem', fontWeight: '600' }}>🆔 Job ID</div>
                <div style={{ fontSize: '1rem', fontFamily: 'monospace', wordBreak: 'break-all', color: '#14532d' }}>{job.job_id}</div>
              </div>
              <div style={{ 
                padding: '1.5rem', 
                background: job.status === 'completed' 
                  ? 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)' 
                  : job.status === 'failed' 
                    ? 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)'
                    : 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)', 
                borderRadius: '16px',
                border: `2px solid ${job.status === 'completed' ? '#10b981' : job.status === 'failed' ? '#ef4444' : '#f59e0b'}`,
                boxShadow: job.status === 'completed' 
                  ? '0 4px 15px rgba(16, 185, 129, 0.2)' 
                  : job.status === 'failed' 
                    ? '0 4px 15px rgba(239, 68, 68, 0.2)'
                    : '0 4px 15px rgba(245, 158, 11, 0.2)'
              }}>
                <div style={{ fontSize: '0.875rem', color: job.status === 'completed' ? '#166534' : job.status === 'failed' ? '#991b1b' : '#92400e', marginBottom: '0.5rem', fontWeight: '600' }}>
                  {job.status === 'completed' ? '✅' : job.status === 'failed' ? '❌' : '⏳'} Status
                </div>
                <div style={{ 
                  fontSize: '1.25rem', 
                  fontWeight: '700',
                  color: job.status === 'completed' ? '#166534' : job.status === 'failed' ? '#991b1b' : '#92400e'
                }}>
                  {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                </div>
              </div>
              <div style={{ 
                padding: '1.5rem', 
                background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)', 
                borderRadius: '16px',
                border: '2px solid #10b981',
                boxShadow: '0 4px 15px rgba(16, 185, 129, 0.2)'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#166534', marginBottom: '0.5rem', fontWeight: '600' }}>📊 Progress</div>
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#166534' }}>{job.progress}%</div>
              </div>
            </div>
          </div>

          {job.result && (
            <div style={{ display: 'grid', gap: '2rem' }}>
              <div>
                <h3 style={{ 
                  fontSize: '1.75rem', 
                  fontWeight: '800', 
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  margin: '0 0 1.5rem 0',
                  textAlign: 'center'
                }}>
                  📝 Generated Copy
                </h3>
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  {job.result.copy.map((c, i) => (
                    <div key={i} style={{ 
                      padding: '1.5rem', 
                      background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)', 
                      borderRadius: '16px',
                      border: '2px solid #10b981',
                      boxShadow: '0 4px 15px rgba(16, 185, 129, 0.2)'
                    }}>
                      <div style={{ 
                        fontSize: '0.875rem', 
                        color: '#166534', 
                        marginBottom: '0.75rem',
                        fontWeight: '700',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em'
                      }}>
                        📱 Channel {i + 1}
                      </div>
                      <div style={{ 
                        fontSize: '1rem', 
                        lineHeight: '1.6',
                        whiteSpace: 'pre-wrap',
                        color: '#14532d',
                        fontWeight: '500'
                      }}>
                        {c}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 style={{ 
                  fontSize: '1.75rem', 
                  fontWeight: '800', 
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  margin: '0 0 1.5rem 0',
                  textAlign: 'center'
                }}>
                  🖼️ Generated Images
                </h3>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', 
                  gap: '1.5rem'
                }}>
                  {job.result.images.map((src, i) => (
                    <div key={i} style={{ 
                      border: '3px solid #10b981',
                      borderRadius: '20px',
                      overflow: 'hidden',
                      backgroundColor: 'white',
                      boxShadow: '0 8px 25px rgba(16, 185, 129, 0.2)',
                      transition: 'transform 0.3s ease'
                    }}>
                      <img 
                        src={src} 
                        alt={`Generated image ${i + 1}`} 
                        style={{ 
                          width: '100%', 
                          height: 'auto', 
                          display: 'block'
                        }} 
                      />
                      <div style={{ 
                        padding: '1rem',
                        fontSize: '0.875rem',
                        color: '#166534',
                        backgroundColor: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                        fontWeight: '600',
                        textAlign: 'center'
                      }}>
                        🎨 Image {i + 1}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
