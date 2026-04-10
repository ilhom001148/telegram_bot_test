import React, { useState, useEffect } from 'react';

const API_URL = window.location.port === '5173' || window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' ? 'http://127.0.0.1:8000' : '';

// Professional SVG Icons
const Icons = {
  Dashboard: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/></svg>,
  Training: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3zM3.88 9L12 4.57 20.12 9 12 13.43 3.88 9zM12 17l-7-3.82V17l7 3.82 7-3.82v-3.82l-7 3.82z"/></svg>,
  History: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg>,
  Groups: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>,
  Settings: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>,
  Profile: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>,
  Logout: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>,
  Warning: () => <svg style={{width:40, height:40}} viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>,
  Database: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 4.24 2 7c0 2.23 3.12 4.19 7.42 4.8.44.06.89.1 1.34.13.41-.02.82-.05 1.24-.09C16.88 11.2 20 9.23 20 7c0-2.76-4.48-5-10-5zm0 8.5c-.82 0-1.61-.06-2.37-.15-.45-.05-.88-.13-1.29-.22C5.07 9.8 2 8.52 2 7v3c0 2.76 4.48 5 10 5s10-2.24 10-5V7c0 1.52-3.07 2.8-6.34 3.13-.41.09-.84.17-1.29.22-.76.09-1.55.15-2.37.15zm0 5c-.82 0-1.61-.06-2.37-.15-.45-.05-.88-.13-1.29-.22C5.07 14.8 2 13.52 2 12v3c0 2.76 4.48 5 10 5s10-2.24 10-5v-3c0 1.52-3.07 2.8-6.34 3.13-.41.09-.84.17-1.29.22-.76.09-1.55.15-2.37.15zM22 7c0-2.76-4.48-5-10-5S2 4.24 2 7v10c0 2.76 4.48 5 10 5s10-2.24 10-5V7zm-10 8c-4.42 0-8-1.79-8-4s3.58-4 8-4 8 1.79 8 4-3.58 4-8 4zm0-6c-3.31 0-6 1.34-6 3s2.69 3 6 3 6-1.34 6-3-2.69-3-6-3z" opacity=".3"/><path d="M12 2C6.48 2 2 4.24 2 7v10c0 2.76 4.48 5 10 5s10-2.24 10-5V7c0-2.76-4.48-5-10-5zm0 2c4.42 0 8 1.79 8 4s-3.58 4-8 4-8-1.79-8-4 3.58-4 8-4zm0 13c-4.42 0-8-1.79-8-4v-3.08c1.61 1.07 4.54 1.74 8 1.74s6.39-.67 8-1.74V17c0 2.21-3.58 4-8 4zm0-5c-4.42 0-8-1.79-8-4V7.92C5.61 8.99 8.54 9.66 12 9.66s6.39-.67 8-1.74V8c0 2.21-3.58 4-8 4z"/></svg>,
  Bot: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M12 2c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm9 7h-4.9c-.3-.8-1.1-1.3-2.1-1.3h-4c-1 0-1.8.5-2.1 1.3H3c-1.1 0-2 .9-2 2v6c0 1.1.9 2 2 2h2v3c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2v-3h2c1.1 0 2-.9 2-2v-6c0-1.1-.9-2-2-2zM5 15H3v-4h2v4zm10 4H9v-3h6v3zm4-4h-2v-4h2v4z"/></svg>,
  Broadcast: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm8.94 11c-.46 0-.85-.28-.99-.7l-1.34-4.8c-.14-.5-.54-.88-1.04-1.02l-4.8-1.34c-.42-.14-.7-.53-.7-.99s.28-.85.7-.99l4.8-1.34c.5-.14.9-.52 1.04-1.02l1.34-4.8c.14-.42.53-.7.99-.7s.85.28.99.7l1.34 4.8c.14.5.54.88 1.04 1.02l4.8 1.34c.42.14.7.53.7.99s-.28.85-.7.99l-4.8 1.34c-.5.14-.9.52-1.04 1.02l-1.34 4.8c-.14.42-.53.7-.99.7z"/></svg>,
  Folder: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>,
  Telegram: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M9.78 18.65l.66-3.33L19.62 4.41c.21-.19.46-.3.73-.3.26 0 .52.1.72.3.4.4.4 1.04 0 1.44l-8.73 8.73 3.32 3.32c.39.39.39 1.02 0 1.41l-1.41 1.41c-.39.39-1.02.39-1.41 0l-3.33-3.32-3.32 3.32c-.39.39-1.02.39-1.41 0l-1.41-1.41c-.39-.39-.39-1.02 0-1.41l3.32-3.32z"/></svg>,
};

