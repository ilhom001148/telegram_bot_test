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
  Company: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z"/></svg>,
  Id: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M19 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-7-2h5v-2h-5v2zm-4-2h3v-2H8v2zm0-3h3V8H8v3zm4 0h5V8h-5v3z"/></svg>,
  Phone: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>,
  User: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>,
  Users: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>,
  Clock: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"/></svg>,
  Shield: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>,
  Grid: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M4 11h5V5H4v6zm0 7h5v-6H4v6zm7 0h5v-6h-5v6zm6 0h5v-6h-5v6zM11 11h5V5h-5v6zm6-6v6h5V5h-5z"/></svg>,
  List: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M4 14h4v-4H4v4zm0 5h4v-4H4v4zM4 9h4V5H4v4zm5 5h12v-4H9v4zm0 5h12v-4H9v4zM9 5v4h12V5H9z"/></svg>,
  Search: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>,
  ExternalLink: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/></svg>,
  Flag: ({className}) => <svg className={className} viewBox="0 0 24 24" fill="currentColor"><path d="M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6h-5.6z"/></svg>,
  Calendar: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zm0-12H5V6h14v2zm-7 5h5v5h-5v-5z"/></svg>,
  ChevronDown: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/></svg>,
  Add: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>,
  CheckCircle: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>,
  MessageCircle: () => <svg className="svg-icon" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10z"/></svg>,
};

const getAvatarColor = (name) => {
  const colors = ['#6366f1', '#4f46e5', '#4338ca', '#8b5cf6', '#7c3aed', '#6d28d9'];
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return colors[Math.abs(hash) % colors.length];
};

const getInitials = (name) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
};

const formatDate = (dateStr) => {
  if (!dateStr) return '—';
  try {
    // Agar vaqtda timezone bo'lmasa, uni UTC deb hisoblaymiz (Z qo'shamiz)
    let normalized = dateStr.toString().replace(' ', 'T');
    if (!normalized.includes('Z') && !normalized.includes('+') && !normalized.includes('-')) {
      normalized += 'Z';
    }
    
    const d = new Date(normalized);
    if (isNaN(d.getTime())) return dateStr;
    
    // Foydalanuvchi mintaqasida (Toshkent) ko'rsatish
    return d.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).replace(',', '');
  } catch (e) {
    return dateStr;
  }
};

