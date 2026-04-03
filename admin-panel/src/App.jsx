import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000';

function App() {
  const [token, setToken] = useState(localStorage.getItem('admin_token'));
  const [activeTab, setActiveTab] = useState('dashboard');
  const [username, setUsername] = useState('');

  useEffect(() => {
    if (token) {
      fetch(`${API_URL}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      .then(res => {
        if (res.status === 401) {
          handleLogout();
          return;
        }
        return res.json();
      })
      .then(data => {
        if (data) setUsername(data.username);
      })
      .catch(() => handleLogout());
    }
  }, [token]);

  const handleLogin = (newToken) => {
    localStorage.setItem('admin_token', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    setToken(null);
  };

  if (!token) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="brand">UySot Bot Admin</div>
        <div className="user-info">Logged in as: <strong>{username}</strong></div>
        <div 
          className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </div>
        <div 
          className={`nav-link ${activeTab === 'knowledge' ? 'active' : ''}`}
          onClick={() => setActiveTab('knowledge')}
        >
          Knowledge Base (AI Training)
        </div>
        <div 
          className={`nav-link ${activeTab === 'messages' ? 'active' : ''}`}
          onClick={() => setActiveTab('messages')}
        >
          QA History & Unanswered
        </div>
        <div 
          className={`nav-link ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          Mening Profilim
        </div>
        <div className="nav-link logout" onClick={handleLogout} style={{marginTop: 'auto', color: '#f87171'}}>
          Chiqish (Logout)
        </div>
      </div>
      <div className="main-content">
        {activeTab === 'dashboard' && <Dashboard token={token} />}
        {activeTab === 'knowledge' && <KnowledgeBase token={token} />}
        {activeTab === 'messages' && <Messages token={token} />}
        {activeTab === 'profile' && <Profile token={token} setUsername={setUsername} />}
      </div>
    </div>
  );
}

function Login({ onLogin }) {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    .then(res => res.json())
    .then(data => {
      if (data.access_token) {
        onLogin(data.access_token);
      } else {
        setError('Login yoki parol xato!');
      }
    })
    .catch(() => setError('Server bilan bog\'lanishda xato!'));
  };

  return (
    <div className="login-screen">
      <div className="glass-card login-card">
        <h2>UySot Bot Admin</h2>
        <p>Tizimga kirish uchun ma'lumotlarni kiriting</p>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Login</label>
            <input 
              type="text" 
              value={form.username} 
              onChange={e => setForm({...form, username: e.target.value})} 
              required 
            />
          </div>
          <div className="form-group">
            <label>Parol</label>
            <input 
              type="password" 
              value={form.password} 
              onChange={e => setForm({...form, password: e.target.value})} 
              required 
            />
          </div>
          <button type="submit" className="btn">Kirish</button>
        </form>
      </div>
    </div>
  );
}

function Profile({ token, setUsername }) {
  const [form, setForm] = useState({ username: '', password: '', confirmPassword: '' });
  const [msg, setMsg] = useState({ type: '', text: '' });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (form.password && form.password !== form.confirmPassword) {
      setMsg({ type: 'error', text: 'Parollar mos kelmadi!' });
      return;
    }

    fetch(`${API_URL}/auth/me`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        username: form.username || undefined,
        password: form.password || undefined
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        setMsg({ type: 'success', text: 'Profil muvaffaqiyatli yangilandi!' });
        if (data.new_username) setUsername(data.new_username);
        setForm({ username: '', password: '', confirmPassword: '' });
      } else {
        setMsg({ type: 'error', text: data.detail || 'Xatolik yuz berdi!' });
      }
    });
  };

  return (
    <>
      <h2 className="header-title">Mening Profilim</h2>
      <div className="glass-card" style={{maxWidth: '500px'}}>
        <h3>Ma'lumotlarni tahrirlash</h3>
        {msg.text && <div className={`${msg.type}-msg`} style={{marginBottom: '1rem'}}>{msg.text}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Yangi Login (bo'sh qolsa o'zgarmaydi)</label>
            <input type="text" value={form.username} onChange={e => setForm({...form, username: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Yangi Parol (bo'sh qolsa o'zgarmaydi)</label>
            <input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Yangi Parolni tasdiqlang</label>
            <input type="password" value={form.confirmPassword} onChange={e => setForm({...form, confirmPassword: e.target.value})} />
          </div>
          <button type="submit" className="btn">Saqlash</button>
        </form>
      </div>
    </>
  );
}

function Dashboard({ token }) {
  const [stats, setStats] = useState({ 
    total_groups: 0, 
    total_questions: 0,
    answered_questions: 0,
    unanswered_questions: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/dashboard/stats`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => console.error(err));
  }, [token]);

  if (loading) return <div className="loader"></div>;

  return (
    <>
      <h2 className="header-title">Dashboard Overview</h2>
      <div className="grid-cards">
        <div className="glass-card stat-card">
          <div className="stat-value">{stats.total_groups || 0}</div>
          <div className="stat-label">Active Groups</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value">{stats.total_questions || 0}</div>
          <div className="stat-label">Total Questions Asked</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value" style={{color: '#34d399'}}>{stats.answered_questions || 0}</div>
          <div className="stat-label">Answered by AI/KB</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value" style={{color: '#f87171'}}>{stats.unanswered_questions || 0}</div>
          <div className="stat-label">Unanswered</div>
        </div>
      </div>
    </>
  );
}

function KnowledgeBase({ token }) {
  const [kb, setKb] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ question: '', answer: '' });

  const fetchKb = () => {
    fetch(`${API_URL}/knowledge/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        setKb(data);
        setLoading(false);
      })
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetchKb();
  }, [token]);

  const handleSubmit = (e) => {
    e.preventDefault();
    fetch(`${API_URL}/knowledge/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(form)
    })
    .then(() => {
      setForm({ question: '', answer: '' });
      fetchKb();
    });
  };

  const handleDelete = (id) => {
    if(window.confirm('Delete this knowledge entry?')) {
      fetch(`${API_URL}/knowledge/${id}`, { 
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      .then(() => fetchKb());
    }
  };

  return (
    <>
      <h2 className="header-title">AI Training Data (Knowledge Base)</h2>
      <div className="glass-card">
        <h3>Add New Training Material</h3>
        <form onSubmit={handleSubmit} style={{marginTop: '1rem'}}>
          <div className="form-group">
            <label>Expected Question / Topic</label>
            <input 
              required 
              type="text" 
              placeholder="e.g. Parolni qanday tiklayman?"
              value={form.question}
              onChange={(e) => setForm({...form, question: e.target.value})}
            />
          </div>
          <div className="form-group">
            <label>AI Answer Source</label>
            <textarea 
              required 
              placeholder="Provide the exact fact/answer. AI will use this context to answer nicely."
              value={form.answer}
              onChange={(e) => setForm({...form, answer: e.target.value})}
            ></textarea>
          </div>
          <button type="submit" className="btn">Add to Knowledge</button>
        </form>
      </div>

      <div className="glass-card table-wrapper">
        {loading ? <div className="loader"></div> : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Trained Question</th>
                <th>Context Provided</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {kb.map(item => (
                <tr key={item.id}>
                  <td>#{item.id}</td>
                  <td>{item.question}</td>
                  <td>{item.answer.substring(0, 100)}{item.answer.length > 100 ? '...' : ''}</td>
                  <td>
                    <button className="btn btn-danger" onClick={() => handleDelete(item.id)}>Delete</button>
                  </td>
                </tr>
              ))}
              {kb.length === 0 && <tr><td colSpan="4">No knowledge entries found. Add some above.</td></tr>}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}

function Messages({ token }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/questions/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    }) 
      .then(res => res.json())
      .then(data => {
        setMessages(data.items || []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [token]);

  return (
    <>
      <h2 className="header-title">Questions History</h2>
      <div className="glass-card table-wrapper">
        {loading ? <div className="loader"></div> : (
          <table>
            <thead>
              <tr>
                <th>User</th>
                <th>Group</th>
                <th>Question</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {messages.map(msg => (
                <tr key={msg.id}>
                  <td>{msg.full_name}</td>
                  <td>Group #{msg.group_id}</td>
                  <td>{msg.text}</td>
                  <td>
                    {msg.is_answered ? 
                      (msg.answered_by_bot ? <span className="badge badge-ai">Answered by AI</span> : <span className="badge badge-kb">Answered by User</span>)
                      : <span className="badge badge-unanswered">Unanswered</span>
                    }
                  </td>
                </tr>
              ))}
              {messages.length === 0 && <tr><td colSpan="4">No questions yet.</td></tr>}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}

export default App;
