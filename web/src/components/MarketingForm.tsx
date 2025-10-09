import { useCallback, useMemo, useState } from 'react';

type AudienceTarget = {
  age_range: string;
  gender: string;
  location: string;
  interests: string[];
  platform_preference: string;
};

type BrandAssets = {
  primary_color: string;
  secondary_color: string;
  logo_url?: string;
  brand_voice: string;
  tone: string;
  brand_values: string[];
};

type JobResponse = {
  job_id: string;
  status: string;
  progress: number;
  result?: {
    multimodal_copies: Array<{
      channel: string;
      primary: string;
      variations: string[];
      engagement_score: number;
      optimization_tips: string[];
    }>;
    images: string[];
    performance_predictions: Array<{
      channel: string;
      predicted_engagement: number;
      best_posting_time: string;
      estimated_reach: string;
    }>;
    campaign_insights: {
      overall_engagement_score: number;
      best_performing_channel: string;
      total_variations_generated: number;
      recommendations: string[];
    };
    meta?: Record<string, unknown>;
  } | null;
};

const API_BASE = 'http://localhost:8000';

export default function MarketingForm() {
  const [title, setTitle] = useState('');
  const [brief, setBrief] = useState('');
  const [channels, setChannels] = useState<string[]>([]);
  const [brandFile, setBrandFile] = useState<File | null>(null);

  // New multimodal features state
  const [audienceTarget, setAudienceTarget] = useState<AudienceTarget>({
    age_range: '25-45',
    gender: 'all',
    location: 'global',
    interests: [],
    platform_preference: 'all'
  });
  
  const [brandAssets, setBrandAssets] = useState<BrandAssets>({
    primary_color: '#10b981',
    secondary_color: '#059669',
    brand_voice: 'professional',
    tone: 'neutral',
    brand_values: ['quality', 'innovation', 'trust']
  });
  
  const [contentLength, setContentLength] = useState('medium');
  const [generateVariations, setGenerateVariations] = useState(true);
  const [includeEmoji, setIncludeEmoji] = useState(false);

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
        body: JSON.stringify({ 
          title, 
          brief, 
          brand_profile_id, 
          channels,
          audience_target: audienceTarget,
          brand_assets: brandAssets,
          content_length: contentLength,
          generate_variations: generateVariations,
          include_emoji: includeEmoji
        }),
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
  }, [title, brief, channels, brandProfileIdPromise, audienceTarget, brandAssets, contentLength, generateVariations, includeEmoji]);

  return (
    <div style={{ 
      maxWidth: '90vw', 
      width: '100%',
      margin: '0 auto',
      padding: '0 2rem'
    }}>
      <form onSubmit={submit} style={{ 
        backgroundColor: 'white',
        padding: '4rem',
        borderRadius: '32px',
        boxShadow: '0 30px 60px rgba(0, 0, 0, 0.15), 0 15px 30px rgba(0, 0, 0, 0.1)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        backdropFilter: 'blur(20px)',
        background: 'rgba(255, 255, 255, 0.98)',
        position: 'relative',
        overflow: 'hidden',
        minHeight: '75vh'
      }}>
        <div style={{ display: 'grid', gap: '2.5rem' }}>
          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '1.25rem', 
              fontWeight: '700', 
              color: '#1f2937',
              marginBottom: '1rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Campaign Title
            </label>
            <input 
              value={title} 
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTitle(e.target.value)} 
              required 
              placeholder="Summer Sale" 
              style={{ 
                width: '100%',
                padding: '1.5rem', 
                border: '2px solid #e5e7eb', 
                borderRadius: '16px',
                fontSize: '1.25rem',
                outline: 'none',
                transition: 'all 0.3s ease',
                boxSizing: 'border-box',
                backgroundColor: '#f8fafc',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#10b981';
                e.target.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1), 0 4px 12px rgba(0, 0, 0, 0.1)';
                e.target.style.backgroundColor = '#ffffff';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#e5e7eb';
                e.target.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)';
                e.target.style.backgroundColor = '#f8fafc';
              }}
            />
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '1.25rem', 
              fontWeight: '700', 
              color: '#1f2937',
              marginBottom: '1rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Campaign Brief
            </label>
            <textarea 
              value={brief} 
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setBrief(e.target.value)} 
              required 
              placeholder="50% off all items" 
              rows={4} 
              style={{ 
                width: '100%',
                padding: '1.5rem', 
                border: '2px solid #e5e7eb', 
                borderRadius: '16px',
                fontSize: '1.25rem',
                outline: 'none',
                transition: 'all 0.3s ease',
                resize: 'vertical',
                boxSizing: 'border-box',
                backgroundColor: '#f8fafc',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#10b981';
                e.target.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1), 0 4px 12px rgba(0, 0, 0, 0.1)';
                e.target.style.backgroundColor = '#ffffff';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#e5e7eb';
                e.target.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)';
                e.target.style.backgroundColor = '#f8fafc';
              }}
            />
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '1.25rem', 
              fontWeight: '700', 
              color: '#1f2937',
              marginBottom: '1rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Marketing Channels
            </label>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '1.5rem',
              marginBottom: '1rem'
            }}>
              {[
                { 
                  value: 'email', 
                  label: 'Email Marketing', 
                  icon: '@',
                  iconStyle: { 
                    color: '#4285f4', 
                    fontSize: '1.8rem', 
                    fontWeight: 'bold',
                    fontFamily: 'Arial, sans-serif'
                  }
                },
                { 
                  value: 'instagram', 
                  label: 'Instagram', 
                  icon: (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <defs>
                        <linearGradient id="instagram-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#833ab4"/>
                          <stop offset="50%" stopColor="#fd1d1d"/>
                          <stop offset="100%" stopColor="#fcb045"/>
                        </linearGradient>
                      </defs>
                      <rect x="2" y="2" width="20" height="20" rx="5" ry="5" fill="url(#instagram-gradient)"/>
                      <path d="m16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" fill="white"/>
                      <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  ),
                  iconStyle: { 
                    fontSize: '1.8rem',
                    width: '24px',
                    height: '24px'
                  }
                },
                { 
                  value: 'facebook', 
                  label: 'Facebook', 
                  icon: 'f',
                  iconStyle: { 
                    color: '#1877f2', 
                    fontSize: '1.8rem', 
                    fontWeight: 'bold',
                    fontFamily: 'Arial, sans-serif'
                  }
                },
                { 
                  value: 'twitter', 
                  label: 'X (Twitter)', 
                  icon: '𝕏',
                  iconStyle: { 
                    color: '#000000', 
                    fontSize: '1.8rem', 
                    fontWeight: 'bold'
                  }
                }
              ].map((channel) => (
                <label key={channel.value} style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '1.5rem',
                  border: channels.includes(channel.value) ? '2px solid #10b981' : '2px solid #e5e7eb',
                  borderRadius: '12px',
                  backgroundColor: channels.includes(channel.value) ? '#f0fdf4' : '#f8fafc',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: channels.includes(channel.value) ? '0 4px 15px rgba(16, 185, 129, 0.2)' : '0 2px 4px rgba(0, 0, 0, 0.05)'
                }}>
                  <input
                    type="checkbox"
                    checked={channels.includes(channel.value)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setChannels([...channels, channel.value]);
                      } else {
                        setChannels(channels.filter(c => c !== channel.value));
                      }
                    }}
                    style={{ marginRight: '0.75rem', transform: 'scale(1.2)' }}
                  />
                  <span style={{ marginRight: '0.75rem', ...channel.iconStyle }}>{channel.icon}</span>
                  <span style={{ 
                    fontSize: '1.25rem', 
                    fontWeight: '600',
                    color: channels.includes(channel.value) ? '#166534' : '#374151'
                  }}>
                    {channel.label}
                  </span>
                </label>
              ))}
            </div>
            <p style={{ 
              fontSize: '0.875rem', 
              color: '#6b7280',
              margin: '0.5rem 0 0 0',
              fontWeight: '500',
              textAlign: 'center'
            }}>
              Click to select multiple channels
            </p>
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '1.25rem', 
              fontWeight: '700', 
              color: '#1f2937',
              marginBottom: '1rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Brand Profile (Optional)
            </label>
            <input 
              type="file" 
              accept="application/json" 
              onChange={onFileChange}
              style={{
                width: '100%',
                padding: '1.5rem',
                border: '2px solid #e5e7eb',
                borderRadius: '16px',
                fontSize: '1rem',
                outline: 'none',
                transition: 'all 0.3s ease',
                boxSizing: 'border-box',
                backgroundColor: '#f8fafc',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
                cursor: 'pointer'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#10b981';
                e.target.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1), 0 4px 12px rgba(0, 0, 0, 0.1)';
                e.target.style.backgroundColor = '#ffffff';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#e5e7eb';
                e.target.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)';
                e.target.style.backgroundColor = '#f8fafc';
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

          {/* Audience Targeting Section */}
          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '1.25rem', 
              fontWeight: '700', 
              color: '#1f2937',
              marginBottom: '1rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Target Audience
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>
                  Age Range
                </label>
                <select 
                  value={audienceTarget.age_range} 
                  onChange={(e) => setAudienceTarget({...audienceTarget, age_range: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    backgroundColor: '#f8fafc'
                  }}
                >
                  <option value="18-24">18-24</option>
                  <option value="25-34">25-34</option>
                  <option value="35-44">35-44</option>
                  <option value="45-54">45-54</option>
                  <option value="55+">55+</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>
                  Gender
                </label>
                <select 
                  value={audienceTarget.gender} 
                  onChange={(e) => setAudienceTarget({...audienceTarget, gender: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    backgroundColor: '#f8fafc'
                  }}
                >
                  <option value="all">All</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="non-binary">Non-binary</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>
                  Location
                </label>
                <select 
                  value={audienceTarget.location} 
                  onChange={(e) => setAudienceTarget({...audienceTarget, location: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    backgroundColor: '#f8fafc'
                  }}
                >
                  <option value="global">Global</option>
                  <option value="united-states">United States</option>
                  <option value="canada">Canada</option>
                  <option value="united-kingdom">United Kingdom</option>
                  <option value="australia">Australia</option>
                  <option value="germany">Germany</option>
                  <option value="france">France</option>
                  <option value="spain">Spain</option>
                  <option value="italy">Italy</option>
                  <option value="japan">Japan</option>
                  <option value="south-korea">South Korea</option>
                  <option value="china">China</option>
                  <option value="india">India</option>
                  <option value="brazil">Brazil</option>
                  <option value="mexico">Mexico</option>
                  <option value="argentina">Argentina</option>
                  <option value="south-africa">South Africa</option>
                  <option value="nigeria">Nigeria</option>
                  <option value="europe">Europe</option>
                  <option value="asia">Asia</option>
                  <option value="latin-america">Latin America</option>
                  <option value="middle-east">Middle East</option>
                  <option value="africa">Africa</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>
                  Interests
                </label>
                <input 
                  type="text"
                  value={audienceTarget.interests.join(', ')}
                  onChange={(e) => setAudienceTarget({...audienceTarget, interests: e.target.value.split(',').map(i => i.trim()).filter(i => i)})}
                  placeholder="e.g., technology, fitness, travel"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    backgroundColor: '#f8fafc'
                  }}
                />
              </div>
            </div>
          </div>

          {/* Brand Assets Section */}
          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '1.25rem', 
              fontWeight: '700', 
              color: '#1f2937',
              marginBottom: '1rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Brand Assets
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>
                  Brand Voice
                </label>
                <select 
                  value={brandAssets.brand_voice} 
                  onChange={(e) => setBrandAssets({...brandAssets, brand_voice: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    backgroundColor: '#f8fafc'
                  }}
                >
                  <option value="professional">Professional</option>
                  <option value="casual">Casual</option>
                  <option value="humorous">Humorous</option>
                  <option value="friendly">Friendly</option>
                  <option value="authoritative">Authoritative</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>
                  Tone
                </label>
                <select 
                  value={brandAssets.tone} 
                  onChange={(e) => setBrandAssets({...brandAssets, tone: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    backgroundColor: '#f8fafc'
                  }}
                >
                  <option value="formal">Formal</option>
                  <option value="neutral">Neutral</option>
                  <option value="casual">Casual</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>
                  Primary Color
                </label>
                <input 
                  type="color"
                  value={brandAssets.primary_color}
                  onChange={(e) => setBrandAssets({...brandAssets, primary_color: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    height: '3rem'
                  }}
                />
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>
                  Content Length
                </label>
                <select 
                  value={contentLength} 
                  onChange={(e) => setContentLength(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    backgroundColor: '#f8fafc'
                  }}
                >
                  <option value="short">Short</option>
                  <option value="medium">Medium</option>
                  <option value="long">Long</option>
                </select>
              </div>
            </div>
          </div>

          {/* Advanced Options */}
          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '1.25rem', 
              fontWeight: '700', 
              color: '#1f2937',
              marginBottom: '1rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Advanced Options
            </label>
            <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input 
                  type="checkbox"
                  checked={generateVariations}
                  onChange={(e) => setGenerateVariations(e.target.checked)}
                  style={{ transform: 'scale(1.2)' }}
                />
                <span style={{ fontSize: '1rem', fontWeight: '500' }}>Generate A/B Test Variations</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input 
                  type="checkbox"
                  checked={includeEmoji}
                  onChange={(e) => setIncludeEmoji(e.target.checked)}
                  style={{ transform: 'scale(1.2)' }}
                />
                <span style={{ fontSize: '1rem', fontWeight: '500' }}>Include Emojis (Minimal)</span>
              </label>
            </div>
          </div>

          <button 
            type="submit" 
            disabled={isSubmitting} 
            style={{ 
              width: '100%',
              padding: '2rem 3rem', 
              borderRadius: '20px', 
              border: 'none',
              background: isSubmitting 
                ? 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)' 
                : 'linear-gradient(135deg, #10b981 0%, #059669 100%)', 
              color: 'white', 
              fontSize: '1.5rem',
              fontWeight: '700',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              marginTop: '3rem',
              boxShadow: isSubmitting 
                ? '0 4px 15px rgba(156, 163, 175, 0.4)' 
                : '0 12px 35px rgba(16, 185, 129, 0.5)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              position: 'relative',
              overflow: 'hidden'
            }}
            onMouseEnter={(e) => {
              if (!isSubmitting) {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 15px 40px rgba(16, 185, 129, 0.6)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isSubmitting) {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 12px 35px rgba(16, 185, 129, 0.5)';
              }
            }}
          >
            <span style={{ position: 'relative', zIndex: 1 }}>
              {isSubmitting ? 'Generating Content...' : 'Generate Marketing Content'}
            </span>
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
              margin: '0 0 1.5rem 0',
              textAlign: 'center'
            }}>
              Generation Results
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
                <div style={{ fontSize: '0.875rem', color: '#166534', marginBottom: '0.5rem', fontWeight: '600' }}>Job ID</div>
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
                  Status
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
                <div style={{ fontSize: '0.875rem', color: '#166534', marginBottom: '0.5rem', fontWeight: '600' }}>Progress</div>
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
                  margin: '0 0 1.5rem 0',
                  textAlign: 'center'
                }}>
                  Generated Content
                </h3>
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  {job.result.multimodal_copies ? job.result.multimodal_copies.map((copy, i) => (
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
                        marginBottom: '1rem',
                        fontWeight: '700',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em'
                      }}>
                        {copy.channel} (Score: {copy.engagement_score})
                      </div>
                      <div style={{ 
                        fontSize: '1.25rem', 
                        lineHeight: '1.6',
                        whiteSpace: 'pre-wrap',
                        color: '#14532d',
                        fontWeight: '500',
                        marginBottom: '1rem'
                      }}>
                        {copy.primary}
                      </div>
                      {copy.variations && copy.variations.length > 0 && (
                        <div style={{ marginBottom: '1rem' }}>
                          <div style={{ fontSize: '0.875rem', color: '#166534', fontWeight: '600', marginBottom: '0.5rem' }}>
                            Variations:
                          </div>
                          {copy.variations.map((variation, vIndex) => (
                            <div key={vIndex} style={{ 
                              fontSize: '1rem', 
                              color: '#14532d',
                              padding: '0.75rem',
                              background: 'rgba(255, 255, 255, 0.5)',
                              borderRadius: '8px',
                              marginBottom: '0.5rem'
                            }}>
                              <strong>Variation {vIndex + 1}:</strong><br />
                              {variation}
                            </div>
                          ))}
                        </div>
                      )}
                      {copy.optimization_tips && copy.optimization_tips.length > 0 && (
                        <div>
                          <div style={{ fontSize: '0.875rem', color: '#166534', fontWeight: '600', marginBottom: '0.5rem' }}>
                            Tips:
                          </div>
                          <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                            {copy.optimization_tips.map((tip, tIndex) => (
                              <li key={tIndex} style={{ fontSize: '0.875rem', color: '#166534' }}>{tip}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )) : job.result.copy.map((c, i) => (
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
                        marginBottom: '1rem',
                        fontWeight: '700',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em'
                      }}>
                        Channel {i + 1}
                      </div>
                      <div style={{ 
                        fontSize: '1.25rem', 
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
                  margin: '0 0 1.5rem 0',
                  textAlign: 'center'
                }}>
                  Generated Images
                </h3>
                <div style={{ 
                  display: 'flex', 
                  flexWrap: 'wrap',
                  justifyContent: 'center',
                  gap: '1.5rem'
                }}>
                  {job.result.images.map((src, i) => (
                    <div key={i} style={{ 
                      border: '3px solid #10b981',
                      borderRadius: '20px',
                      overflow: 'hidden',
                      backgroundColor: 'white',
                      boxShadow: '0 8px 25px rgba(16, 185, 129, 0.2)',
                      transition: 'transform 0.3s ease',
                      width: '400px',
                      maxWidth: '100%',
                      margin: '0 auto'
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
                        Image {i + 1}
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