function ArchiveManager({ token }) {
  const [summaries, setSummaries] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/messages/archive/summary`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json())
      .then(data => { setSummaries(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [token]);

  const openFolder = (date) => {
    setSelectedDate(date);
    setDetailLoading(true);
    fetch(`${API_URL}/messages/archive/questions-by-date/${date}`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json())
      .then(data => { setQuestions(data); setDetailLoading(false); })
      .catch(() => setDetailLoading(false));
  };

  if (loading) return <div className="loader"></div>;

  return (
    <div style={{animation: 'fadeIn 0.5s ease-out'}}>
      {!selectedDate ? (
        <>
          <h2 className="header-title">Kunlik Arxiv (Savollar hisoboti)</h2>
          <div className="grid-cards" style={{gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '1.5rem'}}>
            {summaries.length > 0 ? summaries.map((s, i) => (
              <div key={i} className="glass-card archive-folder" onClick={() => openFolder(s.date)} 
                   style={{cursor:'pointer', transition:'transform 0.2s', textAlign:'center', position:'relative', overflow:'hidden'}}>
                <div style={{color:'var(--primary)', marginBottom:'1rem'}}><Icons.Folder /></div>
                <div style={{fontWeight:'bold', fontSize:'1.1rem', marginBottom:'0.5rem'}}>{s.date}</div>
                <div className="archive-stats" style={{fontSize:'0.8rem', color:'var(--text-muted)'}}>
                   <div className="flex-between" style={{marginBottom:'5px'}}><span>Jami:</span> <b>{s.total}</b></div>
                   <div className="flex-between" style={{color:'var(--success)', marginBottom:'5px'}}><span>Javob berildi:</span> <b>{s.answered}</b></div>
                   <div className="flex-between" style={{color: s.unanswered > 0 ? 'var(--danger)' : 'var(--text-muted)'}}><span>Kutilmoqda:</span> <b>{s.unanswered}</b></div>
                </div>
              </div>
            )) : <p style={{gridColumn:'1/-1', textAlign:'center', padding:'3rem', color:'var(--text-muted)'}}>Hozircha arxivda savollar mavjud emas.</p>}
          </div>
        </>
      ) : (
        <>
          <div className="flex-between" style={{marginBottom:'2rem'}}>
             <h2 className="header-title" style={{margin:0}}>{selectedDate} kungi savollar (Hisobot)</h2>
             <div style={{display:'flex', gap:'10px'}}>
               <button className="btn btn-sm" onClick={() => window.print()} style={{background:'var(--primary)'}}>
                 📄 PDF shaklida saqlash
               </button>
               <button className="btn btn-sm" onClick={() => setSelectedDate(null)}>⬅️ Orqaga</button>
             </div>
          </div>

          {detailLoading ? <div className="loader"></div> : (
            <div className="glass-card print-area">
              <div className="table-wrapper">
                <table>
                  <thead>
                     <tr>
                        <th style={{width:'80px'}}>Vaqt</th>
                        <th style={{width:'150px'}}>Kimdan</th>
                        <th>Savol matni</th>
                        <th>Javob</th>
                        <th style={{width:'120px'}}>Holati</th>
                     </tr>
                  </thead>
                  <tbody>
                    {questions.map(q => (
                      <tr key={q.id}>
                        <td style={{whiteSpace:'nowrap', fontSize:'0.8rem'}}>{q.created_at}</td>
                        <td>
                           <div style={{fontWeight:'600', fontSize:'0.9rem'}}>{q.full_name}</div>
                           <div style={{fontSize:'0.7rem', color:'var(--text-muted)'}}>@{q.username || 'anonim'}</div>
                        </td>
                        <td style={{fontSize:'0.9rem'}}>{q.telegram_app_link ? <a href={q.telegram_app_link} style={{color: 'inherit', textDecoration: 'none', borderBottom: '1px dashed currentColor'}} title="Telegram ilovasida ochish">{q.text}</a> : q.text}</td>
                        <td style={{fontSize:'0.9rem'}}>
                           {q.answer_text ? (
                              <div>
                                 <div style={{color:'var(--primary)', fontWeight:'600', fontSize:'0.7rem', textTransform:'uppercase', marginBottom:'4px'}}>
                                    {q.answered_by || 'Bot'} javobi:
                                 </div>
                                 {q.answer_text}
                              </div>
                           ) : <span style={{color:'var(--text-muted)', fontStyle:'italic'}}>Javobsiz</span>}
                        </td>
                        <td>
                           <span className={`badge ${q.is_answered ? 'badge-kb' : 'badge-unanswered'}`} style={{fontSize:'0.7rem'}}>
                              {q.is_answered ? 'Javob berilgan' : 'Kutilmoqda'}
                           </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
function ConfirmModal({ isOpen, title, text, onConfirm, onCancel }) {
  if (!isOpen) return null;
  return (
    <div className="modal-overlay">
      <div className="confirm-modal">
        <div className="modal-icon"><Icons.Warning /></div>
        <div className="modal-title">{title}</div>
        <div className="modal-text">{text}</div>
        <div className="modal-actions">
          <button className="modal-btn modal-btn-cancel" onClick={onCancel}>Yo'q</button>
          <button className="modal-btn modal-btn-confirm" onClick={() => { onConfirm(); onCancel(); }}>Ha, tasdiqlayman</button>
        </div>
      </div>
    </div>
  );
}

const SimpleBarChart = ({ data, colors = ['#6366f1', '#ec4899'] }) => {
  const [tooltip, setTooltip] = useState(null);
  if (!data || data.length === 0) return null;
  const maxVal = Math.max(...data.map(d => Math.max(d.messages, d.questions, 1)));

  return (
    <div style={{ position: 'relative' }}>
      {/* Tooltip */}
      {tooltip && (
        <div className="chart-tooltip" style={{ left: tooltip.x, top: tooltip.y }}>
          <div className="chart-tooltip-title">{tooltip.day}</div>
          <div className="chart-tooltip-row">
            <span className="chart-tooltip-dot" style={{ background: colors[0] }}></span>
            <span>Xabarlar:</span>
            <strong>{tooltip.messages}</strong>
          </div>
          <div className="chart-tooltip-row">
            <span className="chart-tooltip-dot" style={{ background: colors[1] }}></span>
            <span>Savollar:</span>
            <strong>{tooltip.questions}</strong>
          </div>
        </div>
      )}

      <div
        className="chart-container"
        style={{ height: '200px', display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: '8px', padding: '10px 0' }}
        onMouseLeave={() => setTooltip(null)}
      >
        {data.map((d, i) => (
          <div
            key={i}
            style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', position: 'relative' }}
            onMouseEnter={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              const parentRect = e.currentTarget.closest('.chart-container').getBoundingClientRect();
              setTooltip({
                day: d.day,
                messages: d.messages,
                questions: d.questions,
                x: rect.left - parentRect.left - 60,
                y: -90,
              });
            }}
          >
            {/* Y-axis value labels on top of bars */}
            <div style={{ width: '100%', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', gap: '3px', height: '160px' }}>
              {/* Messages bar */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-end', height: '100%' }}>
                {d.messages > 0 && (
                  <span style={{ fontSize: '0.6rem', color: colors[0], fontWeight: 700, marginBottom: '2px', opacity: 0.9 }}>
                    {d.messages}
                  </span>
                )}
                <div
                  style={{
                    width: '10px',
                    background: `linear-gradient(180deg, ${colors[0]}dd, ${colors[0]}88)`,
                    height: `${Math.max((d.messages / maxVal) * 100, d.messages > 0 ? 3 : 0)}%`,
                    borderRadius: '4px 4px 0 0',
                    transition: 'all 0.5s ease',
                    cursor: 'pointer',
                    boxShadow: `0 0 8px ${colors[0]}55`,
                  }}
                ></div>
              </div>

              {/* Questions bar */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-end', height: '100%' }}>
                {d.questions > 0 && (
                  <span style={{ fontSize: '0.6rem', color: colors[1], fontWeight: 700, marginBottom: '2px', opacity: 0.9 }}>
                    {d.questions}
                  </span>
                )}
                <div
                  style={{
                    width: '10px',
                    background: `linear-gradient(180deg, ${colors[1]}dd, ${colors[1]}88)`,
                    height: `${Math.max((d.questions / maxVal) * 100, d.questions > 0 ? 3 : 0)}%`,
                    borderRadius: '4px 4px 0 0',
                    transition: 'all 0.5s ease',
                    cursor: 'pointer',
                    boxShadow: `0 0 8px ${colors[1]}55`,
                  }}
                ></div>
              </div>
            </div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '6px' }}>{d.day}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

/* Tracking Mode Component */
function MonitoringManager({ token, showFlash }) {
  const [trackingMode, setTrackingMode] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/settings/`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json())
      .then(data => {
        setTrackingMode(data.tracking_mode === 'true');
        setLoading(false);
      });
  }, [token]);

  const toggleTracking = () => {
    const newValue = !trackingMode;
    setTrackingMode(newValue);
    fetch(`${API_URL}/settings/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ key: 'tracking_mode', value: newValue ? 'true' : 'false' })
    }).then(() => showFlash(`Rejim: ${newValue ? 'Faqat sanash' : 'Javob berish'}`));
  };

  if (loading) return <div className="loader"></div>;

  return (
    <>
      <h2 className="header-title">Bot Monitoringi</h2>
      <div className="glass-card" style={{maxWidth:'600px'}}>
         <div className="flex-between">
            <div>
               <h3 style={{marginBottom:'0.5rem'}}>Faqat sanash rejimi</h3>
               <p style={{fontSize:'0.85rem', color:'var(--text-muted)'}}>Ushbu rejim yoqilganda bot savollarni aniqlaydi va bazada sanaydi, lekin AI orqali javob qaytarmaydi.</p>
            </div>
            <label className="switch">
               <input type="checkbox" checked={trackingMode} onChange={toggleTracking} />
               <span className="slider round"></span>
            </label>
         </div>
      </div>
    </>
  );
}

/* Broadcast Manager Component */
function BroadcastManager({ token, showFlash }) {
  const [form, setForm] = useState({ text: '', target: 'all', group_id: '', scheduled_at: '' });
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/groups/`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(setGroups);
  }, [token]);

  const handleBroadcast = (e) => {
    e.preventDefault();
    if (!form.text.trim()) return;
    setLoading(true);
    fetch(`${API_URL}/admin/broadcast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ ...form, group_id: form.group_id ? parseInt(form.group_id) : null })
    })
    .then(res => res.json())
    .then(data => {
      setLoading(false);
      if (data.status === 'success') { showFlash(data.message); setForm({ ...form, text: '', scheduled_at: '' }); }
      else { showFlash(data.message, 'error'); }
    });
  };

  return (
    <>
      <h2 className="header-title">Aqlli xabar yuborish</h2>
      <div className="glass-card" style={{maxWidth:'800px'}}>
        <form onSubmit={handleBroadcast}>
           <div className="form-group">
              <label>Xabar nishoni</label>
              <select value={form.target} onChange={e => setForm({...form, target: e.target.value})} className="glass-input" style={{width:'100%', padding:'10px', background:'rgba(0,0,0,0.3)', border:'1px solid var(--card-border)', color:'#fff'}}>
                 <option value="all">Hamma (Guruhlar + Shaxsiy)</option>
                 <option value="groups">Faqat barcha guruhlar</option>
                 <option value="users">Faqat barcha shaxsiy foydalanuvchilar</option>
                 <option value="specific_group">Aniq bir guruhga</option>
              </select>
           </div>
           {form.target === 'specific_group' && (
             <div className="form-group" style={{marginTop:'1.5rem'}}>
                <label>Guruhni tanlang</label>
                <select value={form.group_id} onChange={e => setForm({...form, group_id: e.target.value})} className="glass-input" style={{width:'100%', padding:'10px', background:'rgba(0,0,0,0.3)', border:'1px solid var(--card-border)', color:'#fff'}}>
                   <option value="">Guruhni tanlang...</option>
                   {groups.map(g => <option key={g.id} value={g.id}>{g.title}</option>)}
                </select>
             </div>
           )}
           <div className="form-group" style={{marginTop:'1.5rem'}}>
              <label>Rejalashtirish (ixtiyoriy)</label>
              <input 
                 type="datetime-local" 
                 value={form.scheduled_at} 
                 onChange={e => setForm({...form, scheduled_at: e.target.value})} 
                 className="glass-input" 
                 style={{width:'100%', padding:'10px', background:'rgba(0,0,0,0.3)', border:'1px solid var(--card-border)', color:'#fff'}}
              />
              <small style={{color:'var(--text-muted)'}}>Agar vaqt tanlasangiz, xabar shu vaqtda avtomatik yuboriladi. Darhol yuborish uchun bo'sh qoldiring.</small>
           </div>
           <div className="form-group" style={{marginTop:'1.5rem'}}>
              <label>Xabar matni</label>
              <textarea rows="6" value={form.text} onChange={e => setForm({...form, text: e.target.value})} placeholder="Xabaringizni yozing..." required />
           </div>
           <button type="submit" className="btn" style={{marginTop:'2rem', width:'100%'}} disabled={loading}>
              {loading ? 'Yuborilmoqda...' : 'Xabarni yuborish'}
           </button>
        </form>
      </div>
    </>
  );
}

function App() {
  const [token, setToken] = useState(sessionStorage.getItem('admin_token'));
  const [activeTab, setActiveTab] = useState('dashboard');
  const [username, setUsername] = useState('');
  const [isAuthChecking, setIsAuthChecking] = useState(!!token);
  
  // Global UI States
  const [flash, setFlash] = useState(null);
  const [modal, setModal] = useState({ isOpen: false, title: '', text: '', onConfirm: null });

  const showFlash = (text, type = 'success') => {
    setFlash({ text, type });
    setTimeout(() => setFlash(null), 3000);
  };

  const askConfirm = (title, text, onConfirm) => {
    setModal({ isOpen: true, title, text, onConfirm });
  };

  useEffect(() => {
    if (token) {
      fetch(`${API_URL}/auth/me`, { headers: { 'Authorization': `Bearer ${token}` } })
        .then(res => {
          if (res.status === 401) { handleLogout(); return null; }
          return res.json();
        })
        .then(data => { 
           if (data) setUsername(data.username); 
           setIsAuthChecking(false);
        })
        .catch(err => { console.error('Auth check error:', err); handleLogout(); });
    } else {
        setIsAuthChecking(false);
    }
  }, [token]);

  const handleLogout = () => { sessionStorage.removeItem('admin_token'); setToken(null); setIsAuthChecking(false); };

  if (isAuthChecking) return <div className="loader"></div>;
  if (!token) return <Login onLogin={(t) => { sessionStorage.setItem('admin_token', t); setToken(t); }} />;

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="brand">
          <Icons.Bot /> <span>UyQur</span>
        </div>
        <div className="nav-links">
          <div className="nav-group">
            <div className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}><Icons.Dashboard /> <span>Asosiy</span></div>
          </div>
          
          <div className="nav-group">
            <div className={`nav-link ${(activeTab === 'messages' || activeTab === 'groups' || activeTab === 'archive' || activeTab === 'customers') ? 'active' : ''}`}><Icons.History /> <span>Muloqotlar ▾</span></div>
            <div className="nav-sub-menu">
              <div className={`nav-link ${activeTab === 'messages' ? 'active' : ''}`} onClick={() => setActiveTab('messages')}><Icons.History /> <span>Jurnal</span></div>
              <div className={`nav-link ${activeTab === 'groups' ? 'active' : ''}`} onClick={() => setActiveTab('groups')}><Icons.Groups /> <span>Guruhlar</span></div>
              <div className={`nav-link ${activeTab === 'customers' ? 'active' : ''}`} onClick={() => setActiveTab('customers')}><Icons.Profile /> <span>Mijozlar (CRM)</span></div>
              <div className={`nav-link ${activeTab === 'archive' ? 'active' : ''}`} onClick={() => setActiveTab('archive')}><Icons.Folder /> <span>Kunlik Arxiv</span></div>
            </div>
          </div>

          <div className="nav-group">
            <div className={`nav-link ${(activeTab === 'knowledge' || activeTab === 'broadcast' || activeTab === 'monitoring') ? 'active' : ''}`}><Icons.Bot /> <span>Bot Boshqaruvi ▾</span></div>
            <div className="nav-sub-menu">
              <div className={`nav-link ${activeTab === 'knowledge' ? 'active' : ''}`} onClick={() => setActiveTab('knowledge')}><Icons.Training /> <span>Botni o'qitish</span></div>
              <div className={`nav-link ${activeTab === 'broadcast' ? 'active' : ''}`} onClick={() => setActiveTab('broadcast')}><Icons.Broadcast /> <span>Xabar yuborish</span></div>
              <div className={`nav-link ${activeTab === 'monitoring' ? 'active' : ''}`} onClick={() => setActiveTab('monitoring')}><Icons.Settings /> <span>Monitoring</span></div>
            </div>
          </div>

          <div className="nav-group">
            <div className={`nav-link ${(activeTab === 'settings' || activeTab === 'database' || activeTab === 'profile') ? 'active' : ''}`}><Icons.Settings /> <span>Tizim & Sozlamalar ▾</span></div>
            <div className="nav-sub-menu">
              <div className={`nav-link ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => setActiveTab('settings')}><Icons.Settings /> <span>Sozlamalar</span></div>
              <div className={`nav-link ${activeTab === 'database' ? 'active' : ''}`} onClick={() => setActiveTab('database')}><Icons.Database /> <span>Ma'lumotlar bazasi</span></div>
              <div className={`nav-link ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}><Icons.Profile /> <span>Profil</span></div>
            </div>
          </div>

          <div className="nav-group" style={{marginTop: 'auto'}}>
            <div className="nav-link logout" onClick={handleLogout}><Icons.Logout /> <span>Chiqish</span></div>
          </div>
        </div>
      </div>
      <div className="main-content">
        {flash && <div className={`flash-banner ${flash.type}`}>{flash.text}</div>}
        <ConfirmModal {...modal} onCancel={() => setModal({ ...modal, isOpen: false })} />
        {activeTab === 'dashboard' && <Dashboard token={token} />}
        {activeTab === 'messages' && <Messages token={token} />}
        {activeTab === 'groups' && <Groups token={token} />}
        {activeTab === 'knowledge' && <KnowledgeBase token={token} showFlash={showFlash} askConfirm={askConfirm} />}
        {activeTab === 'broadcast' && <BroadcastManager token={token} showFlash={showFlash} />}
        {activeTab === 'monitoring' && <MonitoringManager token={token} showFlash={showFlash} />}
        {activeTab === 'settings' && <BotSettings token={token} showFlash={showFlash} askConfirm={askConfirm} />}
        {activeTab === 'profile' && <Profile token={token} setUsername={setUsername} showFlash={showFlash} />}
        {activeTab === 'database' && <DatabaseManager token={token} showFlash={showFlash} askConfirm={askConfirm} />}
        {activeTab === 'archive' && <ArchiveManager token={token} />}
        {activeTab === 'customers' && <CustomersManager token={token} />}
      </div>
    </div>
  );
}

function CustomersManager({ token }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/users/`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json())
      .then(d => { setUsers(d || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, [token]);

  return (
    <>
      <div className="flex-between" style={{marginBottom:'2rem'}}>
         <h2 className="header-title" style={{margin:0}}>Mijozlar ro'yxati (CRM)</h2>
         <a href={`${API_URL}/export/users`} className="btn btn-sm" style={{background:'var(--primary)'}}>
            📥 Excel yuklab olish
         </a>
      </div>
      
      {loading ? <div className="loader"></div> : (
        <div className="glass-card table-wrapper">
          <table>
            <thead>
              <tr>
                <th>No</th>
                <th>Ismi / Username</th>
                <th>Tili</th>
                <th>Jami Xabarlar</th>
                <th>Savollar miqdori</th>
                <th>Ro'yxatdan o'tgan</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u, i) => (
                <tr key={u.id}>
                  <td style={{color:'var(--text-muted)'}}>{i + 1}</td>
                  <td>
                    <div style={{fontWeight:'600'}}>{u.full_name || 'Nomalum'}</div>
                    {u.username && <div style={{fontSize:'0.75rem', color:'var(--text-muted)'}}>@{u.username}</div>}
                  </td>
                  <td style={{textTransform:'uppercase', fontSize:'0.8rem'}}>{u.language_code || 'uz'}</td>
                  <td><span className="badge badge-kb">{u.total_messages} ta</span></td>
                  <td><span className="badge badge-unanswered" style={{background: u.total_questions > 0 ? 'rgba(239, 68, 68, 0.1)' : 'rgba(255,255,255,0.05)', color: u.total_questions > 0 ? 'var(--danger)' : 'var(--text-muted)'}}>{u.total_questions} ta</span></td>
                  <td style={{fontSize:'0.8rem'}}>{new Date(u.created_at).toLocaleDateString('ru-RU')}</td>
                </tr>
              ))}
              {users.length === 0 && <tr><td colSpan="6" style={{textAlign:'center'}}>Mijozlar topilmadi.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function Dashboard({ token }) {
  const [stats, setStats] = useState({ 
    total_groups: 0, total_questions: 0, answered_questions: 0, unanswered_questions: 0, bot_answers: 0, total_messages: 0,
    latest_unanswered: [], most_active_group: null, most_active_user: null, 
    trending_topics: [], daily_activity: [], total_users: 0, top_groups: []
  });
  const [loading, setLoading] = useState(true);
  const [answeringId, setAnsweringId] = useState(null);
  const [answerText, setAnswerText] = useState('');
  const [sending, setSending] = useState(false);

  const fetchStats = () => {
    fetch(`${API_URL}/dashboard/stats`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(data => { setStats(data); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchStats();
  }, [token]);

  const handleSendAnswer = (e) => {
    e.preventDefault();
    if (!answerText.trim()) return;
    setSending(true);
    fetch(`${API_URL}/questions/${answeringId}/answer`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
       body: JSON.stringify({ text: answerText })
    })
    .then(res => res.json())
    .then(() => {
       setSending(false);
       setAnsweringId(null);
       setAnswerText('');
       fetchStats();
    })
    .catch(() => { setSending(false); });
  };

  if (loading) return <div className="loader"></div>;

  return (
    <div className="dashboard-layout">
      {/* Stat Cards */}
      <div className="grid-cards" style={{gridTemplateColumns:'repeat(4, 1fr)', gap:'1.5rem', marginBottom:'2rem'}}>
         <div className="glass-card stat-card">
            <div className="stat-label">Jami xabarlar</div>
            <div className="stat-value">{stats.total_messages || 0}</div>
         </div>
         <div className="glass-card stat-card">
            <div className="stat-label">Jami so'rovlar</div>
            <div className="stat-value">{stats.total_questions || 0}</div>
         </div>
         <div className="glass-card stat-card">
            <div className="stat-label">Bot javoblari</div>
            <div className="stat-value" style={{color:'var(--primary)'}}>{stats.bot_answers || 0}</div>
         </div>
         <div className="glass-card stat-card">
            <div className="stat-label">Guruhlar</div>
            <div className="stat-value">{stats.total_groups || 0}</div>
         </div>
      </div>

      <div className="glass-card" style={{padding:'2rem', marginBottom:'2rem'}}>
        <div className="summary-header" style={{display:'flex', justifyContent:'space-between', marginBottom:'1.5rem'}}>
           <div className="summary-title" style={{margin:0}}>Haftalik faollik (Xabarlar va Savollar)</div>
           <div style={{display:'flex', gap:'15px', fontSize:'0.75rem'}}>
              <span style={{display:'flex', alignItems:'center', gap:'5px'}}><span style={{width:'8px', height:'8px', background:'#6366f1', borderRadius:'2px'}}></span> Xabarlar</span>
              <span style={{display:'flex', alignItems:'center', gap:'5px'}}><span style={{width:'8px', height:'8px', background:'#ec4899', borderRadius:'2px'}}></span> Savollar</span>
           </div>
        </div>
        <SimpleBarChart data={stats.daily_activity} />
      </div>

      <div className="grid-cards" style={{gridTemplateColumns:'1fr 1fr', gap:'2rem'}}>
          <div className="glass-card" style={{marginBottom:0}}>
             <div className="summary-title" style={{marginBottom:'1rem'}}>Kutilayotgan savollar ({stats.unanswered_questions || 0})</div>
             <div className="unanswered-list" style={{maxHeight:'400px', overflowY:'auto'}}>
                {stats.latest_unanswered && stats.latest_unanswered.length > 0 ? stats.latest_unanswered.map(q => (
                  <div key={q.id} className="unanswered-item" style={{display: 'block', padding:'1rem', background:'rgba(255,255,255,0.02)', borderRadius:'12px', marginBottom:'10px'}}>
                    <div className="flex-between" style={{alignItems: 'flex-start', gap:'15px'}}>
                      <div style={{flex:1}}>
                        <div style={{fontSize:'0.9rem', lineHeight:1.4}}>{q.text}</div>
                        <div style={{fontSize:'0.7rem', color:'var(--text-muted)', marginTop:'5px'}}>{q.full_name} • {q.group_title}</div>
                      </div>
                      {answeringId !== q.id && <button className="btn btn-sm" onClick={() => {setAnsweringId(q.id); setAnswerText('');}}>Javob berish</button>}
                    </div>
                    
                    {answeringId === q.id && (
                      <form onSubmit={handleSendAnswer} style={{marginTop: '1rem'}}>
                        <textarea 
                          rows="3" 
                          value={answerText} 
                          onChange={e => setAnswerText(e.target.value)}
                          placeholder="Javobingizni yozing..."
                          style={{width:'100%', padding:'10px', fontSize:'0.9rem', marginBottom:'10px'}}
                          required
                        />
                        <div className="flex-between">
                           <button type="button" className="btn btn-sm btn-danger" onClick={() => setAnsweringId(null)}>Bekor qilish</button>
                           <button type="submit" className="btn btn-sm" disabled={sending}>{sending ? 'Yuborilmoqda...' : 'Yuborish'}</button>
                        </div>
                      </form>
                    )}
                  </div>
                )) : <p style={{color:'var(--text-muted)', fontSize:'0.9rem', textAlign:'center', padding:'2rem'}}>Kutilayotgan savollar topilmadi.</p>}
             </div>
          </div>

          <div className="glass-card" style={{marginBottom:0}}>
             <div className="summary-title" style={{marginBottom:'1.5rem'}}>Trenddagi mavzular (AI)</div>
             {stats.trending_topics && stats.trending_topics.map((t, i) => (
                <div key={i} className="trending-topic">
                   <div className="topic-info">
                      <span>{t.word}</span>
                      <span className="trending-count">{t.count} marta</span>
                   </div>
                   <div className="topic-bar-bg">
                      <div className="topic-bar-fill" style={{width: `${(t.count / (stats.trending_topics[0]?.count || 1)) * 100}%`, background:'linear-gradient(90deg, #ec4899, #f43f5e)'}}></div>
                   </div>
                </div>
             ))}
          </div>
      </div>

      <div className="glass-card" style={{marginTop:'2rem'}}>
         <div className="summary-title" style={{marginBottom:'1.5rem'}}>Eng faol guruhlar</div>
         <div className="grid-cards" style={{gridTemplateColumns:'repeat(auto-fit, minmax(200px, 1fr))', gap:'1rem', marginBottom:0}}>
             {stats.top_groups && stats.top_groups.map((g, i) => (
                <div key={i} className="glass-card" style={{margin:0, padding:'1rem', background:'rgba(255,255,255,0.03)'}}>
                   <div style={{fontSize:'0.9rem', fontWeight:600}}>{g.title}</div>
                   <div style={{fontSize:'1.5rem', marginTop:'0.5rem'}}>{g.messages} <small style={{fontSize:'0.7rem', color:'var(--text-muted)'}}>xabar</small></div>
                </div>
             ))}
         </div>
      </div>
    </div>
  );
}

function KnowledgeBase({ token, showFlash, askConfirm }) {
  const [kb, setKb] = useState([]);
  const [form, setForm] = useState({ question: '', answer: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // PDF Extraction States
  const [extracting, setExtracting] = useState(false);
  const [extractedData, setExtractedData] = useState(null);

  const fetchKb = () => {
    setLoading(true);
    fetch(`${API_URL}/knowledge/`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(data => { setKb(data); setLoading(false); })
      .catch(() => setLoading(false));
  };
  useEffect(() => fetchKb(), [token]);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setExtracting(true);
    fetch(`${API_URL}/knowledge/extract`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    })
    .then(async res => {
       const data = await res.json();
       if (!res.ok) throw new Error(data.detail || 'Tahlil xatosi');
       return data;
    })
    .then(data => { setExtracting(false); setExtractedData(data); showFlash('Tahlil yakunlandi'); })
    .catch(err => { setExtracting(false); showFlash(err.message, 'error'); });
  };

  const handleEditExtracted = (i, field, val) => {
    const newData = [...extractedData];
    newData[i][field] = val;
    setExtractedData(newData);
  };

  const handleRemoveExtracted = (i) => {
    setExtractedData(extractedData.filter((_, idx) => idx !== i));
  };

  const handleBulkSave = () => {
    setSaving(true);
    fetch(`${API_URL}/knowledge/bulk`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
       body: JSON.stringify({ items: extractedData })
    })
    .then(() => { setSaving(true); setExtractedData(null); showFlash('Bilimlar saqlandi'); fetchKb(); })
    .catch(() => { setSaving(false); showFlash('Saqlashda xato', 'error'); });
  };

  const deleteKb = (id) => {
    askConfirm('Ma\'lumotni o\'chirish', 'Haqiqatan ham o\'chirmoqchimisiz?', () => {
      fetch(`${API_URL}/knowledge/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } })
        .then(() => { showFlash('Bilim o\'chirildi', 'error'); fetchKb(); });
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setSaving(true);
    fetch(`${API_URL}/knowledge/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(form)
    }).then(() => { 
      setForm({ question: '', answer: '' }); 
      setSaving(false); 
      showFlash('Ma\'lumot saqlandi');
      fetchKb(); 
    }).catch(() => { setSaving(false); showFlash('Xato', 'error'); });
  };

  return (
    <>
      <h2 className="header-title">AI Bilimlar bazasi</h2>
      <div className="grid-cards" style={{gridTemplateColumns:'1fr 1fr', gap:'2rem', alignItems:'start'}}>
         <div className="glass-card">
            <div className="summary-title" style={{marginBottom:'1rem'}}>Qo'lda bilim qo'shish</div>
            <form onSubmit={handleSubmit}>
               <div className="form-group"><label>Savol yoki kalit so'z</label><input type="text" value={form.question} onChange={e => setForm({...form, question: e.target.value})} required /></div>
               <div className="form-group"><label>Javob matni</label><textarea value={form.answer} onChange={e => setForm({...form, answer: e.target.value})} required /></div>
               <button type="submit" className="btn" disabled={saving}>{saving ? 'Saqlanmoqda...' : 'Saqlash'}</button>
            </form>
         </div>

         <div className="glass-card">
            <div className="summary-title" style={{marginBottom:'1rem'}}>Fayldan bilim ajratish (PDF/DOCX/TXT)</div>
            <p style={{fontSize:'0.85rem', color:'var(--text-muted)', marginBottom:'1.5rem'}}>
               Faylni yuklang va AI undagi eng muhim savollarni sizga ajratib beradi.
            </p>
            <input 
              type="file" 
              accept=".pdf,.docx,.txt" 
              onChange={handleFileUpload} 
              style={{display:'none'}} 
              id="pdf-upload" 
              disabled={extracting}
            />
            <label htmlFor="pdf-upload" className="btn" style={{display:'block', textAlign:'center', cursor:'pointer', background: 'rgba(255,255,255,0.05)', border:'2px dashed var(--card-border)'}}>
               {extracting ? 'AI Tahlil qilmoqda...' : 'Faylni tanlash'}
            </label>
         </div>
      </div>

      {extractedData && (
        <div className="glass-card" style={{marginTop:'2rem', border:'1px solid var(--primary)', animation:'fadeIn 0.5s ease'}}>
           <div className="flex-between" style={{marginBottom:'1.5rem'}}>
              <div>
                 <div className="summary-title" style={{margin:0}}>Siz uchun ajratib olingan bilimlar ({extractedData.length})</div>
                 <p style={{fontSize:'0.75rem', color:'var(--text-muted)', marginTop:'5px'}}>AI faylni o'qib chiqdi. Kerakli joylarini tahrirlab, so'ng saqlang.</p>
              </div>
              <div className="flex-between" style={{gap:'10px'}}>
                 <button className="btn btn-sm btn-danger" onClick={() => setExtractedData(null)}>Bekor qilish</button>
                 <button className="btn btn-sm" onClick={handleBulkSave} disabled={saving || extractedData.length === 0}>
                    {saving ? 'Saqlanmoqda...' : 'Tasdiqlash va Saqlash'}
                 </button>
              </div>
           </div>
           
           {extractedData.length === 0 ? (
             <div style={{textAlign:'center', padding:'3rem', background:'rgba(255,255,255,0.02)', borderRadius:'12px'}}>
                <p style={{color:'var(--text-muted)'}}>AI ushbu fayldan hech qanday ma'lumot ajratib ololmadi. Boshqa fayl yoki boshqa AI provider (masalan, Gemini) sinab ko'ring.</p>
             </div>
           ) : (
             <div className="table-wrapper">
                <table className="editable-table">
                   <thead><tr><th style={{width:'40%'}}>Savol / Mavzu</th><th>AI tayyorlagan javob</th><th style={{width:'50px'}}></th></tr></thead>
                   <tbody>
                      {extractedData.map((d, i) => (
                         <tr key={i}>
                            <td style={{padding:'8px'}}>
                               <textarea 
                                  className="glass-input-table"
                                  style={{minHeight:'100px', fontWeight:'600'}}
                                  value={d.question} 
                                  onChange={(e) => handleEditExtracted(i, 'question', e.target.value)}
                                  placeholder="Savolni tahrirlang..."
                               />
                            </td>
                            <td style={{padding:'8px'}}>
                               <textarea 
                                  className="glass-input-table"
                                  style={{minHeight:'100px'}}
                                  value={d.answer} 
                                  onChange={(e) => handleEditExtracted(i, 'answer', e.target.value)}
                                  placeholder="Javobni tahrirlang..."
                               />
                            </td>
                            <td style={{textAlign:'center', verticalAlign:'middle'}}>
                               <button 
                                 className="btn btn-sm btn-danger" 
                                 title="O'chirish"
                                 style={{padding:'10px', borderRadius:'10px'}} 
                                 onClick={() => handleRemoveExtracted(i)}
                               >
                                 <Icons.Logout style={{transform:'rotate(90deg)', width:'16px', height:'16px'}} />
                               </button>
                            </td>
                         </tr>
                      ))}
                   </tbody>
                </table>
             </div>
           )}
        </div>
      )}

      <div className="glass-card table-wrapper" style={{marginTop:'2rem'}}>
        <div className="summary-title" style={{marginBottom:'1.5rem'}}>Mavjud bilimlar jurnali</div>
        <table><thead><tr><th>Savol</th><th>Bilim matni</th><th>Amallar</th></tr></thead>
        <tbody>{kb.map(item => (<tr key={item.id}><td>{item.question}</td><td style={{fontSize:'0.85rem', color:'var(--text-muted)', maxWidth:'400px'}}>{item.answer}</td><td><button className="btn btn-sm btn-danger" onClick={() => deleteKb(item.id)}>O'chirish</button></td></tr>))}</tbody></table>
        {kb.length === 0 && !loading && <p style={{textAlign:'center', padding:'2rem', color:'var(--text-muted)'}}>Hali ma'lumotlar qo'shilmagan.</p>}
      </div>
    </>
  );
}

function Messages({ token }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/questions/?limit=15&offset=${page * 15}`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(data => { setMessages(data.items || []); setTotal(data.total || 0); setLoading(false); })
      .catch(() => setLoading(false));
  }, [token, page]);

  if (loading) return <div className="loader"></div>;

  return (
    <>
      <div className="flex-between" style={{marginBottom:'2rem'}}>
         <h2 className="header-title" style={{margin:0}}>Muloqotlar jurnali</h2>
         <a href={`${API_URL}/export/messages`} className="btn btn-sm" style={{background:'var(--primary)'}}>
            📥 Excel yuklab olish
         </a>
      </div>
      <div className="glass-card table-wrapper">
        <table><thead><tr><th>Foydalanuvchi</th><th>Xabar matni</th><th>Guruh</th><th>Holati</th></tr></thead>
        <tbody>{messages.map(msg => (<tr key={msg.id}><td>{msg.full_name}</td><td style={{maxWidth:'300px', fontSize:'0.85rem'}}>{msg.telegram_app_link ? <a href={msg.telegram_app_link} style={{color: 'inherit', textDecoration: 'none', borderBottom: '1px dashed currentColor'}} title="Telegram ilovasida ochish">{msg.text}</a> : msg.text}</td><td>{msg.group_title}</td><td><span className={`badge ${msg.is_answered ? 'badge-kb' : 'badge-unanswered'}`}>{msg.is_answered ? 'Javob berilgan' : 'Kutilmoqda'}</span></td></tr>))}</tbody></table>
        <div className="flex-between" style={{marginTop:'1.5rem'}}><button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(p => p - 1)}>Orqaga</button><strong>{page + 1} / {Math.ceil(total / 15) || 1}</strong><button className="btn btn-sm" disabled={(page + 1) * 15 >= total} onClick={() => setPage(p => p + 1)}>Oldinga</button></div>
      </div>
    </>
  );
}

function Groups({ token }) {
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchGroups = () => {
    setLoading(true);
    fetch(`${API_URL}/groups/`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(data => { setGroups(data); setLoading(false); })
      .catch(() => setLoading(false));
  };
  useEffect(() => { if(!selectedGroup) fetchGroups(); }, [token, selectedGroup]);

  if (loading) return <div className="loader"></div>;
  if (selectedGroup) return <GroupHistory token={token} group={selectedGroup} onBack={() => setSelectedGroup(null)} />;

  return (
    <>
      <h2 className="header-title">Guruhlar ro'yxati</h2>
      <div className="glass-card table-wrapper">
        <table><thead><tr><th>Guruh nomi</th><th>Jami xabarlar</th><th>So'rovlar</th><th>Aniqlik %</th><th>Kutilmoqda</th></tr></thead>
        <tbody>{groups.map(g => (<tr key={g.id} className="clickable-row" onClick={() => setSelectedGroup(g)}><td>{g.title}</td><td>{g.total_messages}</td><td>{g.total_questions}</td><td>{Math.round((g.answered_questions / (g.total_questions || 1)) * 100)}%</td><td><span className="badge badge-unanswered">{g.unanswered_questions}</span></td></tr>))}</tbody></table>
      </div>
    </>
  );
}

function GroupHistory({ token, group, onBack }) {
  const [msgs, setMsgs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [answeringId, setAnsweringId] = useState(null);
  const [answerText, setAnswerText] = useState('');
  const [sending, setSending] = useState(false);

  const fetchMessages = () => {
    setLoading(true);
    fetch(`${API_URL}/groups/${group.id}/messages?limit=50`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json())
      .then(d => { setMsgs(d.items || []); setLoading(false); })
      .catch(() => { setLoading(false); }); 
  };

  useEffect(() => { 
    fetchMessages();
  }, [group, token]);

  const handleSendAnswer = (e, qId) => {
    e.preventDefault();
    if (!answerText.trim()) return;
    setSending(true);
    fetch(`${API_URL}/questions/${qId}/answer`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
       body: JSON.stringify({ text: answerText })
    })
    .then(res => res.json())
    .then(() => {
       setSending(false);
       setAnsweringId(null);
       setAnswerText('');
       fetchMessages();
    })
    .catch(() => { setSending(false); });
  };

  return (<>
    <div className="flex-between" style={{marginBottom:'2rem'}}>
       <h2 className="header-title" style={{margin:0}}>{group.title} tarixi</h2>
       <button className="btn btn-sm" onClick={onBack}>⬅️ Orqaga qaytish</button>
    </div>
    
    {loading && msgs.length === 0 ? <div className="loader"></div> : (
      <div className="glass-card table-wrapper">
        <table>
          <thead>
             <tr>
                <th style={{width:'80px'}}>Vaqti</th>
                <th style={{width:'150px'}}>Kimdan</th>
                <th style={{width:'30%'}}>Xabar (Savol)</th>
                <th>Javob</th>
                <th style={{width:'120px'}}>Holati</th>
             </tr>
          </thead>
          <tbody>
            {msgs.length > 0 ? msgs.map(m => (
              <tr key={m.id}>
                <td style={{fontSize:'0.8rem', whiteSpace:'nowrap'}}>{new Date(m.created_at).toLocaleString('ru-RU', {hour:'2-digit', minute:'2-digit', day:'2-digit', month:'2-digit'})}</td>
                <td>
                   <div style={{fontWeight:'600', fontSize:'0.9rem'}}>{m.full_name}</div>
                   {m.username && <div style={{fontSize:'0.7rem', color:'var(--text-muted)'}}>@{m.username}</div>}
                </td>
                <td style={{fontSize:'0.9rem'}}>
                   {m.telegram_app_link ? <a href={m.telegram_app_link} style={{color: 'inherit', textDecoration: 'none', borderBottom: '1px dashed currentColor'}} title="Telegram ilovasida ochish">{m.text}</a> : m.text}
                </td>
                <td style={{fontSize:'0.9rem'}}>
                   {m.is_question ? (
                     m.answer_text ? (
                        <div>
                           <div style={{color:'var(--primary)', fontWeight:'600', fontSize:'0.7rem', textTransform:'uppercase', marginBottom:'4px'}}>
                              {m.answered_by || 'Bot'} javobi:
                           </div>
                           {m.answer_text}
                        </div>
                     ) : (
                        answeringId === m.id ? (
                           <form onSubmit={(e) => handleSendAnswer(e, m.id)} style={{marginTop: '5px'}}>
                             <textarea 
                               rows="3" 
                               value={answerText} 
                               onChange={e => setAnswerText(e.target.value)}
                               placeholder="Javobingizni yozing..."
                               style={{width:'100%', padding:'10px', fontSize:'0.9rem', marginBottom:'10px', borderRadius:'8px', border:'1px solid var(--card-border)', background:'rgba(0,0,0,0.2)', color:'#fff'}}
                               required
                             />
                             <div className="flex-between">
                                <button type="button" className="btn btn-sm btn-danger" onClick={() => {setAnsweringId(null); setAnswerText('');}}>Bekor qilish</button>
                                <button type="submit" className="btn btn-sm" disabled={sending}>{sending ? 'Yuborilmoqda...' : 'Yuborish'}</button>
                             </div>
                           </form>
                        ) : (
                           <div>
                              <span style={{color:'var(--text-muted)', fontStyle:'italic', display:'block', marginBottom:'8px'}}>Kutilmoqda...</span>
                              <button className="btn btn-sm" onClick={() => {setAnsweringId(m.id); setAnswerText('');}}>Javob berish</button>
                           </div>
                        )
                     )
                   ) : <span style={{color:'var(--text-muted)', fontSize:'0.8rem'}}>Oddiy xabar</span>}
                </td>
                <td>
                   {m.is_question ? (
                     <span className={`badge ${m.is_answered ? 'badge-kb' : 'badge-unanswered'}`} style={{fontSize:'0.7rem'}}>
                        {m.is_answered ? 'Javob berilgan' : 'Kutilmoqda'}
                     </span>
                   ) : <span style={{color:'var(--text-muted)', fontSize:'0.8rem'}}>-</span>}
                </td>
              </tr>
            )) : <tr><td colSpan="5" style={{textAlign:'center', padding:'3rem', color:'var(--text-muted)'}}>Tarixda ma'lumotlar topilmadi.</td></tr>}
          </tbody>
        </table>
      </div>
    )}
  </>);
}

function BotSettings({ token, showFlash, askConfirm }) {
  const [s, setS] = useState({ 
    system_prompt: '', company_info: '', maintenance_mode: 'false', maintenance_text: '',
    ai_provider: 'openai', openai_api_key: '', groq_api_key: '', gemini_api_key: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/settings/`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(d => { 
        setS({ 
          system_prompt: d.system_prompt || '', 
          company_info: d.company_info || '',
          maintenance_mode: d.maintenance_mode || 'false',
          maintenance_text: d.maintenance_text || 'Hozirda tizimda texnik ishlar olib borilmoqda. Tez orada qaytamiz!',
          ai_provider: d.ai_provider || 'openai',
          openai_api_key: d.openai_api_key || '',
          groq_api_key: d.groq_api_key || '',
          gemini_api_key: d.gemini_api_key || ''
        }); 
        setLoading(false); 
      })
      .catch(() => setLoading(false));
  }, [token]);

  const save = (k, v) => {
    setSaving(k);
    fetch(`${API_URL}/settings/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ key: k, value: v })
    }).then(() => { setSaving(null); showFlash('Mualliflik saqlandi!'); }).catch(() => { setSaving(null); showFlash('Xatolik!', 'error'); });
  };

  const handleClearDB = () => {
    askConfirm(
      'DIQQAT! Barcha ma\'lumotlarni o\'chirish',
      'Haqiqatan ham barcha ma\'lumotlarni (guruhlar, xabarlar, AI bilimlari va sozlamalar) butunlay o\'chirib tashlamoqchimisiz? Bu amalni ortga qaytarib bo\'lmaydi!',
      () => {
        setLoading(true);
        fetch(`${API_URL}/settings/clear-all`, { 
          method: 'DELETE', 
          headers: { 'Authorization': `Bearer ${token}` } 
        })
        .then(res => res.json())
        .then(data => {
            setLoading(false);
            if (data.status === 'success') {
                showFlash("Barcha ma'lumotlar o'chirildi. Tizim toza holatga qaytdi.");
                setTimeout(() => window.location.reload(), 2000);
            } else {
                showFlash("Xatolik yuz berdi", "error");
            }
        })
        .catch(() => {
            setLoading(false);
            showFlash("Xatolik", "error");
        });
      }
    );
  };

  if (loading) return <div className="loader"></div>;

  const isMaint = s.maintenance_mode === 'true';

  return (<>
    <div className="flex-between" style={{marginBottom:'2.5rem', alignItems:'center'}}>
       <div>
         <h2 className="header-title" style={{margin:0}}>Tizim boshqaruvi</h2>
         <p style={{color:'var(--text-muted)', fontSize:'0.9rem', marginTop:'0.5rem'}}>Bot parametrlari va AI provayderlarini sozlashingiz mumkin.</p>
       </div>
       <div className={`badge ${isMaint ? 'badge-unanswered' : 'badge-kb'}`} style={{padding:'10px 20px', borderRadius:'30px', display:'flex', alignItems:'center', gap:'8px', fontSize:'0.85rem', fontWeight:'600', boxShadow: isMaint ? '0 0 15px rgba(239, 68, 68, 0.2)' : '0 0 15px rgba(16, 185, 129, 0.2)'}}>
          <span style={{width:8, height:8, borderRadius:'50%', background: isMaint ? 'var(--danger)' : 'var(--success)', display:'inline-block'}}></span>
          {isMaint ? 'TEXNIK ISHLAR REJIMIDA' : 'BOT TO\'LIQ FAOL'}
       </div>
    </div>

    <div className="grid-cards" style={{gridTemplateColumns:'repeat(2, 1fr)', gap:'2rem'}}>
       {/* AI Provider Section */}
       <div className="glass-card" style={{margin:0}}>
          <div style={{display:'flex', alignItems:'center', gap:'12px', marginBottom:'1.5rem'}}>
             <div className="stat-icon-wrapper" style={{margin:0, color:'var(--primary)', background:'rgba(99, 102, 241, 0.1)'}}><Icons.Training /></div>
             <div className="summary-title" style={{margin:0}}>AI Provayder Sozlamalari</div>
          </div>
          
          <div className="form-group">
            <label>Joriy AI Provayder</label>
            <select 
              value={s.ai_provider} 
              onChange={e => { setS({...s, ai_provider: e.target.value}); save('ai_provider', e.target.value); }}
              style={{width:'100%', padding:'0.875rem', borderRadius:'0.75rem', background:'rgba(0,0,0,0.3)', color:'#fff', border:'1px solid var(--card-border)'}}
            >
              <option value="openai">OpenAI (GPT-4o-mini)</option>
              <option value="groq">Groq (Llama 3.3 - Bepul & Tez!)</option>
              <option value="gemini">Google Gemini (Pro/Flash)</option>
            </select>
          </div>

          <div className="form-group" style={{marginTop:'1.5rem'}}>
            <label>{s.ai_provider.toUpperCase()} API Key</label>
            <input 
              type="password" 
              value={s[`${s.ai_provider}_api_key`]} 
              onChange={e => setS({...s, [`${s.ai_provider}_api_key`]: e.target.value})}
              placeholder="API kalitini kiriting..." 
            />
            <button className="btn btn-sm" style={{marginTop:'10px', width:'100%'}} onClick={() => save(`${s.ai_provider}_api_key`, s[`${s.ai_provider}_api_key`])}>
              Kalitni saqlash
            </button>
          </div>
       </div>

       {/* Maintenance Mode Section */}
       <div className="glass-card" style={{margin:0, display:'flex', flexDirection:'column'}}>
          <div className="flex-between" style={{marginBottom:'1.5rem'}}>
             <div style={{display:'flex', alignItems:'center', gap:'12px'}}>
                <div className="stat-icon-wrapper" style={{margin:0, color:'var(--danger)', background:'rgba(239, 68, 68, 0.1)'}}><Icons.Settings /></div>
                <div className="summary-title" style={{margin:0}}>Xizmat blokirovkasi</div>
             </div>
             <label className="switch">
                <input 
                  type="checkbox" 
                  checked={isMaint} 
                  onChange={e => {
                    const newVal = e.target.checked ? 'true' : 'false';
                    setS({...s, maintenance_mode: newVal});
                    save('maintenance_mode', newVal);
                  }} 
                />
                <span className="slider round"></span>
             </label>
          </div>
          <div className="form-group" style={{marginTop:'auto'}}>
             <label style={{fontSize:'0.75rem', textTransform:'uppercase', letterSpacing:'0.05em'}}>Foydalanuvchilar uchun xabar</label>
             <textarea 
               rows="3" 
               style={{fontSize:'0.9rem', background:'rgba(0,0,0,0.2)'}}
               value={s.maintenance_text} 
               onChange={e => setS({...s, maintenance_text: e.target.value})} 
               placeholder="Botda profilaktika ishlari olib borilmoqda..." 
             />
             <button className="btn btn-sm" style={{marginTop:'15px', width:'100%'}} onClick={() => save('maintenance_text', s.maintenance_text)} disabled={saving === 'maintenance_text'}>
                {saving === 'maintenance_text' ? 'Saqlanmoqda...' : 'Xabarni yangilash'}
             </button>
          </div>
       </div>

       {/* Bot Identity Section */}
       <div className="glass-card" style={{margin:0}}>
          <div style={{display:'flex', alignItems:'center', gap:'12px', marginBottom:'1.5rem'}}>
             <div className="stat-icon-wrapper" style={{margin:0, color:'var(--primary)', background:'rgba(99, 102, 241, 0.1)'}}><Icons.Training /></div>
             <div className="summary-title" style={{margin:0}}>AI Shaxsi va Rol</div>
          </div>
          <div className="form-group">
            <label style={{fontSize:'0.75rem', textTransform:'uppercase', letterSpacing:'0.05em'}}>Botning tizim ko'rsatmasi</label>
            <textarea 
              rows="6" 
              style={{fontSize:'0.9rem', background:'rgba(0,0,0,0.2)'}}
              value={s.system_prompt} 
              onChange={e => setS({...s, system_prompt: e.target.value})} 
              placeholder="Masalan: Sen aqlli va xushmuomala yordamshisan..." 
            />
            <button className="btn btn-sm" style={{marginTop:'15px', width:'100%'}} onClick={() => save('system_prompt', s.system_prompt)} disabled={saving === 'system_prompt'}>
              {saving === 'system_prompt' ? 'Saqlanmoqda...' : 'Rolni saqlash'}
            </button>
          </div>
       </div>

       {/* Company Info Section */}
       <div className="glass-card" style={{margin:0}}>
          <div style={{display:'flex', alignItems:'center', gap:'12px', marginBottom:'1.5rem'}}>
             <div className="stat-icon-wrapper" style={{margin:0, color:'var(--secondary)', background:'rgba(236, 72, 153, 0.1)'}}><Icons.History /></div>
             <div className="summary-title" style={{margin:0}}>Kompaniya ma'lumotlari</div>
          </div>
          <div className="form-group">
            <label style={{fontSize:'0.75rem', textTransform:'uppercase', letterSpacing:'0.05em'}}>Kompaniya haqida umumiy ma'lumot</label>
            <textarea 
              rows="6" 
              style={{fontSize:'0.9rem', background:'rgba(0,0,0,0.2)'}}
              value={s.company_info} 
              onChange={e => setS({...s, company_info: e.target.value})} 
              placeholder="Kompaniya qachon tashkil topgan, xizmatlari qanday?.." 
            />
            <button className="btn btn-sm" style={{marginTop:'15px', width:'100%'}} onClick={() => save('company_info', s.company_info)} disabled={saving === 'company_info'}>
              {saving === 'company_info' ? 'Saqlanmoqda...' : "Ma'lumotni saqlash"}
            </button>
          </div>
       </div>

    </div>
    </>
  );
}

function Broadcast({ token, showFlash }) {
  const [text, setText] = useState('');
  const [target, setTarget] = useState('all');
  const [selectedGroupId, setSelectedGroupId] = useState('');
  const [groups, setGroups] = useState([]);
  const [counts, setCounts] = useState({ total_groups: 0, total_users: 0 });
  const [sending, setSending] = useState(false);
  const [loadingCounts, setLoadingCounts] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/groups/`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(data => setGroups(data))
      .catch(() => {});
    
    setLoadingCounts(true);
    fetch(`${API_URL}/admin/broadcast/count`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json())
      .then(data => { setCounts(data); setLoadingCounts(false); })
      .catch(() => setLoadingCounts(false));
  }, [token]);

  const handleSend = () => {
    if (!text.trim()) {
      showFlash("Iltimos, xabar matnini kiriting!", "error");
      return;
    }
    if (target === 'specific_group' && !selectedGroupId) {
       showFlash("Iltimos, guruhni tanlang!", "error");
       return;
    }
    
    setSending(true);
    const bodyArgs = { text, target };
    if (target === 'specific_group') {
        bodyArgs.group_id = parseInt(selectedGroupId);
    }

    fetch(`${API_URL}/admin/broadcast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(bodyArgs)
    })
    .then(res => res.json())
    .then(data => {
      setSending(false);
      if (data.status === 'success') {
        showFlash(data.message);
        setText('');
      } else {
        showFlash(data.message || 'Xatolik!', 'error');
      }
    })
    .catch(() => { setSending(false); showFlash('Server xatosi!', 'error'); });
  };

  const getTargetCount = () => {
    if (target === 'all') return (counts.total_groups || 0) + (counts.total_users || 0);
    if (target === 'groups') return counts.total_groups || 0;
    if (target === 'users') return counts.total_users || 0;
    if (target === 'specific_group') return 1;
    return 0;
  };

  return (
    <div style={{animation: 'fadeIn 0.5s ease-out'}}>
      <h2 className="header-title">Xabar tarqatish (Broadcast)</h2>
      
      <div className="grid-cards" style={{gridTemplateColumns: 'minmax(400px, 1.5fr) 1fr', gap: '2rem'}}>
        <div className="glass-card" style={{padding: '2rem'}}>
          <div className="form-group" style={{marginBottom: '1.5rem'}}>
            <label style={{display:'block', marginBottom:'0.5rem', fontWeight:'600'}}>Kimga yuborilsin?</label>
            <select className="input" value={target} onChange={(e) => setTarget(e.target.value)} style={{width:'100%'}}>
              <option value="all">Barchaga (Guruhlar + Foydalanuvchilar)</option>
              <option value="groups">Faqat barcha guruhlarga</option>
              <option value="users">Faqat barcha shaxsiy foydalanuvchilar</option>
              <option value="specific_group">Ma'lum bir guruhga...</option>
            </select>
          </div>

          {target === 'specific_group' && (
            <div className="form-group" style={{marginBottom: '1.5rem', animation: 'slideDown 0.3s ease-out'}}>
              <label style={{display:'block', marginBottom:'0.5rem', fontWeight:'600'}}>Guruhni tanlang:</label>
              <select className="input" value={selectedGroupId} onChange={(e) => setSelectedGroupId(e.target.value)} style={{width:'100%'}}>
                <option value="">-- Tanlang --</option>
                {groups.map(g => <option key={g.id} value={g.id}>{g.title}</option>)}
              </select>
            </div>
          )}

          <div className="form-group" style={{marginBottom: '1.5rem'}}>
            <label style={{display:'block', marginBottom:'0.5rem', fontWeight:'600'}}>Xabar matni:</label>
            <textarea 
              className="input" 
              value={text} 
              onChange={(e) => setText(e.target.value)} 
              placeholder="Xabaringizni bu yerga yozing..."
              style={{width:'100%', minHeight:'200px', resize:'vertical', padding:'1rem'}}
            ></textarea>
          </div>

          <div className="flex-between" style={{background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '12px', marginBottom: '1.5rem'}}>
            <div style={{fontSize: '0.9rem'}}>
              {loadingCounts ? 'Hisoblanmoqda...' : (
                <>Taxminiy nishonlar: <strong style={{color:'var(--primary)'}}>{getTargetCount()} ta</strong></>
              )}
            </div>
            <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>
              {target === 'all' && `(${counts.total_groups} guruh, ${counts.total_users} user)`}
            </div>
          </div>

          <button 
            className="btn btn-primary" 
            onClick={handleSend} 
            disabled={sending || !text.trim()} 
            style={{width:'100%', height:'55px', fontSize:'1.1rem', fontWeight:'bold'}}
          >
            {sending ? '📤 Yuborilmoqda...' : '🚀 Xabarni yuborish'}
          </button>
        </div>

        <div className="glass-card" style={{padding: '2rem', display:'flex', flexDirection:'column', height:'fit-content'}}>
           <label style={{display:'block', marginBottom:'1.5rem', fontWeight:'600', textAlign:'center'}}>Telegram'da ko'rinishi (Preview):</label>
           <div style={{
              background: 'rgba(0,0,0,0.2)',
              borderRadius: '20px',
              padding: '40px 20px 20px 20px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'flex-end',
              border: '2px solid rgba(255,255,255,0.1)',
              minHeight: '200px',
              position: 'relative'
           }}>
              <div style={{position:'absolute', top:'10px', left:'50%', transform:'translateX(-50%)', width:'40px', height:'4px', background:'rgba(255,255,255,0.1)', borderRadius:'2px'}}></div>
              <div style={{
                 alignSelf: 'flex-start',
                 background: 'rgba(52, 60, 75, 0.95)',
                 padding: '12px 16px',
                 borderRadius: '15px 15px 15px 4px',
                 maxWidth: '90%',
                 fontSize: '0.95rem',
                 boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
                 lineHeight: '1.4',
                 whiteSpace: 'pre-wrap',
                 color: '#fff'
              }}>
                {text || <span style={{color:'rgba(255,255,255,0.4)', fontStyle:'italic'}}>Matn kutilmoqda...</span>}
                <div style={{textAlign:'right', fontSize: '0.7rem', color:'rgba(255,255,255,0.5)', marginTop:'5px'}}>17:25</div>
              </div>
           </div>
           <ul style={{fontSize:'0.8rem', color:'var(--text-muted)', marginTop:'2rem', paddingLeft:'1.2rem', lineHeight:'1.6'}}>
             <li>Xabarlar fon rejimida navbat bilan yuboriladi.</li>
             <li>Lekin terminalda jarayonni kuzatishingiz mumkin.</li>
           </ul>
        </div>
      </div>
    </div>
  );
}


function DatabaseManager({ token, showFlash, askConfirm }) {
  const [groups, setGroups] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [msgPage, setMsgPage] = useState(0);
  const [totalMsgs, setTotalMsgs] = useState(0);

  const fetchGroups = () => {
    fetch(`${API_URL}/groups/`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(data => setGroups(data))
      .catch(() => {});
  };

  const fetchMessages = () => {
    fetch(`${API_URL}/messages/?limit=10&offset=${msgPage * 10}`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(data => {
        setMessages(data.items || []);
        setTotalMsgs(data.total || 0);
      })
      .catch(() => {});
  };

  useEffect(() => {
    fetchGroups();
    fetchMessages();
  }, [token, msgPage]);

  const deleteMessage = (id) => {
    askConfirm(
      "Xabarni o'chirish",
      "Haqiqatan ham ushbu xabarni bazadan o'chirmoqchimisiz?",
      () => {
        fetch(`${API_URL}/messages/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } })
          .then(res => res.json())
          .then(data => {
            if (data.status === 'success') {
              showFlash("Xabar o'chirildi");
              fetchMessages();
            }
          });
      }
    );
  };

  const deleteGroup = (id, title) => {
    askConfirm(
      "Guruhni o'chirish",
      `"${title}" guruhini va unga tegishli barcha xabarlarni o'chirib tashlamoqchimisiz?`,
      () => {
        fetch(`${API_URL}/groups/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } })
          .then(res => res.json())
          .then(data => {
            if (data.status === 'success') {
              showFlash("Guruh va xabarlar o'chirildi");
              fetchGroups();
              fetchMessages();
            }
          });
      }
    );
  };

  const handleClearHistory = () => {
    askConfirm(
      'Muloqotlarni tozalash',
      'Faqat xabarlar va guruhlar tarixini o\'chirmoqchimisiz? AI bilimlari va bot sozlamalari saqlanib qoladi.',
      () => {
        setLoading(true);
        fetch(`${API_URL}/settings/clear-history`, { 
          method: 'DELETE', 
          headers: { 'Authorization': `Bearer ${token}` } 
        })
        .then(res => res.json())
        .then(data => {
            setLoading(false);
            if (data.status === 'success') {
                showFlash(data.message);
                fetchGroups();
                fetchMessages();
            }
        });
      }
    );
  };

  const handleResetAll = () => {
    askConfirm(
      'DIQQAT! Butun tizimni reset qilish',
      'Haqiqatan ham barcha ma\'lumotlarni (AI bilimlari va API kalitlarni ham) butunlay o\'chirib tashlamoqchimisiz? Bu amalni ortga qaytarib bo\'lmaydi!',
      () => {
        setLoading(true);
        fetch(`${API_URL}/settings/clear-all`, { 
          method: 'DELETE', 
          headers: { 'Authorization': `Bearer ${token}` } 
        })
        .then(res => res.json())
        .then(data => {
            setLoading(false);
            if (data.status === 'success') {
                showFlash("Tizim to'liq tozalandi.");
                setTimeout(() => window.location.reload(), 2000);
            }
        });
      }
    );
  };

  return (
    <div style={{animation: 'fadeIn 0.5s ease-out'}}>
      <h2 className="header-title">Baza nazorati (Database Management)</h2>

      <div className="glass-card" style={{border: '1px solid rgba(255, 255, 255, 0.1)', marginBottom: '2rem'}}>
        <div style={{display:'flex', alignItems:'center', gap:'12px', marginBottom:'1.5rem'}}>
          <div className="stat-icon-wrapper" style={{margin:0, color:'var(--primary)', background:'rgba(99, 102, 241, 0.1)'}}><Icons.Database /></div>
          <div className="summary-title" style={{margin:0}}>Umumiy boshqaruv</div>
        </div>
        
        <div className="grid-cards" style={{gridTemplateColumns:'1fr 1fr', gap:'1.5rem', marginBottom:0}}>
           <div style={{padding:'1rem', borderRadius:'12px', background:'rgba(255,255,255,0.03)', border:'1px solid var(--card-border)'}}>
              <h4 style={{margin:'0 0 0.5rem 0'}}>Muloqotlar tarixi</h4>
              <p style={{fontSize:'0.8rem', color:'var(--text-muted)', marginBottom:'1.5rem'}}>Barcha xabarlar va guruhlarni tozalash. AI bilimlari o'chmaydi.</p>
              <button className="btn btn-sm" onClick={handleClearHistory} disabled={loading} style={{width:'100%'}}>
                 Tarixni tozalash
              </button>
           </div>

           <div style={{padding:'1rem', borderRadius:'12px', background:'rgba(239, 68, 68, 0.05)', border:'1px solid rgba(239, 68, 68, 0.2)'}}>
              <h4 style={{margin:'0 0 0.5rem 0', color:'var(--danger)'}}>To'liq reset (Format)</h4>
              <p style={{fontSize:'0.8rem', color:'var(--text-muted)', marginBottom:'1.5rem'}}>Hamma narsani (AI bilimlar va sozlamalar) o'chirib yuboradi.</p>
              <button className="btn btn-sm btn-danger" onClick={handleResetAll} disabled={loading} style={{width:'100%'}}>
                 ⚠️ Tizimni reset qilish
              </button>
           </div>
        </div>
      </div>

      <div className="grid-cards" style={{gridTemplateColumns:'1fr 1fr', gap:'2rem'}}>
        <div className="glass-card">
          <div className="summary-title" style={{marginBottom:'1rem'}}>Guruh bo'yicha o'chirish</div>
          <div className="table-wrapper" style={{maxHeight:'400px', overflowY:'auto'}}>
            <table>
              <thead><tr><th>Guruh nomi</th><th>Amal</th></tr></thead>
              <tbody>
                {groups.map(g => (
                  <tr key={g.id}>
                    <td>{g.title} <br/><small style={{color:'var(--text-muted)'}}>{g.total_messages} ta xabar</small></td>
                    <td><button className="btn btn-sm btn-danger" onClick={() => deleteGroup(g.id, g.title)}>🗑️</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass-card">
          <div className="summary-title" style={{marginBottom:'1rem'}}>Bittalab xabarlarni o'chirish</div>
          <div className="table-wrapper" style={{maxHeight:'400px', overflowY:'auto'}}>
            <table>
              <thead><tr><th>Xabar</th><th>Amal</th></tr></thead>
              <tbody>
                {messages.map(m => (
                  <tr key={m.id}>
                    <td style={{fontSize:'0.8rem'}}>
                      <strong>{m.full_name}</strong>: {m.text?.substring(0, 50)}{m.text?.length > 50 ? '...' : ''}
                    </td>
                    <td><button className="btn btn-sm btn-danger" onClick={() => deleteMessage(m.id)}>🗑️</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex-between" style={{marginTop:'1rem'}}>
            <button className="btn btn-sm" disabled={msgPage === 0} onClick={() => setMsgPage(p => p - 1)}>Orqaga</button>
            <span style={{fontSize:'0.8rem'}}>{msgPage + 1} / {Math.ceil(totalMsgs / 10) || 1}</span>
            <button className="btn btn-sm" disabled={(msgPage + 1) * 10 >= totalMsgs} onClick={() => setMsgPage(p => p + 1)}>Oldinga</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Profile({ token, setUsername, showFlash }) {
  const [f, setF] = useState({ username: '', pass: '', cpass: '' });
  const [saving, setSaving] = useState(false);

  const submit = (e) => {
    e.preventDefault();
    if (f.pass && f.pass !== f.cpass) { showFlash('Parollar mos kelmadi', 'error'); return; }
    setSaving(true);
    fetch(`${API_URL}/auth/me`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ username: f.username || undefined, password: f.pass || undefined })
    })
    .then(res => res.json()).then(d => {
      setSaving(false);
      if(d.status === 'success') { showFlash('Profil ma\'lumotlari yangilandi'); if(d.new_username) setUsername(d.new_username); }
      else showFlash('Xatolik yuz berdi', 'error');
    }).catch(() => { setSaving(false); showFlash('Server xatosi', 'error'); });
  };
  return (<>
    <h2 className="header-title">Profil sozlamalari</h2>
    <div className="glass-card" style={{maxWidth:'600px'}}>
      <form onSubmit={submit}>
        <div className="form-group"><label>Yangi foydalanuvchi nomi</label><input type="text" value={f.username} onChange={e => setF({...f, username: e.target.value})} placeholder="Foydalanuvchi nomi..." /></div>
        <div className="form-group"><label>Yangi parol</label><input type="password" value={f.pass} onChange={e => setF({...f, pass: e.target.value})} placeholder="••••••••" /></div>
        <div className="form-group"><label>Parolni tasdiqlash</label><input type="password" value={f.cpass} onChange={e => setF({...f, cpass: e.target.value})} placeholder="••••••••" /></div>
        <button type="submit" className="btn" disabled={saving}>{saving ? 'Saqlanmoqda...' : "O'zgarishlarni saqlash"}</button>
      </form>
    </div>
  </>);
}

function Login({ onLogin }) {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const handleSubmit = (e) => {
    e.preventDefault(); setLoading(true);
    fetch(`${API_URL}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) })
    .then(res => res.json()).then(data => { setLoading(false); if (data.access_token) onLogin(data.access_token); else setError('Xato: Foydalanuvchi nomi yoki parol noto\'g\'ri.'); })
    .catch(() => { setLoading(false); setError('Xato: Server bilan aloqa yo\'q.'); });
  };
  return (<div className="login-screen"><div className="glass-card login-card">
    <div className="stat-icon-wrapper" style={{margin:'0 auto 2rem', background:'var(--primary)', width:60, height:60}}><svg style={{width:32, height:32, fill:'#fff'}} viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg></div>
    <h2>UyQur Tizimi</h2><p>Admin panelga kirish</p>{error && <div className="error-msg">{error}</div>}
    <form onSubmit={handleSubmit} style={{textAlign:'left'}}>
      <div className="form-group"><label>Foydalanuvchi nomi</label><input type="text" value={form.username} onChange={e => setForm({...form, username: e.target.value})} placeholder="Login..." /></div>
      <div className="form-group"><label>Parol</label><input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} placeholder="••••••••" /></div>
      <button type="submit" className="btn" disabled={loading}>{loading ? 'Kirilmoqda...' : 'Kirish'}</button>
    </form>
  </div></div>);
}

export default App;
