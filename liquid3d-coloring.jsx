import React, { useState, useEffect, useRef } from 'react';
import { Plus, Search, Grid, Network, Clock, Palette, Droplets } from 'lucide-react';

const ArtifactRegistry = () => {
  const [view, setView] = useState('gallery');
  const [selectedArtifact, setSelectedArtifact] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const canvasRef = useRef(null);
  
  // Artifact type color mapping
  const typeColors = {
    code: '#00D4FF',
    docs: '#FFB800',
    image: '#FF006E',
    dataset: '#8B00FF',
    schema: '#00FF88',
    model: '#FF3366',
    policy: '#4169E1',
    log: '#C0C0C0'
  };

  // Sample artifacts with relationships
  const [artifacts, setArtifacts] = useState([
    {
      id: 'art_001',
      title: 'User Authentication Module',
      type: 'code',
      version: 'v1.2.0',
      created_at: '2026-01-10T14:30:00Z',
      created_by: 'JMR0824197846902',
      source_ai: 'Claude',
      status: 'stable',
      notes: 'JWT-based auth with refresh tokens',
      tags: ['security', 'backend'],
      relationships: []
    },
    {
      id: 'art_002',
      title: 'Database Schema v3',
      type: 'schema',
      version: 'v3.0.1',
      created_at: '2026-01-12T09:15:00Z',
      created_by: 'JMR0824197846902',
      source_ai: 'ChatGPT',
      status: 'stable',
      notes: 'PostgreSQL schema with audit tables',
      tags: ['database', 'infrastructure'],
      relationships: [{ type: 'derived_from', target: 'art_001' }]
    },
    {
      id: 'art_003',
      title: 'API Documentation',
      type: 'docs',
      version: 'v2.1.0',
      created_at: '2026-01-13T16:45:00Z',
      created_by: 'JMR0824197846902',
      source_ai: 'Claude',
      status: 'draft',
      notes: 'OpenAPI 3.0 specification',
      tags: ['documentation', 'api'],
      relationships: [{ type: 'related_to', target: 'art_001' }]
    },
    {
      id: 'art_004',
      title: 'User Dataset (Jan 2026)',
      type: 'dataset',
      version: 'v1.0.0',
      created_at: '2026-01-14T11:20:00Z',
      created_by: 'JMR0824197846902',
      source_ai: 'human',
      status: 'stable',
      notes: 'Anonymized user behavior data',
      tags: ['analytics', 'privacy'],
      relationships: [{ type: 'derived_from', target: 'art_002' }]
    },
    {
      id: 'art_005',
      title: 'ML Training Model',
      type: 'model',
      version: 'v0.9.2',
      created_at: '2026-01-15T08:00:00Z',
      created_by: 'JMR0824197846902',
      source_ai: 'Claude',
      status: 'draft',
      notes: 'User behavior prediction model',
      tags: ['machine-learning', 'experimental'],
      relationships: [{ type: 'derived_from', target: 'art_004' }]
    },
    {
      id: 'art_006',
      title: 'Brand Logo Assets',
      type: 'image',
      version: 'v1.0.0',
      created_at: '2026-01-11T13:30:00Z',
      created_by: 'JMR0824197846902',
      source_ai: 'human',
      status: 'stable',
      notes: 'SVG and PNG logo variations',
      tags: ['design', 'branding'],
      relationships: []
    }
  ]);

  // Liquid background animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    let particles = [];
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 3 + 1,
        color: Object.values(typeColors)[Math.floor(Math.random() * Object.values(typeColors).length)]
      });
    }
    
    const animate = () => {
      ctx.fillStyle = 'rgba(10, 10, 20, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      particles.forEach((p, i) => {
        p.x += p.vx;
        p.y += p.vy;
        
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        
        ctx.beginPath();
        const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.radius * 3);
        gradient.addColorStop(0, p.color + 'AA');
        gradient.addColorStop(1, p.color + '00');
        ctx.fillStyle = gradient;
        ctx.arc(p.x, p.y, p.radius * 3, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw connections
        particles.slice(i + 1).forEach(p2 => {
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist < 150) {
            ctx.beginPath();
            ctx.strokeStyle = p.color + Math.floor((1 - dist / 150) * 30).toString(16).padStart(2, '0');
            ctx.lineWidth = 1;
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        });
      });
      
      requestAnimationFrame(animate);
    };
    
    animate();
  }, []);

  const getStatusColor = (status) => {
    switch(status) {
      case 'stable': return '#00FF88';
      case 'draft': return '#FFB800';
      case 'archived': return '#808080';
      case 'deprecated': return '#FF3366';
      default: return '#FFFFFF';
    }
  };

  const filteredArtifacts = artifacts.filter(a => 
    a.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="relative w-full h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
      {/* Liquid Background Canvas */}
      <canvas ref={canvasRef} className="absolute inset-0 z-0" />
      
      {/* Main Interface */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Header */}
        <header className="backdrop-blur-xl bg-black/30 border-b border-white/10 p-4">
          <div className="flex items-center justify-between max-w-7xl mx-auto">
            <div className="flex items-center gap-3">
              <Droplets className="w-8 h-8 text-cyan-400" />
              <h1 className="text-2xl font-bold text-white">Artifact Registry</h1>
              <span className="text-xs text-cyan-400 px-2 py-1 rounded bg-cyan-400/20">
                Project ELM369
              </span>
            </div>
            
            {/* Search */}
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search artifacts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/50"
                />
              </div>
              
              <button className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-600 text-white font-medium flex items-center gap-2 transition-all">
                <Plus className="w-4 h-4" />
                New Artifact
              </button>
            </div>
          </div>
        </header>

        {/* View Toggle */}
        <div className="backdrop-blur-xl bg-black/20 border-b border-white/10 p-3">
          <div className="flex gap-2 max-w-7xl mx-auto">
            {[
              { id: 'gallery', icon: Grid, label: 'Gallery' },
              { id: 'network', icon: Network, label: 'Network' },
              { id: 'timeline', icon: Clock, label: 'Timeline' },
              { id: 'palette', icon: Palette, label: 'Libraries' }
            ].map(({ id, icon: Icon, label }) => (
              <button
                key={id}
                onClick={() => setView(id)}
                className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${
                  view === id
                    ? 'bg-cyan-500 text-white'
                    : 'bg-white/10 text-gray-300 hover:bg-white/20'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-7xl mx-auto">
            {view === 'gallery' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredArtifacts.map(artifact => (
                  <div
                    key={artifact.id}
                    onClick={() => setSelectedArtifact(artifact)}
                    className="group relative backdrop-blur-xl bg-black/40 rounded-2xl p-6 border-2 cursor-pointer transition-all hover:scale-105 hover:shadow-2xl"
                    style={{
                      borderColor: typeColors[artifact.type] + '60',
                      boxShadow: `0 0 30px ${typeColors[artifact.type]}20`
                    }}
                  >
                    {/* Color Indicator */}
                    <div 
                      className="absolute top-0 left-0 w-full h-2 rounded-t-2xl"
                      style={{
                        background: `linear-gradient(90deg, ${typeColors[artifact.type]}, ${typeColors[artifact.type]}80)`
                      }}
                    />
                    
                    {/* Status Badge */}
                    <div className="flex items-center justify-between mb-3">
                      <span 
                        className="text-xs px-2 py-1 rounded-full font-medium"
                        style={{
                          backgroundColor: getStatusColor(artifact.status) + '20',
                          color: getStatusColor(artifact.status)
                        }}
                      >
                        {artifact.status}
                      </span>
                      <span className="text-xs text-gray-400">{artifact.version}</span>
                    </div>

                    {/* Title */}
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-cyan-400 transition-colors">
                      {artifact.title}
                    </h3>

                    {/* Type Badge */}
                    <div className="flex items-center gap-2 mb-3">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: typeColors[artifact.type] }}
                      />
                      <span className="text-sm text-gray-300 capitalize">{artifact.type}</span>
                    </div>

                    {/* Notes */}
                    <p className="text-sm text-gray-400 mb-4 line-clamp-2">
                      {artifact.notes}
                    </p>

                    {/* Tags */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {artifact.tags.map(tag => (
                        <span 
                          key={tag}
                          className="text-xs px-2 py-1 rounded bg-white/10 text-gray-300"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>

                    {/* Metadata */}
                    <div className="text-xs text-gray-500 space-y-1 border-t border-white/10 pt-3">
                      <div>Created: {new Date(artifact.created_at).toLocaleDateString()}</div>
                      <div>Source: {artifact.source_ai}</div>
                      {artifact.relationships.length > 0 && (
                        <div className="flex items-center gap-1">
                          <Network className="w-3 h-3" />
                          {artifact.relationships.length} connection{artifact.relationships.length !== 1 ? 's' : ''}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {view === 'network' && (
              <div className="backdrop-blur-xl bg-black/40 rounded-2xl p-8 border border-white/20">
                <h2 className="text-2xl font-bold text-white mb-6">Relationship Network</h2>
                <div className="relative h-96 flex items-center justify-center">
                  {/* Simple network visualization */}
                  <svg className="w-full h-full">
                    {artifacts.map((artifact, i) => {
                      const angle = (i / artifacts.length) * Math.PI * 2;
                      const x = 300 + Math.cos(angle) * 150;
                      const y = 200 + Math.sin(angle) * 150;
                      
                      return (
                        <g key={artifact.id}>
                          {artifact.relationships.map(rel => {
                            const targetIndex = artifacts.findIndex(a => a.id === rel.target);
                            if (targetIndex === -1) return null;
                            const targetAngle = (targetIndex / artifacts.length) * Math.PI * 2;
                            const tx = 300 + Math.cos(targetAngle) * 150;
                            const ty = 200 + Math.sin(targetAngle) * 150;
                            
                            return (
                              <line
                                key={`${artifact.id}-${rel.target}`}
                                x1={x}
                                y1={y}
                                x2={tx}
                                y2={ty}
                                stroke={typeColors[artifact.type]}
                                strokeWidth="2"
                                opacity="0.4"
                              />
                            );
                          })}
                          <circle
                            cx={x}
                            cy={y}
                            r="20"
                            fill={typeColors[artifact.type]}
                            opacity="0.8"
                            className="cursor-pointer hover:opacity-100"
                            onClick={() => setSelectedArtifact(artifact)}
                          />
                          <text
                            x={x}
                            y={y + 35}
                            textAnchor="middle"
                            className="text-xs fill-white"
                          >
                            {artifact.type}
                          </text>
                        </g>
                      );
                    })}
                  </svg>
                </div>
              </div>
            )}

            {view === 'timeline' && (
              <div className="backdrop-blur-xl bg-black/40 rounded-2xl p-8 border border-white/20">
                <h2 className="text-2xl font-bold text-white mb-6">Timeline</h2>
                <div className="space-y-4">
                  {[...artifacts].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).map(artifact => (
                    <div 
                      key={artifact.id}
                      className="flex items-center gap-4 p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-all cursor-pointer"
                      onClick={() => setSelectedArtifact(artifact)}
                    >
                      <div 
                        className="w-12 h-12 rounded-full flex items-center justify-center"
                        style={{ backgroundColor: typeColors[artifact.type] + '40' }}
                      >
                        <div 
                          className="w-6 h-6 rounded-full"
                          style={{ backgroundColor: typeColors[artifact.type] }}
                        />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-white">{artifact.title}</h3>
                        <p className="text-sm text-gray-400">{artifact.notes}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-300">{artifact.version}</div>
                        <div className="text-xs text-gray-500">
                          {new Date(artifact.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {view === 'palette' && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {Object.entries(typeColors).map(([type, color]) => {
                  const typeArtifacts = artifacts.filter(a => a.type === type);
                  return (
                    <div 
                      key={type}
                      className="backdrop-blur-xl bg-black/40 rounded-2xl p-6 border-2 transition-all hover:scale-105"
                      style={{
                        borderColor: color + '60',
                        boxShadow: `0 0 30px ${color}20`
                      }}
                    >
                      <div 
                        className="w-full h-24 rounded-lg mb-4"
                        style={{
                          background: `linear-gradient(135deg, ${color}, ${color}80)`
                        }}
                      />
                      <h3 className="text-lg font-bold text-white capitalize mb-2">{type}</h3>
                      <p className="text-2xl font-bold" style={{ color }}>
                        {typeArtifacts.length}
                      </p>
                      <p className="text-xs text-gray-400">artifact{typeArtifacts.length !== 1 ? 's' : ''}</p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Detail Modal */}
      {selectedArtifact && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm"
          onClick={() => setSelectedArtifact(null)}
        >
          <div 
            className="backdrop-blur-xl bg-black/80 rounded-2xl p-8 max-w-2xl w-full border-2 max-h-[80vh] overflow-auto"
            style={{
              borderColor: typeColors[selectedArtifact.type] + '80',
              boxShadow: `0 0 60px ${typeColors[selectedArtifact.type]}40`
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-3xl font-bold text-white mb-2">{selectedArtifact.title}</h2>
                <div className="flex items-center gap-3">
                  <span 
                    className="px-3 py-1 rounded-full text-sm font-medium"
                    style={{
                      backgroundColor: typeColors[selectedArtifact.type] + '20',
                      color: typeColors[selectedArtifact.type]
                    }}
                  >
                    {selectedArtifact.type}
                  </span>
                  <span className="text-gray-400">{selectedArtifact.version}</span>
                  <span 
                    className="px-2 py-1 rounded text-xs"
                    style={{
                      backgroundColor: getStatusColor(selectedArtifact.status) + '20',
                      color: getStatusColor(selectedArtifact.status)
                    }}
                  >
                    {selectedArtifact.status}
                  </span>
                </div>
              </div>
              <button 
  