function ArchiveManager({ token, showFlash }) {
  const [summaries, setSummaries] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  
  const [answeringId, setAnsweringId] = useState(null);
  const [answerText, setAnswerText] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/messages/archive/summary`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json())
      .then(data => { setSummaries(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [token]);

  const fetchQuestions = (date) => {
    setDetailLoading(true);
    fetch(`${API_URL}/messages/archive/questions-by-date/${date}`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json())
      .then(data => { setQuestions(data); setDetailLoading(false); })
      .catch(() => setDetailLoading(false));
  };

  const openFolder = (date) => {
    setSelectedDate(date);
    fetchQuestions(date);
  };

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
       showFlash("Javob saqlandi");
       fetchQuestions(selectedDate);
    })
    .catch(() => { setSending(false); showFlash("Xatolik yuz berdi", "error"); });
  };

  if (loading) return <div className="loader"></div>;

  return (
    <div style={{animation: 'fadeIn 0.5s ease-out'}}>
      {!selectedDate ? (
        <>
          <h2 className="header-title">Kunlik Arxiv (Savollar hisoboti)</h2>
          <div className="grid-cards" style={{gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '2rem'}}>
            {summaries.length > 0 ? summaries.map((s, i) => (
              <div key={i} className="glass-card archive-folder-card" onClick={() => openFolder(s.date)}>
                <div className="folder-icon-glow">
                   <Icons.Folder />
                </div>
                <div className="folder-content">
                   <div className="folder-date">
                     {(() => {
                        const d = new Date(s.date);
                        const m = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"];
                        return `${d.getDate()} - ${m[d.getMonth()]}, ${d.getFullYear()}`;
                     })()}
                   </div>
                   <div className="folder-stats-grid">
                      <div className="folder-stat">
                         <span className="stat-num">{s.total}</span>
                         <span className="stat-desc">Savol</span>
                      </div>
                      <div className="folder-stat">
                         <span className="stat-num" style={{color:'var(--success)'}}>{s.answered}</span>
                         <span className="stat-desc">Javob</span>
                      </div>
                      <div className="folder-stat">
                         <span className="stat-num" style={{color: s.unanswered > 0 ? 'var(--danger)' : 'var(--text-muted)'}}>{s.unanswered}</span>
                         <span className="stat-desc">Kutilmoqda</span>
                      </div>
                   </div>
                </div>
                <div className="folder-footer">
                   <span>Hisobotni ochish</span>
                   <Icons.Logout style={{width:14, transform:'rotate(0deg)'}} />
                </div>
              </div>
            )) : <p style={{gridColumn:'1/-1', textAlign:'center', padding:'3rem', color:'var(--text-muted)'}}>Hozircha arxivda savollar mavjud emas.</p>}
          </div>
        </>
      ) : (
        <>
          <div className="flex-between" style={{marginBottom:'2rem'}}>
             <div>
                <h2 className="header-title" style={{margin:0}}>{selectedDate} kungi savollar</h2>
                <p style={{fontSize:'0.85rem', color:'var(--text-muted)', marginTop:'5px'}}>Kunlik faoliyat hisoboti</p>
             </div>
             <div style={{display:'flex', gap:'12px'}}>
               <a href={`${API_URL}/export/daily-report?date=${selectedDate}`} className="btn btn-sm btn-outline" style={{borderColor:'var(--primary)', color:'var(--primary)'}}>
                 📥 Excel
               </a>
               <button className="btn btn-sm" onClick={() => window.print()} style={{background:'var(--primary)'}}>
                 📄 PDF / Chop etish
               </button>
               <button className="btn btn-sm btn-danger" onClick={() => setSelectedDate(null)}> Orqaga </button>
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
                      <tr key={q.id} style={{height: '100px', verticalAlign: 'top'}}>
                        <td style={{whiteSpace:'nowrap', fontSize:'0.85rem', padding:'25px 15px', color:'var(--text-muted)'}}>
                           {q.telegram_app_link ? (
                             <a href={q.telegram_app_link} className="tg-link" onClick={e => e.stopPropagation()} title="Telegramda ko'rish">{formatDate(q.created_at)}</a>
                           ) : formatDate(q.created_at)}
                        </td>
                        <td style={{padding:'25px 10px'}}>
                           {q.telegram_app_link ? (
                             <a href={q.telegram_app_link} className="tg-link" onClick={e => e.stopPropagation()} style={{textDecoration:'none', color:'inherit'}} title="Telegramda ko'rish">
                               <div style={{fontWeight:'700', fontSize:'1rem', color:'#fff'}}>{q.full_name}</div>
                               <div style={{fontSize:'0.8rem', color:'var(--text-muted)', marginTop:'4px'}}>@{q.username || 'anonim'}</div>
                             </a>
                           ) : (
                             <>
                               <div style={{fontWeight:'700', fontSize:'1rem', color:'#fff'}}>{q.full_name}</div>
                               <div style={{fontSize:'0.8rem', color:'var(--text-muted)', marginTop:'4px'}}>@{q.username || 'anonim'}</div>
                             </>
                           )}
                        </td>
                        <td style={{fontSize:'0.95rem', lineHeight:'1.7', color:'#e2e8f0', cursor:'pointer', padding:'25px 10px'}} 
                            onClick={() => { setAnsweringId(q.id); setAnswerText(q.answer_text || ''); }}
                        >
                            {q.telegram_app_link ? (
                               <a href={q.telegram_app_link} className="tg-link" onClick={e => e.stopPropagation()} title="Telegramda ko'rish">{q.text}</a>
                            ) : q.text}
                        </td>
                        <td style={{fontSize:'0.95rem', padding:'25px 10px'}}>
                           {answeringId === q.id ? (
                               <form onSubmit={(e) => handleSendAnswer(e, q.id)}>
                                    <textarea 
                                        rows="2" 
                                        value={answerText} 
                                        onChange={e => setAnswerText(e.target.value)}
                                        placeholder="Javob yozing..."
                                        style={{width:'100%', padding:'10px', fontSize:'0.9rem', marginBottom:'8px', borderRadius:'10px', background:'rgba(0,0,0,0.1)', color:'#fff', border:'1px solid var(--primary)'}}
                                        autoFocus
                                    />
                                    <div style={{display:'flex', gap:'8px'}}>
                                        <button type="submit" className="btn btn-sm" disabled={sending} style={{flex:1, fontSize:'0.75rem'}}>{sending ? '...' : 'Saqlash'}</button>
                                        <button type="button" className="btn btn-sm btn-danger" onClick={() => setAnsweringId(null)} style={{fontSize:'0.75rem'}}>✖</button>
                                    </div>
                               </form>
                           ) : (
                               q.answer_text ? (
                                  <div style={{position:'relative', padding:'10px', background:'rgba(255,255,255,0.03)', borderRadius:'10px'}}>
                                     <div onClick={() => { setAnsweringId(q.id); setAnswerText(q.answer_text); }} style={{cursor:'pointer'}} title="Tahrirlash uchun bosing">
                                        <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'6px'}}>
                                           <div style={{color:'var(--primary)', fontWeight:'700', fontSize:'0.7rem', textTransform:'uppercase'}}>
                                              {q.answered_by || 'Bot'} JAVOBI:
                                           </div>
                                           {q.answered_at && (
                                              <div style={{fontSize:'0.65rem', color:'var(--text-muted)'}}>
                                                 Javob vaqti: {q.answered_at}
                                              </div>
                                           )}
                                        </div>
                                        <div style={{color:'#e2e8f0'}}>{q.answer_text}</div>
                                     </div>
                                     {q.telegram_app_link && (
                                        <a href={q.telegram_app_link} className="tg-link" onClick={e => e.stopPropagation()} 
                                           style={{display:'inline-block', marginTop:'8px', fontSize:'0.7rem', textDecoration:'underline'}}
                                           title="Telegramda ko'rish">
                                           Telegramda ko'rish ↗
                                        </a>
                                     )}
                                  </div>
                               ) : (
                                 <div style={{textAlign:'center'}}>
                                   <span style={{color:'var(--text-muted)', fontSize:'0.85rem', fontStyle:'italic', display:'block', marginBottom:'8px'}}>Javobsiz</span>
                                   <button className="btn btn-sm" onClick={() => { setAnsweringId(q.id); setAnswerText(''); }} style={{fontSize:'0.75rem', padding:'6px 14px'}}>Javob berish</button>
                                 </div>
                               )
                           )}
                        </td>
                        <td style={{textAlign:'center', padding:'25px 10px'}}>
                           {q.is_answered && (
                              <div style={{fontSize:'0.65rem', color:'var(--text-muted)', marginBottom:'5px'}}>
                                 {q.answered_at ? q.answered_at : 'Yaqinda'}
                              </div>
                           )}
                           <span className={`badge ${q.is_answered ? 'badge-kb' : 'badge-unanswered'}`} style={{fontSize:'0.75rem', padding:'6px 14px'}}>
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
            <div className={`nav-link ${activeTab === 'companies' ? 'active' : ''}`} onClick={() => setActiveTab('companies')}><Icons.Company /> <span>Kompaniyalar</span></div>
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
        {activeTab === 'dashboard' && <Dashboard token={token} showFlash={showFlash} />}
        {activeTab === 'companies' && <CompaniesManager token={token} />}
        {activeTab === 'messages' && <Messages token={token} showFlash={showFlash} />}
        {activeTab === 'groups' && <Groups token={token} showFlash={showFlash} askConfirm={askConfirm} />}
        {activeTab === 'knowledge' && <KnowledgeBase token={token} showFlash={showFlash} askConfirm={askConfirm} />}
        {activeTab === 'broadcast' && <BroadcastManager token={token} showFlash={showFlash} />}
        {activeTab === 'settings' && <BotSettings token={token} showFlash={showFlash} askConfirm={askConfirm} />}
        {activeTab === 'profile' && <Profile token={token} setUsername={setUsername} showFlash={showFlash} />}
        {activeTab === 'database' && <DatabaseManager token={token} showFlash={showFlash} askConfirm={askConfirm} />}
        {activeTab === 'archive' && <ArchiveManager token={token} showFlash={showFlash} />}
        {activeTab === 'customers' && <CustomersManager token={token} showFlash={showFlash} />}
      </div>
    </div>
  );
}

function CompaniesManager({ token }) {
  const EMPTY_FORM = {
    name: '', brand_name: '', main_currency: 'UZS', extra_currency: '',
    phone: '', director: '', responsible_name: '', responsible_phone: '',
    status: 'Yangi', subscription_start: '', subscription_end: '', is_active: true,
  };

  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [logoFile, setLogoFile] = useState(null);
  const [logoPreview, setLogoPreview] = useState(null);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});
  const [deleteId, setDeleteId] = useState(null);
  const [flash, setFlash] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [groupBy, setGroupBy] = useState('none'); // none, responsible, status
  const [collapsedGroups, setCollapsedGroups] = useState({}); // Default empty, we'll handle default state in render

  const toggleGroup = (id) => {
    setCollapsedGroups(prev => {
      // If it was undefined, we need to know what the default was
      const isCurrentlyCollapsed = prev[id] === undefined ? (groupBy !== 'none') : prev[id];
      return { ...prev, [id]: !isCurrentlyCollapsed };
    });
  };

  const showMsg = (text, type = 'success') => {
    setFlash({ text, type });
    setTimeout(() => setFlash(null), 3000);
  };

  const fetchCompanies = () => {
    setLoading(true);
    fetch(`${API_URL}/companies/external`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(d => { setCompanies(d || []); setLoading(false); })
      .catch(() => setLoading(false));
  };
  useEffect(() => { fetchCompanies(); }, [token]);

  // ReadOnly check
  const isExternal = (id) => typeof id === 'string' && id.startsWith('ext-');

  // ── Phone validation ──────────────────────────────────────
  const phoneRe = /^\+?[\d\s\-()\u200c]{7,20}$/;
  const validate = () => {
    const e = {};
    if (!form.name.trim()) e.name = "Kompaniya nomi majburiy";
    if (form.phone && !phoneRe.test(form.phone)) e.phone = "Noto'g'ri format (misol: +998901234567)";
    if (form.responsible_phone && !phoneRe.test(form.responsible_phone)) e.responsible_phone = "Noto'g'ri format";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  // ── Logo handler ──────────────────────────────────────────
  const handleLogo = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const allowed = ['image/jpeg','image/png','image/webp','image/gif','image/svg+xml'];
    if (!allowed.includes(file.type)) { showMsg('Faqat JPEG, PNG, WebP, GIF yoki SVG rasm yuklanadi', 'error'); return; }
    if (file.size > 5 * 1024 * 1024) { showMsg("Logo hajmi 5MB dan oshmasligi kerak", 'error'); return; }
    setLogoFile(file);
    setLogoPreview(URL.createObjectURL(file));
  };

  // ── Open form ─────────────────────────────────────────────
  const openEdit = (c) => {
    setEditingId(c.id);
    setForm({
      name: c.name || '', brand_name: c.brand_name || '',
      main_currency: c.main_currency || 'UZS', extra_currency: c.extra_currency || '',
      phone: c.phone || '', director: c.director || '',
      responsible_name: c.responsible_name || '', responsible_phone: c.responsible_phone || '',
      status: c.status || 'Yangi',
      subscription_start: c.subscription_start ? c.subscription_start.slice(0,16) : '',
      subscription_end:   c.subscription_end   ? c.subscription_end.slice(0,16)   : '',
      is_active: c.is_active,
      logo_url: c.logo_url ? (c.logo_url.startsWith('http') ? c.logo_url : `${API_URL}${c.logo_url}`) : null,
    });
    setLogoFile(null);
    setLogoPreview(c.logo_url ? (c.logo_url.startsWith('http') ? c.logo_url : `${API_URL}${c.logo_url}`) : null);
    setErrors({});
    setShowForm(true);
  };

  // ── Submit ────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setSaving(true);
    const fd = new FormData();
    Object.entries(form).forEach(([k, v]) => { if (v !== '' && v !== null && v !== undefined) fd.append(k, v); });
    if (logoFile) fd.append('logo', logoFile);

    const url = editingId ? `${API_URL}/companies/${editingId}` : `${API_URL}/companies/`;
    const method = editingId ? 'PUT' : 'POST';
    try {
      const res = await fetch(url, { method, headers: { Authorization: `Bearer ${token}` }, body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Xato');
      showMsg(editingId ? 'Kompaniya yangilandi ✅' : 'Kompaniya qo\'shildi ✅');
      setShowForm(false);
      fetchCompanies();
    } catch (err) { showMsg(err.message, 'error'); }
    finally { setSaving(false); }
  };

  // ── Toggle active ─────────────────────────────────────────
  const handleToggle = async (id) => {
    try {
      const res = await fetch(`${API_URL}/companies/${id}/toggle`, { method: 'PATCH', headers: { Authorization: `Bearer ${token}` } });
      const data = await res.json();
      if (res.ok) {
        setCompanies(prev => prev.map(c => c.id === id ? { ...c, is_active: data.is_active, status: data.is_active ? 'Faol' : 'To\'xtatilgan' } : c));
      } else {
        showMsg(data.detail || 'Xatolik yuz berdi', 'error');
      }
    } catch (err) {
      showMsg('Server bilan ulanishda xatolik', 'error');
    }
  };

  // ── Delete ────────────────────────────────────────────────
  const handleDelete = async (id) => {
    await fetch(`${API_URL}/companies/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
    showMsg('Kompaniya o\'chirildi', 'error');
    setDeleteId(null);
    fetchCompanies();
  };

  const statusLabel = { Yangi: { label: 'Yangi', color: '#6366f1' }, Faol: { label: 'Faol', color: 'var(--success)' }, "To'xtatilgan": { label: 'To\'xtatilgan', color: '#f59e0b' }, "Bekor qilingan": { label: 'Bekor qilingan', color: 'var(--danger)' } };
  const inp = { width:'100%', padding:'10px 14px', background:'rgba(255,255,255,0.06)', border:'1px solid var(--card-border)', borderRadius:'10px', color:'#fff', fontSize:'0.9rem', outline:'none' };
  const errStyle = { fontSize:'0.75rem', color:'var(--danger)', marginTop:'4px' };

  const statusClassMap = {
    'Faol': 'status-active',
    'Yangi': 'status-new',
    'To\'xtatilgan': 'status-stopped',
    'Bekor qilingan': 'status-cancelled'
  };

  return (
    <div style={{animation:'fadeIn 0.5s ease-out', position:'relative'}}>

      {/* Local flash */}
      {flash && <div className={`flash-banner ${flash.type}`} style={{position:'fixed',top:'20px',right:'20px',zIndex:9999}}>{flash.text}</div>}

      {/* Delete confirm overlay */}
      {deleteId && (
        <div className="modal-overlay">
          <div className="confirm-modal">
            <div className="modal-icon"><Icons.Warning /></div>
            <div className="modal-title">Kompaniyani o'chirish</div>
            <div className="modal-text">Bu amalni ortga qaytarib bo'lmaydi. Davom etasizmi?</div>
            <div className="modal-actions">
              <button className="modal-btn modal-btn-cancel" onClick={() => setDeleteId(null)}>Yo'q</button>
              <button className="modal-btn modal-btn-confirm" onClick={() => handleDelete(deleteId)}>Ha, o'chirish</button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex-between" style={{marginBottom:'2rem'}}>
        <h2 className="header-title" style={{margin:0}}>Kompaniyalar boshqaruvi</h2>
      </div>

      {/* Search & View Toggle */}
      <div style={{marginBottom:'1rem', display:'flex', alignItems:'center', gap:'1rem', flexWrap:'wrap'}}>
        <div style={{position:'relative', flex:1, maxWidth:'400px'}}>
           <div style={{position:'absolute', left:'14px', top:'50%', transform:'translateY(-50%)', color:'var(--text-muted)', display:'flex', pointerEvents:'none'}}>
              <Icons.Search />
           </div>
           <input 
             type="text" 
             placeholder="Qidirish (Nomi yoki raqami bo'yicha)..." 
             style={{...inp, width: '100%', paddingLeft:'42px'}}
             value={searchQuery}
             onChange={e => setSearchQuery(e.target.value)}
           />
        </div>
        
        <div style={{display:'flex', background:'rgba(255,255,255,0.05)', padding:'4px', borderRadius:'12px', border:'1px solid var(--card-border)'}}>
           <button 
             onClick={() => setViewMode('grid')}
             style={{padding:'8px 12px', borderRadius:'8px', border:'none', cursor:'pointer', display:'flex', alignItems:'center', gap:'8px', fontSize:'0.85rem',
               background: viewMode === 'grid' ? 'var(--primary)' : 'transparent', 
               color: viewMode === 'grid' ? '#fff' : 'var(--text-muted)',
               transition: 'all 0.3s'}}
             title="Board ko'rinishi">
             <Icons.Grid /> <span className="hide-mobile">Board</span>
           </button>
           <button 
             onClick={() => setViewMode('list')}
             style={{padding:'8px 12px', borderRadius:'8px', border:'none', cursor:'pointer', display:'flex', alignItems:'center', gap:'8px', fontSize:'0.85rem',
               background: viewMode === 'list' ? 'var(--primary)' : 'transparent', 
               color: viewMode === 'list' ? '#fff' : 'var(--text-muted)',
               transition: 'all 0.3s'}}
             title="Ro'yxat ko'rinishi">
             <Icons.List /> <span className="hide-mobile">Ro'yxat</span>
           </button>
        </div>
 
        {viewMode === 'list' && (
          <div style={{display:'flex', alignItems:'center', background:'rgba(255,255,255,0.03)', padding:'4px', borderRadius:'14px', border:'1px solid var(--card-border)', gap:'4px'}}>
            <button 
              onClick={() => setGroupBy('none')}
              style={{padding:'6px 16px', borderRadius:'10px', border:'none', cursor:'pointer', fontSize:'0.8rem', fontWeight:'600',
                background: groupBy === 'none' ? 'rgba(255,255,255,0.1)' : 'transparent',
                color: groupBy === 'none' ? '#fff' : 'var(--text-muted)',
                transition:'all 0.2s'}}
            >
              Umumiy
            </button>
            <button 
              onClick={() => setGroupBy('responsible')}
              style={{padding:'6px 16px', borderRadius:'10px', border:'none', cursor:'pointer', fontSize:'0.8rem', fontWeight:'600',
                background: groupBy === 'responsible' ? 'rgba(255,255,255,0.1)' : 'transparent',
                color: groupBy === 'responsible' ? '#fff' : 'var(--text-muted)',
                transition:'all 0.2s'}}
            >
              Mas'ul bo'yicha
            </button>
            <button 
              onClick={() => setGroupBy('status')}
              style={{padding:'6px 16px', borderRadius:'10px', border:'none', cursor:'pointer', fontSize:'0.8rem', fontWeight:'600',
                background: groupBy === 'status' ? 'rgba(255,255,255,0.1)' : 'transparent',
                color: groupBy === 'status' ? '#fff' : 'var(--text-muted)',
                transition:'all 0.2s'}}
            >
              Nofaollik bo'yicha
            </button>
          </div>
        )}
      </div>

      {loading ? <div className="loader"/> : (
        <React.Fragment>
          {(() => {
            const filtered = companies.filter(c => 
              c.name.toLowerCase().includes((searchQuery||'').toLowerCase()) || 
              (c.brand_name && c.brand_name.toLowerCase().includes((searchQuery||'').toLowerCase())) ||
              (c.phone && (c.phone+'').includes(searchQuery))
            );

            if (filtered.length === 0) {
              return (
                <div className="glass-card" style={{marginTop:'1.5rem', textAlign:'center', padding:'4rem 2rem', color:'var(--text-muted)'}}>
                  <div style={{opacity:0.4, marginBottom:'1rem'}}><Icons.Company /></div>
                  <p>Hech qanday ma'lumot topilmadi.</p>
                  <p style={{fontSize:'0.85rem', marginTop:'5px'}}>Kompaniyalar har 24 soatda avtomatik ravishda tashqi bazadan yangilanadi.</p>
                </div>
              );
            }

            if (viewMode === 'list') {
              // Grouping Logic - Simplified & Modern
              let groups = [];
                  if (groupBy === 'responsible') {
                    const responsibles = [...new Set(filtered.map(c => c.responsible_name || 'Mas\'ul biriktirilmagan'))];
                    groups = responsibles.map((name, idx) => ({
                      id: `resp-${idx}`,
                      title: name,
                      color: '#6366f1', // Uniform Indigo
                      items: filtered.filter(c => (c.responsible_name || 'Mas\'ul biriktirilmagan') === name)
                    }));
                  } else if (groupBy === 'status') {
                    const now = new Date();
                    groups = [
                      { 
                        id: 'inactive', 
                        title: 'Nofaol / Muddati tugaganlar', 
                        color: '#ef4444', 
                        items: filtered.filter(c => !c.is_active || (c.subscription_end && new Date(c.subscription_end) <= now)) 
                      }
                    ];
                  } else {
                // 'none' mode - Sorted by subscription_end (ascending: closest expiry first)
                const sortedItems = [...filtered].sort((a, b) => {
                  const dateA = a.subscription_end ? new Date(a.subscription_end) : new Date(2099, 11, 31);
                  const dateB = b.subscription_end ? new Date(b.subscription_end) : new Date(2099, 11, 31);
                  return dateA - dateB;
                });

                groups = [
                  { 
                    id: 'all', 
                    title: 'Barcha korxonalar (Muddati bo\'yicha saralangan)', 
                    color: '#6366f1', 
                    items: sortedItems
                  }
                ];
              }

              return (
                <div style={{marginTop:'1.5rem', display:'flex', flexDirection:'column', gap:'1.5rem'}}>
                  {groups.map(st => st.items.length > 0 && (
                      <div key={st.id} className="glass-card" style={{padding:0, overflow:'hidden', border:'1px solid var(--card-border)'}}>
                        <div 
                          className="list-group-header" 
                          onClick={() => toggleGroup(st.id)}
                          style={{padding:'1rem 1.5rem', background:'rgba(255,255,255,0.02)', borderBottom:'1px solid var(--card-border)', cursor:'pointer', display:'flex', alignItems:'center', gap:'1rem'}}
                        >
                          <div style={{transform: (collapsedGroups[st.id] === undefined ? (groupBy !== 'none') : collapsedGroups[st.id]) ? 'rotate(-90deg)' : 'rotate(0deg)', transition:'transform 0.2s', display:'flex', color:'var(--text-muted)'}}>
                            <Icons.ChevronDown />
                          </div>
                          <div style={{fontWeight:700, fontSize:'1rem', color:'#fff', flex:1}}>
                            {st.title}
                            <span style={{marginLeft:'10px', fontSize:'0.8rem', color:'var(--text-muted)', fontWeight:400}}>({st.items.length} ta)</span>
                          </div>
                          {st.id !== 'all' && <div style={{width:8, height:8, borderRadius:'50%', background:st.color, boxShadow:`0 0 10px ${st.color}`}}></div>}
                        </div>
 
                         {!(collapsedGroups[st.id] === undefined ? (groupBy !== 'none' && st.id !== 'inactive') : collapsedGroups[st.id]) && (
                           <div className="table-wrapper">
                             <table className="clickup-table">
                               <thead>
                                 <tr>
                                   <th className="clickup-column-header" style={{width:'30%', paddingLeft:'1.5rem'}}>Kompaniya</th>
                                   <th className="clickup-column-header">Direktor / Brand</th>
                                   <th className="clickup-column-header">Aloqa</th>
                                   <th className="clickup-column-header">Obuna</th>
                                   <th className="clickup-column-header" style={{textAlign:'center'}}>Holati</th>
                                   <th className="clickup-column-header" style={{textAlign:'center'}}>Boshqaruv</th>
                                 </tr>
                               </thead>
                               <tbody>
                                 {st.items.map(c => {
                                   const getExpInfo = (dateStr) => {
                                     if (!dateStr) return null;
                                     const end = new Date(dateStr);
                                     const now = new Date();
                                     const diff = end - now;
                                     const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
                                     if (days < 0) return { color: '#ef4444', icon: '⚠️', text: 'Tugagan' };
                                     if (days <= 30) return { color: '#f59e0b', icon: '⏳', text: `${days} kun` };
                                     return null;
                                   };
                                   const exp = getExpInfo(c.subscription_end);
 
                                   return (
                                     <tr key={c.id} className="clickup-row" onClick={() => openEdit(c)}>
                                       <td style={{paddingLeft:'1.5rem'}}>
                                         <div style={{display:'flex', alignItems:'center', gap:'12px'}}>
                                           <div style={{width:36, height:36, borderRadius:10, overflow:'hidden', background:'rgba(255,255,255,0.03)', flexShrink:0, display:'flex', alignItems:'center', justifyContent:'center', border:'1px solid rgba(255,255,255,0.05)'}}>
                                             {c.logo_url ? <img src={c.logo_url.startsWith('http') ? c.logo_url : `${API_URL}${c.logo_url}`} style={{width:'100%', height:'100%', objectFit:'cover'}} /> : <Icons.Company style={{width:18, opacity:0.3}}/>}
                                           </div>
                                           <div>
                                             <div style={{fontWeight:700, fontSize:'0.9rem', color:'#fff'}}>{c.name}</div>
                                             <div style={{fontSize:'0.7rem', color:'var(--text-muted)', letterSpacing:'0.5px'}}>ID: {c.id.toString().replace('ext-','')}</div>
                                           </div>
                                         </div>
                                       </td>
                                       <td>
                                         <div style={{fontSize:'0.85rem', fontWeight:'600', color:'#e2e8f0'}}>{c.director || '—'}</div>
                                         {c.brand_name && <div style={{fontSize:'0.7rem', color:'var(--primary)', fontWeight:'500', marginTop:'2px'}}>{c.brand_name}</div>}
                                       </td>
                                       <td>
                                         <div className="meta-icon-group" style={{gap:'6px'}}>
                                           <Icons.Phone style={{width:13, opacity:0.6}} />
                                           <span style={{fontSize:'0.85rem', color:'var(--text-secondary)'}}>{c.phone || '—'}</span>
                                         </div>
                                       </td>
                                       <td>
                                         <div style={{fontSize:'0.75rem', lineHeight:'1.4'}}>
                                            <div style={{color:'var(--text-muted)'}}>Tugash: <span style={{color: exp ? exp.color : '#fff', fontWeight:600}}>{c.subscription_end ? new Date(c.subscription_end).toLocaleDateString('uz-UZ') : '—'}</span></div>
                                            {exp && <div style={{color: exp.color, fontSize:'0.65rem', fontWeight:700, textTransform:'uppercase', marginTop:'2px'}}>{exp.icon} {exp.text}</div>}
                                         </div>
                                       </td>
                                       <td style={{textAlign:'center'}}>
                                           {(() => {
                                             const isExpired = c.subscription_end && new Date(c.subscription_end) <= new Date();
                                             const isActive = c.is_active && !isExpired;
                                             return (
                                               <div style={{display:'inline-flex', alignItems:'center', gap:'6px', padding:'4px 10px', borderRadius:'20px', background: isActive ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', border:`1px solid ${isActive ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`}}>
                                                  <div style={{width:6, height:6, borderRadius:'50%', background: isActive ? '#10b981' : '#ef4444'}}></div>
                                                  <span style={{fontSize:'0.7rem', fontWeight:700, color: isActive ? '#10b981' : '#ef4444', textTransform:'uppercase'}}>{isActive ? 'Faol' : 'Nofaol'}</span>
                                               </div>
                                             );
                                           })()}
                                        </td>
                                    <td style={{textAlign:'center'}} onClick={e => e.stopPropagation()}>
                                      <div style={{display:'flex', alignItems:'center', justifyContent:'center', gap:'12px'}}>
                                         <div onClick={() => handleToggle(c.id)} style={{cursor:'pointer', width:32, height:16, borderRadius:8, 
                                            background: (c.is_active && !(c.subscription_end && new Date(c.subscription_end) <= new Date())) ? 'var(--primary)' : 'rgba(255,255,255,0.1)',
                                            display:'flex', alignItems:'center', padding:'2px', transition:'all 0.3s'}}>
                                            <div style={{width:12, height:12, borderRadius:'50%', background:'#fff',
                                              transform: (c.is_active && !(c.subscription_end && new Date(c.subscription_end) <= new Date())) ? 'translateX(16px)' : 'translateX(0)', transition:'transform 0.3s'}}/>
                                         </div>
                                         {!isExternal(c.id) && (
                                            <button onClick={()=>setDeleteId(c.id)} style={{background:'none', border:'none', color:'rgba(239,68,68,0.6)', cursor:'pointer', padding:4, fontSize:'0.9rem', transition:'color 0.2s'}} onMouseEnter={e=>e.target.style.color='#ef4444'} onMouseLeave={e=>e.target.style.color='rgba(239,68,68,0.6)'} title="O'chirish">🗑</button>
                                         )}
                                      </div>
                                    </td>
                                  </tr>
                                 );
                                 })}
                               </tbody>
                             </table>
                           </div>
                         )}
                      </div>
                  ))}
                </div>
              );
            }

            return (
              <div className="grid-cards" style={{marginTop:'1.5rem'}}>
                {filtered.map(c => (
              <div key={c.id} className="premium-card company-card fadeInUp" 
                   style={{ animationDelay: `${companies.indexOf(c) * 0.05}s`, opacity: c.is_active ? 1 : 0.7, filter: c.is_active ? 'none' : 'grayscale(0.3)' }}
                   onClick={() => openEdit(c)}>
                
                <div className="card-header" style={{position:'relative', padding:'1.5rem', display:'flex', flexDirection:'column', alignItems:'flex-start', gap:'1rem'}}>
                  <div className="card-avatar" style={{
                    width:'60px', height:'60px', borderRadius:'15px', overflow:'hidden', 
                    background:'rgba(255,255,255,0.05)', border:'1px solid var(--card-border)',
                    boxShadow:'0 8px 16px rgba(0,0,0,0.2)', position:'absolute', left:'1.5rem', top:'1.5rem'
                  }}>
                    {c.logo_url ? (
                      <img src={c.logo_url.startsWith('http') ? c.logo_url : `${API_URL}${c.logo_url}`} 
                        alt="logo" style={{width:'100%', height:'100%', objectFit:'contain'}} />
                    ) : <Icons.Company style={{width:'60%', height:'60%', margin:'20%', opacity:0.5}} />}
                  </div>
                  
                  <div className="card-titles" style={{marginLeft:'75px', minHeight:'60px', display:'flex', flexDirection:'column', justifyContent:'center'}}>
                    <h3 className="card-main-title" style={{fontSize:'1.1rem', margin:0, color:'#fff', fontWeight:700}}>{c.name}</h3>
                    {c.brand_name && <p className="card-subtitle" style={{fontSize:'0.8rem', margin:'4px 0 0', color:'var(--primary)', fontWeight:600}}>{c.brand_name}</p>}
                  </div>

                  {!isExternal(c.id) && (
                    <div className="card-actions-top" style={{position:'absolute', right:'1rem', top:'1rem'}} onClick={e => e.stopPropagation()}>
                      <button className="icon-btn-danger" onClick={()=>setDeleteId(c.id)} title="O'chirish">🗑</button>
                    </div>
                  )}
                </div>

                <div className="card-body-grid">
                  <div className="info-item">
                    <span className="info-label">ID</span>
                    <span className="info-value">#{c.id.toString().replace('ext-','')}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Telefon</span>
                    <span className="info-value">{c.phone || '—'}</span>
                  </div>
                  <div className="info-item full-width">
                    <span className="info-label">Mas'ul xodim</span>
                    <div className="info-value-group">
                      <span className="info-value-main">{c.responsible_name || '—'}</span>
                      {c.responsible_phone && <span className="info-value-sub">{c.responsible_phone}</span>}
                    </div>
                  </div>
                </div>

                <div className="card-footer">
                  <div className={`status-indicator ${statusClassMap[c.status] || 'status-new'}`}>
                    <div className="pulse-dot"></div>
                    {(statusLabel[c.status]||statusLabel['Yangi']).label}
                  </div>
                </div>
              </div>
            ))
            }
          </div>
        );
      })()}
    </React.Fragment>
  )}

      {/* Slide-in Form Modal */}
      {showForm && (
        <div className="modal-overlay" style={{alignItems:'flex-start', overflowY:'auto', padding:'2rem'}}>
          <div className="glass-card" style={{width:'100%', maxWidth:700, margin:'auto', position:'relative', animation:'fadeIn 0.3s ease-out'}}>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'2rem'}}>
              <h3 style={{margin:0, fontSize:'1.2rem'}}>
                {isExternal(editingId) ? '📋 Kompaniya tafsilotlari' : (editingId ? '✏️ Kompaniyani tahrirlash' : '🏢 Yangi kompaniya qo\'shish')}
              </h3>
              <button onClick={() => setShowForm(false)} style={{background:'none', border:'none', color:'var(--text-muted)', cursor:'pointer', fontSize:'1.5rem', lineHeight:1}}>×</button>
            </div>

            {isExternal(editingId) ? (
              <div className="premium-detail-view fadeInUp">
                <div className="detail-header">
                  <div className="detail-avatar-container">
                    {form.logo_url ? <img src={form.logo_url} alt="logo" className="detail-avatar"/> : <Icons.Company className="detail-avatar-icon"/>}
                  </div>
                  <div className="detail-header-text">
                    <h2 className="detail-title">{form.name}</h2>
                    {form.brand_name && <div className="detail-brand">{form.brand_name}</div>}
                    <div className={`detail-status-badge ${statusClassMap[form.status] || 'status-active'}`}>
                       {(statusLabel[form.status]||statusLabel['Faol']).label}
                    </div>
                  </div>
                </div>

                <div className="detail-grid">
                  <div className="detail-item">
                    <div className="detail-icon"><Icons.Id /></div>
                    <div className="detail-content">
                      <div className="detail-label">Identifikator (ID)</div>
                      <div className="detail-value">{editingId.replace('ext-','')}</div>
                    </div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-icon"><Icons.Phone /></div>
                    <div className="detail-content">
                      <div className="detail-label">Kompaniya telefoni</div>
                      <div className="detail-value">{form.phone || '—'}</div>
                    </div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-icon"><Icons.User /></div>
                    <div className="detail-content">
                      <div className="detail-label">Direktor</div>
                      <div className="detail-value">{form.director || '—'}</div>
                    </div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-icon"><Icons.Settings /></div>
                    <div className="detail-content">
                      <div className="detail-label">Asosiy valyuta</div>
                      <div className="detail-value">{form.main_currency || 'UZS'}</div>
                    </div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-icon"><Icons.Company /></div>
                    <div className="detail-content">
                      <div className="detail-label">Mas'ul xodim</div>
                      <div className="detail-value">{form.responsible_name || '—'}</div>
                    </div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-icon"><Icons.Phone /></div>
                    <div className="detail-content">
                      <div className="detail-label">Xodim telefoni</div>
                      <div className="detail-value">{form.responsible_phone || '—'}</div>
                    </div>
                  </div>
                  <div className="detail-item full-width-item">
                    <div className="detail-icon"><Icons.Clock /></div>
                    <div className="detail-content">
                      <div className="detail-label">Obuna muddati (Expired Date)</div>
                      <div className="detail-value highlight">
                        {form.subscription_end ? (form.subscription_end.includes('T') ? new Date(form.subscription_end).toLocaleDateString('ru-RU', {year:'numeric', month:'long', day:'numeric'}) : form.subscription_end) : '—'}
                      </div>
                    </div>
                  </div>
                  {form.subscription_start && (
                    <div className="detail-item full-width-item">
                      <div className="detail-icon"><Icons.Clock /></div>
                      <div className="detail-content">
                        <div className="detail-label">Ro'yxatdan o'tgan sana</div>
                        <div className="detail-value">
                          {new Date(form.subscription_start).toLocaleDateString('ru-RU', {year:'numeric', month:'long', day:'numeric'})}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="detail-actions-footer">
                   <button className="premium-btn-outline" onClick={() => setShowForm(false)}>Yopish</button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
              {/* Logo upload */}
              <div className="form-group" style={{marginBottom:'1.5rem'}}>
                <label style={{display:'block', marginBottom:'0.5rem', color:'var(--text-muted)', fontSize:'0.85rem'}}>Kompaniya logosi</label>
                <div style={{display:'flex', alignItems:'center', gap:'1rem'}}>
                  <div style={{width:80, height:80, borderRadius:12, background:'rgba(255,255,255,0.06)', border:'2px dashed var(--card-border)',
                    display:'flex', alignItems:'center', justifyContent:'center', overflow:'hidden', flexShrink:0}}>
                    {logoPreview
                      ? <img src={logoPreview} alt="preview" style={{width:'100%', height:'100%', objectFit:'cover'}}/>
                      : <span style={{fontSize:'2rem', opacity:0.3}}>🖼</span>}
                  </div>
                  <div style={{flex:1}}>
                    <input type="file" accept="image/*" id="logo-upload" style={{display:'none'}} onChange={handleLogo}/>
                    <label htmlFor="logo-upload" className="btn btn-sm btn-outline" style={{cursor:'pointer', display:'inline-block', borderColor:'var(--primary)', color:'var(--primary)'}}>
                      📁 Rasm tanlash
                    </label>
                    <div style={{fontSize:'0.75rem', color:'var(--text-muted)', marginTop:'6px'}}>JPEG, PNG, WebP, GIF, SVG • Maks 5MB</div>
                    {logoFile && <div style={{fontSize:'0.75rem', color:'var(--success)', marginTop:'4px'}}>✓ {logoFile.name}</div>}
                  </div>
                </div>
              </div>

              {/* 2-column grid */}
              <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1.2rem'}}>

                <div className="form-group">
                  <label>Kompaniya nomi *</label>
                  <input style={{...inp, borderColor: errors.name ? 'var(--danger)':''}} value={form.name}
                    onChange={e => setForm({...form, name: e.target.value})} placeholder="Masalan: Tech Solutions"/>
                  {errors.name && <div style={errStyle}>{errors.name}</div>}
                </div>

                <div className="form-group">
                  <label>Brand nomi</label>
                  <input style={inp} value={form.brand_name} onChange={e => setForm({...form, brand_name: e.target.value})} placeholder="Masalan: TechSol"/>
                </div>

                <div className="form-group">
                  <label>Asosiy valyuta</label>
                  <select style={{...inp, background:'#0f172a'}} value={form.main_currency} onChange={e => setForm({...form, main_currency: e.target.value})}>
                    {['UZS','USD','EUR','RUB','KZT','GBP','CNY'].map(v => <option key={v} value={v}>{v}</option>)}
                  </select>
                </div>

                <div className="form-group">
                  <label>Qo'shimcha valyuta</label>
                  <select style={{...inp, background:'#0f172a'}} value={form.extra_currency} onChange={e => setForm({...form, extra_currency: e.target.value})}>
                    <option value="">— Yo'q —</option>
                    {['UZS','USD','EUR','RUB','KZT','GBP','CNY'].map(v => <option key={v} value={v}>{v}</option>)}
                  </select>
                </div>

                <div className="form-group">
                  <label>Direktor</label>
                  <input style={inp} value={form.director} onChange={e => setForm({...form, director: e.target.value})} placeholder="To'liq ismi"/>
                </div>

                <div className="form-group">
                  <label>Kompaniya telefoni</label>
                  <input style={{...inp, borderColor: errors.phone ? 'var(--danger)':''}} value={form.phone}
                    onChange={e => setForm({...form, phone: e.target.value})} placeholder="+998901234567"/>
                  {errors.phone && <div style={errStyle}>{errors.phone}</div>}
                </div>

                <div className="form-group">
                  <label>Mas'ul xodim</label>
                  <input style={inp} value={form.responsible_name} onChange={e => setForm({...form, responsible_name: e.target.value})} placeholder="To'liq ismi"/>
                </div>

                <div className="form-group">
                  <label>Mas'ul xodim telefoni</label>
                  <input style={{...inp, borderColor: errors.responsible_phone ? 'var(--danger)':''}} value={form.responsible_phone}
                    onChange={e => setForm({...form, responsible_phone: e.target.value})} placeholder="+998901234567"/>
                  {errors.responsible_phone && <div style={errStyle}>{errors.responsible_phone}</div>}
                </div>

                <div className="form-group">
                  <label>Statusi</label>
                  <select style={{...inp, background:'#0f172a'}} value={form.status} onChange={e => setForm({...form, status: e.target.value})}>
                    <option value="Yangi">Yangi</option>
                    <option value="Faol">Faol</option>
                    <option value="To'xtatilgan">To'xtatilgan</option>
                    <option value="Bekor qilingan">Bekor qilingan</option>
                  </select>
                </div>

                <div className="form-group" style={{display:'flex', flexDirection:'column', justifyContent:'flex-end'}}>
                  <label style={{marginBottom:'0.5rem'}}>Holat (Yoqilgan / O'chirilgan)</label>
                  <div style={{display:'flex', alignItems:'center', gap:'12px'}}>
                    <div onClick={() => setForm({...form, is_active: !form.is_active})} style={{cursor:'pointer', width:52, height:28, borderRadius:14,
                      background: form.is_active ? 'var(--primary)' : 'rgba(255,255,255,0.15)',
                      display:'flex', alignItems:'center', padding:'3px', transition:'background 0.3s'}}>
                      <div style={{width:22, height:22, borderRadius:'50%', background:'#fff',
                        transform: form.is_active ? 'translateX(24px)' : 'translateX(0)', transition:'transform 0.3s', boxShadow:'0 1px 4px rgba(0,0,0,0.4)'}}/>
                    </div>
                    <span style={{fontSize:'0.9rem', color: form.is_active ? 'var(--success)' : 'var(--text-muted)'}}>
                      {form.is_active ? 'Yoqilgan' : 'O\'chirilgan'}
                    </span>
                  </div>
                </div>

                <div className="form-group">
                  <label>Obuna boshlanishi</label>
                  <input type="datetime-local" style={inp} value={form.subscription_start}
                    onChange={e => setForm({...form, subscription_start: e.target.value})}/>
                </div>
                <div className="form-group">
                  <label>Obuna tugashi</label>
                  <input type="datetime-local" style={inp} value={form.subscription_end}
                    onChange={e => setForm({...form, subscription_end: e.target.value})}/>
                </div>

              </div>

              <div style={{display:'flex', gap:'12px', marginTop:'2rem'}}>
                <button type="button" className="btn btn-danger" style={{flex:1}} onClick={() => setShowForm(false)}>
                  Bekor qilish
                </button>
                <button type="submit" className="btn" style={{flex:1}} disabled={saving}>
                  {saving ? '⏳ Saqlanmoqda...' : '💾 Saqlash'}
                </button>
              </div>
            </form>
          )}
          </div>
        </div>
      )}
    </div>
  );
}

function CustomersManager({ token, showFlash }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [qLoading, setQLoading] = useState(false);
  const [ansText, setAnsText] = useState({});
  const [sending, setSending] = useState({});
  const [searchQuery, setSearchQuery] = useState('');

  const fetchUsers = () => {
    fetch(`${API_URL}/users/`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json())
      .then(d => { setUsers(d || []); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchUsers();
  }, [token]);

  const openQuestions = (user) => {
    setSelectedUser(user);
    setQLoading(true);
    fetch(`${API_URL}/messages/?user_id=${user.telegram_id}&is_question=true&limit=50`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json())
      .then(d => { setQuestions(d.items || []); setQLoading(false); })
      .catch(() => setQLoading(false));
  };

  const handleReply = (qId) => {
    const text = ansText[qId];
    if (!text || !text.trim()) return;
    setSending({...sending, [qId]: true});
    fetch(`${API_URL}/questions/${qId}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ text })
    })
    .then(() => {
      setSending({...sending, [qId]: false});
      setAnsText({...ansText, [qId]: ''});
      showFlash("Javob muvaffaqiyatli yuborildi");
      openQuestions(selectedUser);
      fetchUsers();
    })
    .catch(() => { setSending({...sending, [qId]: false}); showFlash("Xatolik yuz berdi", "error"); });
  };

  const filteredUsers = users.filter(u => 
    (u.full_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (u.username || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (u.telegram_id || '').toString().includes(searchQuery)
  );

  return (
    <div style={{animation: 'fadeIn 0.5s ease-out'}}>
      <div className="flex-between" style={{marginBottom:'2.5rem', alignItems:'flex-end'}}>
         <div>
            <h2 className="header-title" style={{margin:0}}>Mijozlar ro'yxati (CRM)</h2>
            <p style={{fontSize:'0.85rem', color:'var(--text-muted)', marginTop:'5px'}}>Bot foydalanuvchilari bilan muloqot va tahlil</p>
         </div>
         <div style={{display:'flex', gap:'1rem', alignItems:'center'}}>
            <div className="glass-card" style={{padding:'10px 20px', display:'flex', alignItems:'center', gap:'12px', border:'1px solid var(--primary)'}}>
               <div style={{fontSize:'1.5rem'}}>👥</div>
               <div>
                  <div style={{fontSize:'0.65rem', color:'var(--text-muted)', textTransform:'uppercase', fontWeight:700}}>Jami mijozlar</div>
                  <div style={{fontSize:'1.1rem', fontWeight:800, color:'#fff'}}>{users.length} ta</div>
               </div>
            </div>
         </div>
      </div>

      <div className="glass-card" style={{padding:'1.5rem', marginBottom:'1.5rem', display:'flex', alignItems:'center', gap:'1.5rem'}}>
         <div style={{position:'relative', flex:1}}>
            <div style={{position:'absolute', left:'15px', top:'50%', transform:'translateY(-50%)', color:'var(--text-muted)', display:'flex'}}>
               <Icons.Search />
            </div>
            <input 
               type="text" 
               placeholder="Mijoz ismi yoki username bo'yicha qidirish..." 
               style={{width:'100%', padding:'12px 12px 12px 45px', background:'rgba(255,255,255,0.03)', border:'1px solid var(--card-border)', borderRadius:'12px', color:'#fff', outline:'none'}}
               value={searchQuery}
               onChange={e => setSearchQuery(e.target.value)}
            />
         </div>
         <button className="btn btn-outline" onClick={fetchUsers} style={{borderColor:'var(--card-border)'}}>🔄 Yangilash</button>
      </div>
      
      {loading ? <div className="loader"></div> : (
        <div className="glass-card" style={{padding:0, overflow:'hidden'}}>
          <div className="table-wrapper">
            <table className="clickup-table">
              <thead>
                <tr>
                  <th style={{paddingLeft:'1.5rem', width:'60px'}}>№</th>
                  <th style={{width:'30%'}}><div style={{display:'flex', alignItems:'center', gap:8}}><Icons.User style={{width:16}}/> Mijoz</div></th>
                  <th style={{textAlign:'center'}}><div style={{display:'flex', alignItems:'center', justifyContent:'center', gap:8}}><Icons.Flag style={{width:14}}/> Til</div></th>
                  <th style={{textAlign:'center'}}><div style={{display:'flex', alignItems:'center', justifyContent:'center', gap:8}}><Icons.History style={{width:14}}/> Faollik</div></th>
                  <th style={{textAlign:'center'}}><div style={{display:'flex', alignItems:'center', justifyContent:'center', gap:8}}><Icons.MessageCircle style={{width:14}}/> Savollar</div></th>
                  <th style={{textAlign:'center'}}><div style={{display:'flex', alignItems:'center', justifyContent:'center', gap:8}}><Icons.Calendar style={{width:14}}/> Ro'yxatdan o'tgan</div></th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.length > 0 ? filteredUsers.map((u, i) => (
                  <tr key={u.id} className="clickup-row" onClick={() => openQuestions(u)}>
                    <td style={{paddingLeft:'1.5rem', color:'var(--text-muted)', fontSize:'0.8rem'}}>{i + 1}</td>
                    <td>
                      <div style={{display:'flex', alignItems:'center', gap:'15px'}}>
                        <div className="user-avatar" style={{
                          background: getAvatarColor(u.full_name || 'U'),
                          width:'38px', height:'38px', fontSize:'0.9rem', borderRadius:'10px'
                        }}>
                          {getInitials(u.full_name || 'U')}
                        </div>
                        <div>
                          <div style={{fontWeight:'700', fontSize:'0.95rem', color:'#fff'}}>{u.full_name || 'Nomalum'}</div>
                          <div style={{fontSize:'0.75rem', color:'var(--text-muted)'}}>{u.username ? `@${u.username}` : `ID: ${u.telegram_id}`}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{textAlign:'center'}}>
                       <span style={{textTransform:'uppercase', fontSize:'0.7rem', fontWeight:'800', padding:'4px 10px', background:'rgba(255,255,255,0.05)', borderRadius:'6px', border:'1px solid rgba(255,255,255,0.1)'}}>
                          {u.language_code || 'uz'}
                       </span>
                    </td>
                    <td style={{textAlign:'center'}}>
                      <div style={{fontSize:'0.85rem', fontWeight:'600', color:'var(--primary)'}}>{u.total_messages} ta xabar</div>
                    </td>
                    <td style={{textAlign:'center'}}>
                      <div className={`status-badge ${u.total_questions > 0 ? 'status-new' : 'status-stopped'}`} 
                            style={{fontSize:'0.7rem', cursor:'pointer', padding:'6px 12px', minWidth:'90px'}}
                            onClick={(e) => { e.stopPropagation(); openQuestions(u); }}>
                        {u.total_questions} ta savol
                      </div>
                    </td>
                    <td style={{textAlign:'center'}}>
                       <div style={{fontSize:'0.85rem', color:'#fff', fontWeight:600}}>
                          {new Date(u.created_at).toLocaleDateString('uz-UZ')}
                       </div>
                       <div style={{fontSize:'0.7rem', color:'var(--text-muted)', marginTop:'2px'}}>
                          {new Date(u.created_at).toLocaleTimeString('uz-UZ', {hour:'2-digit', minute:'2-digit'})}
                       </div>
                    </td>
                  </tr>
                )) : <tr><td colSpan="6" style={{textAlign:'center', padding:'5rem', color:'var(--text-muted)'}}>
                    <div style={{fontSize:'3rem', opacity:0.1, marginBottom:'1rem'}}><Icons.Users /></div>
                    Hech qanday mijoz topilmadi.
                  </td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {selectedUser && (
        <div className="modal-overlay" style={{zIndex: 1000}}>
          <div className="glass-card" style={{width:'90%', maxWidth:'800px', maxHeight:'90vh', overflow:'hidden', display:'flex', flexDirection:'column', padding:0}}>
            <div style={{padding:'1.5rem', borderBottom:'1px solid var(--card-border)', display:'flex', justifyContent:'space-between', alignItems:'center', background:'rgba(255,255,255,0.03)'}}>
               <div style={{display:'flex', alignItems:'center', gap:'12px'}}>
                  <div className="user-avatar" style={{background:getAvatarColor(selectedUser.full_name||'U'), width:32, height:32, fontSize:'0.8rem'}}>
                    {getInitials(selectedUser.full_name||'U')}
                  </div>
                  <h3 style={{margin:0, fontSize:'1.1rem'}}>{selectedUser.full_name} savollari</h3>
               </div>
               <button className="icon-btn" onClick={() => setSelectedUser(null)}>✕</button>
            </div>

            <div style={{padding:'1.5rem', overflowY:'auto', flex:1, minHeight:'300px'}}>
               {qLoading ? (
                 <div style={{display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', height:'100%', gap:'15px', padding:'4rem 0'}}>
                    <div className="loader"></div>
                    <div style={{color:'var(--text-muted)', fontSize:'0.9rem'}}>Savollar yuklanmoqda...</div>
                 </div>
               ) : (
                 <div style={{display:'flex', flexDirection:'column', gap:'1.5rem'}}>
                    {!questions || questions.length === 0 ? (
                      <div style={{textAlign:'center', padding:'4rem 0', color:'var(--text-muted)'}}>
                         <div style={{fontSize:'3rem', marginBottom:'1rem', opacity:0.3}}><Icons.History /></div>
                         <p>Ushbu foydalanuvchida hali savollar mavjud emas.</p>
                      </div>
                    ) : questions.map(q => (
                      <div key={q.id} style={{background:'rgba(255,255,255,0.02)', borderRadius:'12px', padding:'1.25rem', border:'1px solid var(--card-border)'}}>
                         <div style={{display:'flex', justifyContent:'space-between', marginBottom:'0.75rem'}}>
                            <span style={{fontSize:'0.75rem', color:'var(--text-muted)'}}>{new Date(q.created_at).toLocaleString('uz-UZ')}</span>
                            <span className={`badge ${q.is_answered ? 'badge-kb' : 'badge-unanswered'}`} style={{fontSize:'0.65rem'}}>
                               {q.is_answered ? 'Javob berilgan' : 'Javob kutilmoqda'}
                            </span>
                         </div>
                         <p style={{margin:0, fontSize:'0.95rem', lineHeight:'1.5'}}>{q.text}</p>
                         
                         {q.is_answered ? (
                            <div style={{marginTop:'1rem', padding:'1rem', background:'rgba(16, 185, 129, 0.05)', borderRadius:'10px', borderLeft:'3px solid var(--success)'}}>
                               <div style={{fontSize:'0.7rem', color:'var(--success)', marginBottom:'4px', fontWeight:'600'}}>BIZNING JAVOB:</div>
                               <p style={{margin:0, fontSize:'0.9rem', color:'rgba(255,255,255,0.8)'}}>{q.answer_text || 'AI tomonidan javob berilgan'}</p>
                            </div>
                         ) : (
                            <div style={{marginTop:'1.25rem'}}>
                               <textarea 
                                  placeholder="Javobingizni yozing..." 
                                  style={{width:'100%', padding:'12px', borderRadius:'10px', background:'rgba(0,0,0,0.2)', border:'1px solid var(--card-border)', color:'#fff', fontSize:'0.9rem'}}
                                  value={ansText[q.id] || ''}
                                  onChange={e => setAnsText({...ansText, [q.id]: e.target.value})}
                               />
                               <div style={{display:'flex', justifyContent:'flex-end', marginTop:'10px'}}>
                                  <button className="btn btn-sm" onClick={() => handleReply(q.id)} disabled={sending[q.id] || !ansText[q.id]?.trim()}>
                                     {sending[q.id] ? 'Yuborilmoqda...' : 'Javobni yuborish'}
                                  </button>
                               </div>
                            </div>
                         )}
                      </div>
                    ))}
                 </div>
               )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Dashboard({ token, showFlash }) {
  const [stats, setStats] = useState({ 
    total_groups: 0, total_questions: 0, answered_questions: 0, unanswered_questions: 0, bot_answers: 0, total_messages: 0,
    latest_unanswered: [], most_active_group: null, most_active_user: null, 
    trending_topics: [], daily_activity: [], total_users: 0, top_groups: [], ai_usage: []
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
       showFlash("Javob yuborildi");
       fetchStats();
    })
    .catch(() => { setSending(false); showFlash("Xatolik yuz berdi", "error"); });
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
                        <div style={{fontSize:'0.9rem', lineHeight:1.4, cursor:'pointer', position:'relative'}} 
                             onClick={() => {setAnsweringId(q.id); setAnswerText('');}}>
                          {q.telegram_app_link ? (
                            <a href={q.telegram_app_link} className="tg-link" onClick={e => e.stopPropagation()} title="Telegramda ko'rish">{q.text}</a>
                          ) : q.text}
                        </div>
                        <div style={{fontSize:'0.7rem', color:'var(--text-muted)', marginTop:'5px'}}>
                           {q.telegram_app_link ? (
                             <a href={q.telegram_app_link} className="tg-link" onClick={e => e.stopPropagation()} style={{color:'inherit'}} title="Telegramda ko'rish">
                               {q.full_name} • {q.group_title} • {formatDate(q.created_at)}
                             </a>
                           ) : (
                             <>{q.full_name} • {q.group_title} • {formatDate(q.created_at)}</>
                           )}
                        </div>
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
                   <div style={{fontSize:'1.3rem', marginTop:'0.5rem', fontWeight:'700'}}>{g.messages} <small style={{fontSize:'0.7rem', color:'var(--text-muted)', fontWeight:'normal'}}>xabar</small></div>
                </div>
             ))}
         </div>
      </div>

      <div className="glass-card" style={{marginTop:'2rem'}}>
         <div className="summary-title" style={{marginBottom:'1.5rem'}}>AI Provayderlar Sarfi (Umumiy)</div>
         <div className="grid-cards" style={{gridTemplateColumns:'repeat(auto-fit, minmax(240px, 1fr))', gap:'1.5rem'}}>
             {stats.ai_usage && stats.ai_usage.length > 0 ? stats.ai_usage.map((ai, i) => (
                <div key={i} className="glass-card" style={{margin:0, padding:'1.5rem', borderLeft:'4px solid var(--primary)', position:'relative', overflow:'hidden'}}>
                   <div style={{position:'absolute', top:'-10px', right:'-10px', opacity:0.1}}><Icons.Bot /></div>
                   <div style={{fontSize:'1.1rem', fontWeight:700, textTransform:'uppercase', color:'var(--primary)', marginBottom:'0.2rem'}}>{ai.provider}</div>
                   {ai.groups && ai.groups.length > 0 && (
                      <div style={{fontSize:'0.75rem', color:'var(--text-muted)', marginBottom:'0.8rem', display:'flex', flexWrap:'wrap', gap:'5px'}}>
                         {ai.groups.map((g, idx) => (
                            <span key={idx} style={{background: 'rgba(255,255,255,0.05)', padding: '2px 6px', borderRadius: '4px'}}>
                               {g.title}
                            </span>
                         ))}
                      </div>
                   )}
                   
                   <div style={{fontSize:'1.8rem', fontWeight:800}}>{ai.tokens.toLocaleString()} <span style={{fontSize:'0.8rem', color:'var(--text-muted)'}}>token</span></div>
                   <div style={{marginTop:'10px', fontSize:'0.85rem', color:'var(--text-muted)'}}>
                      <div className="flex-between"><span>Jami so'rovlar:</span> <b>{ai.requests} ta</b></div>
                   </div>
                </div>
             )) : (
                <div style={{gridColumn:'1/-1', textAlign:'center', padding:'2rem', color:'var(--text-muted)'}}>
                   AI sarfi haqida ma'lumotlar mavjud emas.
                </div>
             )}
         </div>
      </div>
    </div>
  );
}

function KnowledgeBase({ token, showFlash, askConfirm }) {
  const [kb, setKb] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [form, setForm] = useState({ question: '', answer: '' });
  const [extractedData, setExtractedData] = useState(null);
  const [editingItem, setEditingItem] = useState(null);

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
    .then(() => { setSaving(false); setExtractedData(null); showFlash('Bilimlar saqlandi'); fetchKb(); })
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
    const url = editingItem ? `${API_URL}/knowledge/${editingItem.id}` : `${API_URL}/knowledge/`;
    const method = editingItem ? 'PUT' : 'POST';

    fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(form)
    }).then(() => { 
      setForm({ question: '', answer: '' }); 
      setEditingItem(null);
      setSaving(false); 
      showFlash(editingItem ? 'Ma\'lumot yangilandi' : 'Ma\'lumot saqlandi');
      fetchKb(); 
    }).catch(() => { setSaving(false); showFlash('Xato', 'error'); });
  };

  const startEdit = (item) => {
    setEditingItem(item);
    setForm({ question: item.question, answer: item.answer });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <>
      <h2 className="header-title">AI Bilimlar bazasi</h2>
      <div className="grid-cards" style={{gridTemplateColumns:'1fr 1fr', gap:'2rem', alignItems:'start'}}>
         <div className="glass-card">
            <div className="summary-title" style={{marginBottom:'1rem'}}>
              {editingItem ? 'Bilimni tahrirlash' : 'Qo\'lda bilim qo\'shish'}
            </div>
            <form onSubmit={handleSubmit}>
               <div className="form-group"><label>Savol yoki kalit so'z</label><input type="text" value={form.question} onChange={e => setForm({...form, question: e.target.value})} required /></div>
               <div className="form-group"><label>Javob matni</label><textarea value={form.answer} onChange={e => setForm({...form, answer: e.target.value})} required /></div>
               <div className="flex-between" style={{gap:'10px'}}>
                  <button type="submit" className="btn" disabled={saving} style={{flex:1}}>
                    {saving ? 'Saqlanmoqda...' : (editingItem ? 'Yangilash' : 'Saqlash')}
                  </button>
                  {editingItem && (
                    <button type="button" className="btn btn-danger" onClick={() => { setEditingItem(null); setForm({question:'', answer:''}); }} style={{flex:1}}>
                      Bekor qilish
                    </button>
                  )}
               </div>
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
                   <thead><tr><th style={{width:'40px', textAlign:'center', color:'var(--primary)'}}>№</th><th style={{width:'40%'}}>Savol / Mavzu</th><th>AI tayyorlagan javob</th><th style={{width:'50px'}}></th></tr></thead>
                   <tbody>
                      {extractedData.map((d, i) => (
                         <tr key={i}>
                             <td style={{textAlign:'center', verticalAlign:'middle', padding:'8px', fontWeight:'700', fontSize:'1.1rem', color:'var(--primary)', minWidth:'40px'}}>{i + 1}</td>
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
        <table><thead><tr><th>Savol</th><th>Bilim matni</th><th style={{textAlign:'center'}}>Amallar</th></tr></thead>
        <tbody>{kb.map(item => (
          <tr key={item.id}>
            <td>{item.question}</td>
            <td style={{fontSize:'0.85rem', color:'var(--text-muted)', maxWidth:'400px'}}>{item.answer}</td>
            <td style={{textAlign:'center'}}>
              <div style={{display:'flex', gap:'10px', justifyContent:'center', flexWrap:'wrap'}}>
                <button className="btn btn-sm" onClick={() => startEdit(item)} style={{padding:'5px 12px'}}>Tahrirlash</button>
                <button className="btn btn-sm btn-danger" onClick={() => deleteKb(item.id)} style={{padding:'5px 12px'}}>O'chirish</button>
              </div>
            </td>
          </tr>
        ))}</tbody></table>
        {kb.length === 0 && !loading && <p style={{textAlign:'center', padding:'2rem', color:'var(--text-muted)'}}>Hali ma'lumotlar qo'shilmagan.</p>}
      </div>
    </>
  );
}

function Messages({ token, showFlash }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  
  const [answeringId, setAnsweringId] = useState(null);
  const [answerText, setAnswerText] = useState('');
  const [sending, setSending] = useState(false);

  const fetchMessages = () => {
    setLoading(true);
    fetch(`${API_URL}/questions/?limit=15&offset=${page * 15}`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(data => { setMessages(data.items || []); setTotal(data.total || 0); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchMessages();
  }, [token, page]);

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
       showFlash("Xabar/Javob yuborildi");
       fetchMessages();
    })
    .catch(() => { setSending(false); showFlash("Xatolik yuz berdi", "error"); });
  };

  if (loading) return <div className="loader"></div>;

  return (
    <div style={{animation:'fadeIn 0.5s ease-out'}}>
      <div className="flex-between" style={{marginBottom:'2rem'}}>
         <div>
            <h2 className="header-title" style={{margin:0}}>Muloqotlar jurnali</h2>
            <p style={{fontSize:'0.85rem', color:'var(--text-muted)', marginTop:'5px'}}>Foydalanuvchilar bilan barcha muloqotlar tarixi</p>
         </div>
         <a href={`${API_URL}/export/messages`} className="btn btn-sm btn-outline" style={{padding:'10px 24px', borderRadius:'12px', borderColor:'rgba(255,255,255,0.1)', background:'rgba(255,255,255,0.03)', color:'#fff'}}>
            📥 Excel yuklab olish
         </a>
      </div>

      <div style={{display:'flex', flexDirection:'column', gap:'1.5rem'}}>
        {[
          { id: 'unanswered', title: 'Kutilmoqda', color: '#ef4444', items: messages.filter(m => !m.is_answered) },
          { id: 'answered', title: 'Javob berilgan', color: '#10b981', items: messages.filter(m => m.is_answered) }
        ].map(group => group.items.length > 0 && (
          <div key={group.id} className="glass-card" style={{padding:0, overflow:'hidden', border:'1px solid var(--card-border)'}}>
            <div 
              className="list-group-header" 
              style={{padding:'1rem 1.5rem', background:'rgba(255,255,255,0.02)', borderBottom:'1px solid var(--card-border)', display:'flex', alignItems:'center', gap:'1rem'}}
            >
              <Icons.ChevronDown style={{color:'var(--text-muted)'}} />
              <div style={{fontWeight:700, fontSize:'1rem', color:'#fff', flex:1}}>
                {group.title}
                <span style={{marginLeft:'10px', fontSize:'0.8rem', color:'var(--text-muted)', fontWeight:400}}>({group.items.length} xabar)</span>
              </div>
              <div style={{width:8, height:8, borderRadius:'50%', background:group.color, boxShadow:`0 0 10px ${group.color}`}}></div>
            </div>

            <div className="table-wrapper">
              <table className="clickup-table">
                <thead>
                  <tr>
                    <th className="clickup-column-header" style={{width:'45%', paddingLeft:'1.5rem'}}>Xabar va Mazmuni</th>
                    <th className="clickup-column-header">Kimdan / Assignee</th>
                    <th className="clickup-column-header">Vaqt / Guruh</th>
                    <th className="clickup-column-header" style={{textAlign:'center'}}>Priority</th>
                  </tr>
                </thead>
                <tbody>
                  {group.items.map(msg => (
                    <tr key={msg.id} className="clickup-row" style={{verticalAlign:'top'}}>
                      <td style={{paddingLeft:'1.5rem', paddingBottom:'1.5rem'}}>
                        <div style={{display:'flex', flexDirection:'column', gap:'10px'}}>
                          {/* SAVOL BLOKI */}
                          <div style={{display:'flex', flexDirection:'column', gap:'4px'}}>
                            <div 
                              style={{
                                background: 'rgba(255,255,255,0.04)',
                                padding: '12px 16px',
                                borderRadius: '14px 14px 14px 4px',
                                fontSize: '0.92rem',
                                lineHeight: '1.6',
                                color: '#f8fafc',
                                border: '1px solid rgba(255,255,255,0.06)',
                                cursor: msg.is_answered ? 'default' : 'pointer',
                                position: 'relative',
                                transition: 'all 0.3s ease'
                              }}
                              onClick={() => { if(!msg.is_answered) { setAnsweringId(msg.id); setAnswerText(''); } }}
                            >
                              {msg.text}
                              <div style={{textAlign:'right', marginTop:'6px', fontSize:'0.65rem', color:'rgba(255,255,255,0.4)', fontWeight:600}}>
                                SAVOL • {formatDate(msg.created_at)}
                              </div>
                            </div>
                          </div>
                          
                          {/* JAVOB BERISH FORMASI */}
                          {answeringId === msg.id && (
                            <div style={{marginTop:'4px', animation:'fadeIn 0.3s ease', paddingLeft:'1.5rem'}}>
                              <textarea 
                                rows="3" 
                                value={answerText} 
                                onChange={e => setAnswerText(e.target.value)}
                                placeholder="Javobingizni yozing..."
                                style={{
                                  width:'100%', 
                                  background:'rgba(99, 102, 241, 0.08)', 
                                  border:'2px solid var(--primary)', 
                                  color:'#fff', 
                                  borderRadius:'14px',
                                  padding:'12px',
                                  fontSize:'0.9rem',
                                  outline:'none',
                                  boxShadow: '0 0 15px rgba(99, 102, 241, 0.2)'
                                }}
                                autoFocus
                              />
                              <div style={{display:'flex', gap:'8px', marginTop:'10px', justifyContent:'flex-end'}}>
                                <button className="btn btn-sm btn-danger" onClick={() => setAnsweringId(null)} style={{fontSize:'0.75rem', padding:'8px 18px', borderRadius:'10px'}}>Bekor qilish</button>
                                <button className="btn btn-sm" onClick={(e) => handleSendAnswer(e, msg.id)} disabled={sending} style={{fontSize:'0.75rem', padding:'8px 24px', borderRadius:'10px', background:'var(--primary)'}}>
                                  {sending ? '⏳...' : 'Yuborish'}
                                </button>
                              </div>
                            </div>
                          )}

                          {/* JAVOB BLOKI */}
                          {msg.is_answered && (
                            <div style={{
                              marginLeft: '2rem',
                              padding:'12px 16px', 
                              background:'linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(16, 185, 129, 0.05))', 
                              borderRadius:'14px 14px 4px 14px', 
                              border:'1px solid rgba(16, 185, 129, 0.25)',
                              fontSize:'0.9rem',
                              position: 'relative'
                            }}>
                               <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'8px'}}>
                                  <span style={{
                                    color:'#10b981', 
                                    fontWeight:'900', 
                                    fontSize:'0.6rem', 
                                    textTransform:'uppercase',
                                    letterSpacing: '1px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '5px'
                                  }}>
                                    {msg.answered_by === 'Bot' ? '🤖 AI BOT' : `👤 ${msg.answered_by || 'ADMIN'}`} JAVOBI
                                  </span>
                                  <span style={{fontSize:'0.65rem', color:'rgba(16, 185, 129, 0.7)', fontWeight:600}}>
                                    {formatDate(msg.answered_at)}
                                  </span>
                               </div>
                               <div style={{color:'rgba(255,255,255,0.95)', lineHeight: '1.5'}}>{msg.answer_text || "Javob xabari saqlanmagan"}</div>
                            </div>
                          )}
                        </div>
                      </td>
                      <td style={{paddingTop:'1.5rem'}}>
                        <div style={{display:'flex', alignItems:'center', gap:'12px'}}>
                          {/* Standart User Ikonkasi */}
                          <div style={{
                            width: 36, 
                            height: 36, 
                            borderRadius: '12px', 
                            background: 'rgba(255,255,255,0.05)', 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center',
                            color: 'var(--primary)',
                            border: '1px solid rgba(255,255,255,0.1)'
                          }}>
                            <Icons.User />
                          </div>
                          <div>
                            <div style={{fontSize:'0.95rem', fontWeight:'800', color:'#fff'}}>{msg.full_name || 'Foydalanuvchi'}</div>
                            <div style={{fontSize:'0.75rem', color:'var(--text-muted)'}}>@{msg.username || 'id' + msg.user_id}</div>
                          </div>
                        </div>
                      </td>
                      <td style={{paddingTop:'1.5rem'}}>
                        <div style={{display:'flex', flexDirection:'column', gap:'8px'}}>
                           {/* Guruh nomi */}
                           <div style={{
                             display:'inline-flex', 
                             padding:'4px 10px', 
                             background:'rgba(99,102,241,0.15)', 
                             borderRadius:'8px', 
                             color:'var(--primary)', 
                             fontSize:'0.75rem', 
                             width:'fit-content', 
                             fontWeight:800,
                             border: '1px solid rgba(99,102,241,0.3)'
                           }}>
                              {msg.group_title || 'Shaxsiy'}
                           </div>

                           {/* Savol vaqti */}
                           <div style={{fontSize:'0.75rem', color:'var(--text-muted)', display:'flex', alignItems:'center', gap:'6px', paddingLeft:'2px', marginTop:'4px'}}>
                              <span style={{color:'rgba(255,255,255,0.3)', fontWeight:700, fontSize:'0.65rem'}}>SAVOL:</span>
                              <span>{formatDate(msg.created_at)}</span>
                           </div>

                           {/* Javob vaqti (agar bo'lsa) */}
                           {msg.is_answered && (
                             <div style={{fontSize:'0.75rem', color:'#10b981', display:'flex', alignItems:'center', gap:'6px', paddingLeft:'2px'}}>
                                <span style={{color:'rgba(16, 185, 129, 0.4)', fontWeight:700, fontSize:'0.65rem'}}>JAVOB:</span>
                                <span>{formatDate(msg.answered_at)}</span>
                             </div>
                           )}
                           
                           <div style={{fontSize:'0.65rem', color:'rgba(255,255,255,0.2)', marginTop:'2px', paddingLeft:'2px'}}>
                              ID: {msg.telegram_message_id}
                           </div>
                        </div>
                      </td>
                      <td style={{textAlign:'center', paddingTop:'1.5rem'}}>
                        <div title={msg.is_answered ? 'Javob berilgan' : 'Kutilmoqda'}>
                          <div style={{
                            width: '32px',
                            height: '32px',
                            borderRadius: '10px',
                            background: msg.is_answered ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto',
                            border: `1px solid ${msg.is_answered ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`
                          }}>
                            <Icons.Flag className={`priority-flag priority-${msg.is_answered ? 'normal' : 'urgent'}`} style={{width:16}} />
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>

      <div className="flex-between" style={{marginTop:'2rem', padding:'1rem 1.5rem', background:'rgba(255,255,255,0.02)', borderRadius:'16px', border:'1px solid var(--card-border)'}}>
        <div style={{display:'flex', gap:'12px'}}>
          <button className="btn btn-sm btn-outline" disabled={page === 0} onClick={() => setPage(p => p - 1)} style={{padding:'8px 24px', borderRadius:'10px'}}>
            <Icons.ChevronDown style={{transform:'rotate(90deg)', width:16}} /> Orqaga
          </button>
          <button className="btn btn-sm btn-outline" disabled={(page + 1) * 15 >= total} onClick={() => setPage(p => p + 1)} style={{padding:'8px 24px', borderRadius:'10px'}}>
            Oldinga <Icons.ChevronDown style={{transform:'rotate(-90deg)', width:16}} />
          </button>
        </div>
        <div style={{fontSize:'0.85rem', fontWeight:'600', color:'var(--text-muted)'}}>
           Sahifa: <span style={{color:'#fff'}}>{page + 1}</span> / {Math.ceil(total / 15) || 1} 
           <span style={{marginLeft:'15px', paddingLeft:'15px', borderLeft:'1px solid rgba(255,255,255,0.1)'}}>Jami: {total} ta xabar</span>
        </div>
      </div>
    </div>
  );
}

function Groups({ token, showFlash, askConfirm }) {
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchGroups = () => {
    setLoading(true);
    fetch(`${API_URL}/groups/`, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => res.json()).then(data => { setGroups(data); setLoading(false); })
      .catch(() => setLoading(false));
  };

  const handleDeleteGroup = (id, title) => {
    askConfirm(
      'Guruhni o\'chirish', 
      `Haqiqatan ham "${title}" guruhini va uning barcha xabarlarini o'chirib tashlamoqchimisiz?`, 
      () => {
        fetch(`${API_URL}/groups/${id}`, { 
          method: 'DELETE', 
          headers: { 'Authorization': `Bearer ${token}` } 
        })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            showFlash('Guruh o\'chirildi', 'error');
            fetchGroups();
          } else {
            showFlash('Xatolik yuz berdi', 'error');
          }
        })
        .catch(() => showFlash('Xatolik yuz berdi', 'error'));
      }
    );
  };
  useEffect(() => { if(!selectedGroup) fetchGroups(); }, [token, selectedGroup]);

  if (loading) return <div className="loader"></div>;
  if (selectedGroup) return <GroupHistory token={token} group={selectedGroup} onBack={() => setSelectedGroup(null)} showFlash={showFlash} />;

  return (
    <>
      <h2 className="header-title">Guruhlar ro'yxati</h2>
      <div className="glass-card" style={{padding:'1.5rem'}}>
        <div className="table-wrapper">
          <table className="premium-table">
            <thead>
              <tr>
                <th style={{padding:'20px'}}>Guruh nomi</th>
                <th style={{textAlign:'center'}}>Xabarlar</th>
                <th style={{textAlign:'center'}}>So'rovlar</th>
                <th style={{textAlign:'center'}}>Tokenlar</th>
                <th style={{textAlign:'center'}}>Sarf ($)</th>
                <th style={{textAlign:'center'}}>Kutilmoqda</th>
                <th style={{textAlign:'center'}}>Amallar</th>
              </tr>
            </thead>
            <tbody>
              {groups.map(g => (
                <tr key={g.id} className="clickable-row" onClick={() => setSelectedGroup(g)} style={{height:'80px'}}>
                  <td style={{padding:'20px'}}>
                    <div style={{display:'flex', alignItems:'center', gap:'15px'}}>
                      <div className="user-avatar" style={{background: 'rgba(99, 102, 241, 0.1)', color:'var(--primary)', width:'40px', height:'40px', fontSize:'0.9rem'}}>
                        <Icons.Groups style={{width:20}}/>
                      </div>
                      <div style={{fontWeight:'700', fontSize:'1rem', color:'#fff'}}>{g.title}</div>
                    </div>
                  </td>
                  <td style={{textAlign:'center', fontWeight:'600'}}>{g.total_messages}</td>
                  <td style={{textAlign:'center', fontWeight:'600'}}>{g.total_questions}</td>
                  <td style={{textAlign:'center', color:'var(--text-muted)', fontSize:'0.9rem'}}>{g.total_tokens?.toLocaleString()}</td>
                  <td style={{textAlign:'center'}}>
                    <div style={{color:'var(--success)', fontWeight:'800', fontSize:'1.1rem'}}>
                      ${g.total_ai_cost?.toFixed(4)}
                    </div>
                  </td>
                  <td style={{textAlign:'center'}}>
                    <span className={`badge ${g.unanswered_questions > 0 ? 'badge-unanswered' : 'badge-kb'}`} 
                          style={{
                            fontSize:'0.85rem', 
                            padding:'6px 14px', 
                            boxShadow: g.unanswered_questions > 0 ? '0 0 15px rgba(239, 68, 68, 0.2)' : 'none'
                          }}>
                      {g.unanswered_questions}
                    </span>
                  </td>
                  <td style={{textAlign:'center'}}>
                    <button 
                      className="btn btn-sm btn-danger" 
                      onClick={(e) => { e.stopPropagation(); handleDeleteGroup(g.id, g.title); }}
                      style={{padding:'10px', borderRadius:'12px'}}
                      title="Guruhni o'chirish"
                    >
                      🗑
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

function GroupHistory({ token, group, onBack, showFlash }) {
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
      .catch((err) => { 
        console.error("Group History Fetch Error:", err);
        setLoading(false); 
      }); 
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
       showFlash("Xabar/Javob yuborildi");
       fetchMessages();
    })
    .catch(() => { setSending(false); showFlash("Xatolik yuz berdi", "error"); });
  };

  return (<>
    <div className="flex-between" style={{marginBottom:'2.5rem'}}>
       <div>
          <h2 className="header-title" style={{margin:0}}>{group.title}</h2>
          <p style={{fontSize:'0.85rem', color:'var(--text-muted)', marginTop:'5px'}}>Guruh xabarlar tarixi va savollar</p>
       </div>
       <button className="btn btn-sm btn-outline" onClick={onBack} style={{padding:'10px 24px'}}>
          ⬅️ Orqaga qaytish
       </button>
    </div>
    
    {loading && msgs.length === 0 ? <div className="loader"></div> : (
      <div className="glass-card" style={{padding:'1.5rem'}}>
        <div className="table-wrapper">
          <table className="premium-table">
            <thead>
              <tr style={{background:'rgba(255,255,255,0.02)'}}>
                <th style={{padding:'20px', width:'120px', color:'var(--text-muted)', fontSize:'0.75rem', textTransform:'uppercase', letterSpacing:'1px'}}>
                   <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
                      <Icons.Calendar style={{width:14, opacity:0.6}}/> Vaqti
                   </div>
                </th>
                <th style={{padding:'20px', color:'var(--text-muted)', fontSize:'0.75rem', textTransform:'uppercase', letterSpacing:'1px'}}>
                   <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
                      <Icons.Users style={{width:14, opacity:0.6}}/> Kimdan
                   </div>
                </th>
                <th style={{padding:'20px', width:'35%', color:'var(--text-muted)', fontSize:'0.75rem', textTransform:'uppercase', letterSpacing:'1px'}}>
                   <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
                      <Icons.MessageCircle style={{width:14, opacity:0.6}}/> Xabar (Savol)
                   </div>
                </th>
                <th style={{padding:'20px', color:'var(--text-muted)', fontSize:'0.75rem', textTransform:'uppercase', letterSpacing:'1px'}}>
                   <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
                      <Icons.Training style={{width:14, opacity:0.6}}/> Javob
                   </div>
                </th>
                <th style={{padding:'20px', textAlign:'center', color:'var(--text-muted)', fontSize:'0.75rem', textTransform:'uppercase', letterSpacing:'1px'}}>
                   <div style={{display:'flex', alignItems:'center', justifyContent:'center', gap:'8px'}}>
                      <Icons.History style={{width:14, opacity:0.6}}/> Holati
                   </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {msgs.length > 0 ? msgs.map(m => {
                const isStaffMsg = m.is_staff || (m.full_name && m.full_name.includes('Admin'));
                
                return (
                  <tr key={m.id} style={{height: '140px', verticalAlign:'top', borderBottom:'1px solid rgba(255,255,255,0.05)'}}>
                    <td style={{padding:'25px 20px', fontSize:'0.8rem', color:'var(--text-muted)', fontWeight:'500'}}>
                        <div style={{display:'flex', flexDirection:'column', gap:'10px'}}>
                           <div style={{display:'flex', alignItems:'center', gap:'8px', background:'rgba(255,255,255,0.03)', padding:'4px 8px', borderRadius:'6px', width:'fit-content'}}>
                              <Icons.Calendar style={{width:12, color:'var(--primary)', opacity:0.7}}/>
                              <span>{formatDate(m.created_at)}</span>
                           </div>
                           {m.is_answered && m.answered_at && (
                             <div style={{display:'flex', alignItems:'center', gap:'8px', background:'rgba(16, 185, 129, 0.05)', padding:'4px 8px', borderRadius:'6px', width:'fit-content', color:'#10b981'}}>
                                <Icons.Training style={{width:12}}/>
                                <span>{formatDate(m.answered_at)}</span>
                             </div>
                           )}
                        </div>
                    </td>
                    <td style={{padding:'25px 10px'}}>
                        <div style={{display:'flex', alignItems:'center', gap:'15px'}}>
                           <div style={{position:'relative'}}>
                              <div className="user-avatar" style={{
                                background: isStaffMsg ? 'linear-gradient(135deg, var(--primary), #4f46e5)' : getAvatarColor(m.full_name || 'U'), 
                                width:'45px', height:'45px', fontSize:'1rem', borderRadius:'14px',
                                boxShadow: isStaffMsg ? '0 0 20px rgba(99, 102, 241, 0.3)' : '0 4px 10px rgba(0,0,0,0.2)',
                                border: isStaffMsg ? '2px solid rgba(255,255,255,0.2)' : '1px solid rgba(255,255,255,0.1)',
                                transition: 'transform 0.3s ease'
                              }}>
                                {isStaffMsg ? <Icons.Bot style={{width:22, color:'#fff'}}/> : getInitials(m.full_name || 'U')}
                              </div>
                              {isStaffMsg && (
                                <div style={{
                                  position:'absolute', bottom:'-5px', right:'-5px', 
                                  background:'#10b981', borderRadius:'50%', width:'18px', height:'18px',
                                  display:'flex', alignItems:'center', justifyContent:'center',
                                  border:'2px solid #1a1c2e', boxShadow:'0 2px 5px rgba(0,0,0,0.3)'
                                }}>
                                   <Icons.CheckCircle style={{width:10, color:'#fff'}}/>
                                </div>
                              )}
                           </div>
                           <div>
                             <div style={{display:'flex', alignItems:'center', gap:'6px'}}>
                               <div style={{fontWeight:'700', fontSize:'1rem', color: isStaffMsg ? 'var(--primary)' : '#fff'}}>
                                 {m.full_name}
                               </div>
                               {isStaffMsg && <Icons.Training style={{width:14, color:'var(--primary)'}} title="Tasdiqlangan xodim"/>}
                             </div>
                             {m.username && <div style={{fontSize:'0.75rem', color:'var(--text-muted)', display:'flex', alignItems:'center', gap:'4px'}}>
                                <span style={{opacity:0.5}}>@</span>{m.username}
                             </div>}
                             {isStaffMsg && (
                               <div style={{
                                 marginTop:'4px',
                                 display:'inline-flex',
                                 alignItems:'center',
                                 gap:'4px',
                                 fontSize:'0.6rem',
                                 color:'var(--primary)',
                                 fontWeight:800,
                                 textTransform:'uppercase',
                                 letterSpacing:'1px',
                                 background: 'rgba(99, 102, 241, 0.1)',
                                 padding: '2px 8px',
                                 borderRadius: '4px'
                               }}>
                                  <Icons.Training style={{width:10}}/> Xodim
                               </div>
                             )}
                           </div>
                        </div>
                    </td>
                    <td style={{padding:'25px 10px'}} colSpan={m.is_answered ? 2 : 1}>
                      <div style={{display:'flex', flexDirection:'column', gap:'12px', maxWidth:'100%'}}>
                         {/* Asosiy xabar / Savol */}
                         <div 
                            className="message-bubble"
                            style={{
                              fontSize:'0.95rem', 
                              lineHeight:'1.6', 
                              color: m.is_answered ? 'rgba(255,255,255,0.6)' : '#e2e8f0', 
                              padding:'14px 18px',
                              background: m.is_answered ? 'rgba(255,255,255,0.01)' : (isStaffMsg ? 'rgba(99, 102, 241, 0.05)' : 'rgba(255,255,255,0.03)'),
                              borderRadius: '16px 16px 16px 4px',
                              borderLeft: m.is_answered ? '4px solid var(--primary)' : (isStaffMsg ? '1px solid rgba(99, 102, 241, 0.1)' : '1px solid rgba(255,255,255,0.05)'),
                              cursor: (isStaffMsg || m.is_answered) ? 'default' : 'pointer',
                              position: 'relative',
                              boxShadow: m.is_answered ? 'none' : '0 4px 15px rgba(0,0,0,0.1)'
                            }}
                            onClick={() => { if(!isStaffMsg && !m.is_answered) { setAnsweringId(m.id); setAnswerText(''); } }}
                         >
                            {m.is_answered && (
                               <div style={{display:'flex', alignItems:'center', gap:'6px', marginBottom:'6px'}}>
                                  <Icons.MessageCircle style={{width:12, color:'var(--primary)'}}/>
                                  <span style={{fontSize:'0.65rem', color:'var(--primary)', fontWeight:'800', textTransform:'uppercase'}}>Foydalanuvchi savoli:</span>
                               </div>
                            )}
                            {m.text}
                         </div>

                         {/* Javob qismi (Telegram style Premium) */}
                         {m.is_answered && (
                            <div style={{
                              marginLeft: '25px',
                              padding:'16px 20px', 
                              background:'rgba(16, 185, 129, 0.06)', 
                              borderRadius:'4px 18px 18px 18px', 
                              fontSize:'0.95rem', 
                              border:'1px solid rgba(16, 185, 129, 0.15)',
                              position: 'relative',
                              animation: 'fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                              boxShadow: '0 8px 20px rgba(0,0,0,0.1)'
                            }}>
                               <div style={{display:'flex', alignItems:'center', gap:'8px', marginBottom:'8px'}}>
                                  <div style={{background:'#10b981', borderRadius:'50%', width:'18px', height:'18px', display:'flex', alignItems:'center', justifyContent:'center'}}>
                                     <Icons.CheckCircle style={{width:10, color:'#fff'}}/>
                                  </div>
                                  <span style={{color:'#10b981', fontWeight:'800', fontSize:'0.7rem', textTransform:'uppercase', letterSpacing:'0.5px'}}>Admin Javobi</span>
                               </div>
                               <div style={{color:'rgba(255,255,255,0.95)', lineHeight:'1.6'}}>{m.answer_text}</div>
                            </div>
                         )}

                         {/* Javob yozish formasi */}
                         {answeringId === m.id && (
                           <form onSubmit={(e) => handleSendAnswer(e, m.id)} style={{marginTop:'10px', animation:'fadeIn 0.3s ease'}}>
                             <div style={{position:'relative'}}>
                                <textarea 
                                  rows="4" 
                                  value={answerText} 
                                  onChange={e => setAnswerText(e.target.value)}
                                  placeholder="Foydalanuvchiga javob yozing..."
                                  style={{
                                    width:'100%', padding:'15px', fontSize:'0.95rem', marginBottom:'12px', 
                                    borderRadius:'16px', background:'rgba(99,102,241,0.08)', color:'#fff', 
                                    border:'2px solid var(--primary)', outline:'none',
                                    boxShadow: '0 0 20px rgba(99,102,241,0.1)'
                                  }}
                                  required
                                  autoFocus
                                />
                                <div style={{display:'flex', gap:'10px', justifyContent:'flex-end'}}>
                                   <button type="button" className="btn btn-sm btn-danger" onClick={() => setAnsweringId(null)} style={{padding:'10px 20px', borderRadius:'12px'}}>
                                      <Icons.History style={{width:14, marginRight:6}}/> Bekor qilish
                                   </button>
                                   <button type="submit" className="btn btn-sm" disabled={sending} style={{padding:'10px 30px', borderRadius:'12px', background:'var(--primary)', boxShadow:'0 4px 15px rgba(99,102,241,0.3)'}}>
                                      {sending ? <div className="loader-sm"></div> : <><Icons.Training style={{width:14, marginRight:6, transform:'rotate(90deg)'}}/> Yuborish</>}
                                   </button>
                                </div>
                             </div>
                           </form>
                         )}
                      </div>
                    </td>
                    {!m.is_answered && (
                      <td style={{padding:'25px 10px'}}>
                         <div style={{textAlign:'center'}}>
                            {!isStaffMsg && !m.is_answered && answeringId !== m.id && (
                               <button 
                                 className="btn btn-sm" 
                                 onClick={() => {setAnsweringId(m.id); setAnswerText('');}} 
                                 style={{
                                   padding:'10px 25px', fontSize:'0.85rem', borderRadius:'12px',
                                   background: 'linear-gradient(135deg, var(--primary), #4f46e5)',
                                   boxShadow: '0 4px 15px rgba(99,102,241,0.2)',
                                   display:'inline-flex', alignItems:'center', gap:'8px'
                                 }}
                               >
                                  <Icons.MessageCircle style={{width:14}}/> Javob berish
                               </button>
                            )}
                            {isStaffMsg && (
                               <div style={{color:'var(--text-muted)', fontSize:'0.8rem', fontStyle:'italic', opacity:0.6, display:'flex', alignItems:'center', justifyContent:'center', gap:'6px'}}>
                                  <Icons.Training style={{width:14, opacity:0.5}}/> Chiqish xabari
                               </div>
                            )}
                         </div>
                      </td>
                    )}
                    <td style={{padding:'30px 10px', textAlign:'center'}}>
                        <div style={{display:'flex', flexDirection:'column', gap:'10px', alignItems:'center'}}>
                           <div 
                             style={{
                               fontSize:'0.7rem', 
                               padding:'8px 16px', 
                               borderRadius:'10px',
                               width:'100%', 
                               textAlign:'center',
                               background: m.is_answered ? 'rgba(16, 185, 129, 0.12)' : (isStaffMsg ? 'rgba(99, 102, 241, 0.1)' : 'rgba(239, 68, 68, 0.1)'),
                               color: m.is_answered ? '#10b981' : (isStaffMsg ? 'var(--primary)' : '#ef4444'),
                               fontWeight: '800',
                               display:'flex', alignItems:'center', justifyContent:'center', gap:'6px',
                               border: m.is_answered ? '1px solid rgba(16, 185, 129, 0.2)' : (isStaffMsg ? '1px solid rgba(99, 102, 241, 0.2)' : '1px solid rgba(239, 68, 68, 0.2)')
                             }}
                           >
                              {m.is_answered ? <Icons.CheckCircle style={{width:12}}/> : (isStaffMsg ? <Icons.Bot style={{width:12}}/> : <Icons.History style={{width:12, animation: 'pulse 2s infinite'}}/>)}
                              <span style={{letterSpacing:'0.5px'}}>{m.is_answered ? 'JAVOB BERILGAN' : (isStaffMsg ? 'XODIM XABARI' : 'KUTILMOQDA')}</span>
                           </div>
                           
                           <div style={{background:'rgba(255,255,255,0.03)', padding:'6px 10px', borderRadius:'6px', display:'flex', flexDirection:'column', gap:'4px', width:'100%'}}>
                              <div style={{fontSize:'0.65rem', color:'var(--text-muted)', fontWeight:600, display:'flex', justifyContent:'space-between'}}>
                                 <span>S:</span>
                                 <span>{formatDate(m.created_at)}</span>
                              </div>
                              {m.is_answered && m.answered_at && (
                                <div style={{fontSize:'0.65rem', color:'#10b981', fontWeight:800, display:'flex', justifyContent:'space-between', borderTop:'1px solid rgba(16, 185, 129, 0.1)', paddingTop:'4px'}}>
                                   <span>J:</span>
                                   <span>{formatDate(m.answered_at)}</span>
                                </div>
                              )}
                           </div>
                        </div>
                     </td>
                  </tr>
                );
              }) : <tr><td colSpan="5" style={{textAlign:'center', padding:'4rem', color:'var(--text-muted)'}}><Icons.History style={{display:'block', margin:'0 auto 1rem', opacity:0.2}}/> Hali xabarlar mavjud emas.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    )}
  </>);
}


function BotSettings({ token, showFlash, askConfirm }) {
  const [s, setS] = useState({ 
    tracking_mode: 'false', kb_only_mode: 'false', ai_provider: 'openai', openai_api_key: '', groq_api_key: '', gemini_api_key: ''
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
          tracking_mode: d.tracking_mode || 'false',
          kb_only_mode: d.kb_only_mode || 'false',
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
    }).then(() => { setSaving(null); showFlash('Muvaffaqiyatli saqlandi!'); }).catch(() => { setSaving(null); showFlash('Xatolik!', 'error'); });
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
          <div className="flex-between" style={{marginBottom:'1rem'}}>
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
          
          <div className="flex-between" style={{marginBottom:'1.5rem', paddingBottom:'1rem', borderBottom:'1px solid var(--card-border)'}}>
             <div style={{display:'flex', alignItems:'center', gap:'12px'}}>
                <div className="stat-icon-wrapper" style={{margin:0, color:'var(--warning)', background:'rgba(245, 158, 11, 0.1)'}}><Icons.History /></div>
                <div className="summary-title" style={{margin:0}}>Tracking Mode (Faqat sanash)</div>
             </div>
             <label className="switch">
                <input 
                  type="checkbox" 
                  checked={s.tracking_mode === 'true'} 
                  onChange={e => {
                    const newVal = e.target.checked ? 'true' : 'false';
                    setS({...s, tracking_mode: newVal});
                    save('tracking_mode', newVal);
                  }} 
                />
                <span className="slider round"></span>
             </label>
          </div>

          <div className="flex-between" style={{marginBottom:'1rem'}}>
             <div style={{display:'flex', alignItems:'center', gap:'12px'}}>
                <div className="stat-icon-wrapper" style={{margin:0, color:'var(--primary)', background:'rgba(99, 102, 241, 0.1)'}}><Icons.Shield /></div>
                <div className="summary-title" style={{margin:0}}>KB Only Mode (Faqat bazadan)</div>
             </div>
             <label className="switch">
                <input 
                  type="checkbox" 
                  checked={s.kb_only_mode === 'true'} 
                  onChange={e => {
                    const newVal = e.target.checked ? 'true' : 'false';
                    setS({...s, kb_only_mode: newVal});
                    save('kb_only_mode', newVal);
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
        fetch(`${API_URL}/settings/clear-everything`, { 
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


