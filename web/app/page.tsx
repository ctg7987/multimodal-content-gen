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
    <div>
    <form onSubmit={submit} style={{ display: 'grid', gap: '0.75rem', padding: '1rem', border: '1px solid #ddd', borderRadius: 8 }}>
        <label style={{ display: 'grid', gap: 4 }}>
          <span>Title</span>
      <input value={title} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTitle(e.target.value)} required placeholder="Summer Sale" style={{ padding: 8, border: '1px solid #ccc', borderRadius: 6 }} />
        </label>
        <label style={{ display: 'grid', gap: 4 }}>
          <span>Brief</span>
      <textarea value={brief} onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setBrief(e.target.value)} required placeholder="50% off all items" rows={4} style={{ padding: 8, border: '1px solid #ccc', borderRadius: 6 }} />
        </label>
        <label style={{ display: 'grid', gap: 4 }}>
          <span>Channels</span>
          <select multiple value={channels} onChange={onChannelChange} style={{ padding: 8, border: '1px solid #ccc', borderRadius: 6, height: 100 }}>
            <option value="email">Email</option>
            <option value="instagram">Instagram</option>
            <option value="facebook">Facebook</option>
            <option value="twitter">Twitter</option>
          </select>
          <small>Use Cmd/Ctrl+Click to select multiple</small>
        </label>
        <label style={{ display: 'grid', gap: 4 }}>
          <span>Brand Profile (JSON)</span>
          <input type="file" accept="application/json" onChange={onFileChange} />
          <small>Optional: we'll read an "id" field from this file</small>
        </label>
        <button type="submit" disabled={isSubmitting} style={{ padding: '0.6rem 1rem', borderRadius: 6, border: '1px solid #222', background: '#111', color: '#fff', cursor: 'pointer' }}>
          {isSubmitting ? 'Generating…' : 'Generate'}
        </button>
      </form>

      {error && (
        <div style={{ marginTop: '1rem', color: 'crimson' }}>Error: {error}</div>
      )}

      {job && (
        <div style={{ marginTop: '1.5rem' }}>
          <h2>Job</h2>
          <div style={{ fontSize: 14, color: '#555' }}>id: {job.job_id}</div>
          <div>Status: {job.status}</div>
          <div>Progress: {job.progress}%</div>

          {job.result && (
            <div style={{ marginTop: '1rem', display: 'grid', gap: '1rem' }}>
              <div>
                <h3 style={{ marginBottom: 8 }}>Copy</h3>
                <ul>
                  {job.result.copy.map((c, i) => (
                    <li key={i} style={{ marginBottom: 6 }}>{c}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 style={{ marginBottom: 8 }}>Images</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 12 }}>
                  {job.result.images.map((src, i) => (
                    <img key={i} src={src} alt={`result-${i}`} style={{ width: '100%', height: 'auto', borderRadius: 8, border: '1px solid #eee' }} />
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
