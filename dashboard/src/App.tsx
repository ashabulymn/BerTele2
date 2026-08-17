import { useEffect, useMemo, useState, type ReactNode } from 'react'
import './App.css'

type IconName = 'grid' | 'send' | 'users' | 'webhook' | 'session' | 'media' | 'key' | 'activity' | 'settings' | 'menu' | 'bell' | 'search' | 'arrow' | 'check' | 'clock' | 'message'

type NavItem = {
  label: string
  icon: IconName
  badge?: string
}

const navGroups: { title: string; items: NavItem[] }[] = [
  { title: 'Workspace', items: [{ label: 'Overview', icon: 'grid' }, { label: 'Messages', icon: 'message', badge: '24' }, { label: 'Telegram', icon: 'send' }, { label: 'Sessions', icon: 'session' }] },
  { title: 'Integrations', items: [{ label: 'Webhooks', icon: 'webhook' }, { label: 'Media', icon: 'media' }, { label: 'API Keys', icon: 'key' }] },
  { title: 'System', items: [{ label: 'Activity', icon: 'activity' }, { label: 'Users', icon: 'users' }, { label: 'Settings', icon: 'settings' }] },
]

const activity = [
  { title: 'Telegram message received', detail: 'BerTele2 Bot · @duitku_robot', time: '2 min ago', type: 'message' },
  { title: 'Webhook delivered', detail: 'n8n · message.received', time: '7 min ago', type: 'success' },
  { title: 'Session reconnected', detail: 'telegram-main · +62 •••• 2188', time: '12 min ago', type: 'success' },
  { title: 'Media download completed', detail: 'telegram-media · 2.4 MB', time: '18 min ago', type: 'success' },
]

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const common = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const }
  const paths: Record<IconName, ReactNode> = {
    grid: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>,
    send: <><path d="m22 2-7 20-4-9-9-4Z" /><path d="M22 2 11 13" /></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></>,
    webhook: <><path d="M18 8a4 4 0 0 0-7.75-1.25L8.8 9.5" /><path d="M6 16a4 4 0 0 0 7.75 1.25l1.45-2.75" /><path d="m14.5 8.5-5 7" /><path d="M5 12h6" /><path d="M13 12h6" /></>,
    session: <><rect x="3" y="4" width="18" height="16" rx="2" /><path d="M7 8h.01M11 8h.01" /><path d="M7 12h10M7 16h6" /></>,
    media: <><rect x="3" y="3" width="18" height="18" rx="2" /><circle cx="8.5" cy="8.5" r="1.5" /><path d="m21 15-5-5L5 21" /></>,
    key: <><circle cx="8" cy="15" r="4" /><path d="m10.8 12.2 7.7-7.7a2.1 2.1 0 0 1 3 3l-1.4 1.4-1.5-1.5-1.8 1.8 1.5 1.5-2.2 2.2" /></>,
    activity: <><path d="M3 12h4l3-8 4 16 3-8h4" /></>,
    settings: <><path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z" /><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-1.8 1.8-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V20h-2.54v-.1a1.7 1.7 0 0 0-1.03-1.56 1.7 1.7 0 0 0-1.88.34l-.06.06-1.8-1.8.06-.06A1.7 1.7 0 0 0 8.1 15a1.7 1.7 0 0 0-1.56-1.03H6v-2.54h.54A1.7 1.7 0 0 0 8.1 10.4a1.7 1.7 0 0 0-.34-1.88L7.7 8.46l1.8-1.8.06.06a1.7 1.7 0 0 0 1.88.34A1.7 1.7 0 0 0 12.47 5.5V5h2.54v.5a1.7 1.7 0 0 0 1.03 1.56 1.7 1.7 0 0 0 1.88-.34l.06-.06 1.8 1.8-.06.06A1.7 1.7 0 0 0 19.4 10.4a1.7 1.7 0 0 0 1.56 1.03H21v2.54h-.04A1.7 1.7 0 0 0 19.4 15Z" /></>,
    menu: <><path d="M4 6h16M4 12h16M4 18h16" /></>,
    bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" /><path d="M10 21h4" /></>,
    search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>,
    arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
    message: <><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9.7 9.7 0 0 1-4.3-1L3 20l1.1-4.1A8.4 8.4 0 0 1 3 11.5 8.4 8.4 0 0 1 12 3a8.4 8.4 0 0 1 9 8.5Z" /><path d="M8 12h.01M12 12h.01M16 12h.01" /></>,
  }
  return <svg {...common} aria-hidden="true">{paths[name]}</svg>
}

function App() {
  const [active, setActive] = useState('Overview')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)
  const [search, setSearch] = useState('')

  const apiBase = import.meta.env.VITE_API_BASE_URL || '/api/v1'

  useEffect(() => {
    let mounted = true
    fetch(`${apiBase}/health`, { headers: { Accept: 'application/json' } })
      .then((response) => { if (mounted) setApiOnline(response.ok) })
      .catch(() => { if (mounted) setApiOnline(false) })
    return () => { mounted = false }
  }, [apiBase])

  const filteredActivity = useMemo(() => {
    const query = search.trim().toLowerCase()
    if (!query) return activity
    return activity.filter((item) => `${item.title} ${item.detail}`.toLowerCase().includes(query))
  }, [search])

  return (
    <div className="app-shell">
      {sidebarOpen && <button className="mobile-overlay" aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}
      <aside className={`sidebar ${sidebarOpen ? 'is-open' : ''}`}>
        <div className="brand"><div className="brand-mark">B</div><div><strong>BerTele2</strong><span>Control Center</span></div></div>
        <div className="workspace-switcher"><div className="workspace-avatar">B</div><div><strong>BerTele2 Production</strong><span>Workspace</span></div><span className="chevron">⌄</span></div>
        <nav>{navGroups.map((group) => <div className="nav-group" key={group.title}><div className="nav-label">{group.title}</div>{group.items.map((item) => <button key={item.label} className={`nav-item ${active === item.label ? 'active' : ''}`} onClick={() => { setActive(item.label); setSidebarOpen(false) }}><Icon name={item.icon} /><span>{item.label}</span>{item.badge && <b>{item.badge}</b>}</button>)}</div>)}</nav>
        <div className="sidebar-footer"><div className="status-row"><span className={`status-dot ${apiOnline === false ? 'offline' : ''}`} /><span>{apiOnline === false ? 'API offline' : apiOnline === true ? 'API connected' : 'Checking API…'}</span></div><button className="user-card"><div className="avatar">AY</div><div><strong>Admin</strong><span>Administrator</span></div><span>•••</span></button></div>
      </aside>

      <main className="main">
        <header className="topbar"><button className="icon-button mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Icon name="menu" /></button><div className="breadcrumbs"><span>BerTele2</span><i>/</i><strong>{active}</strong></div><div className="top-actions"><label className="search"><Icon name="search" /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search activity…" /></label><button className="icon-button notification"><Icon name="bell" /><span /></button><div className="avatar top-avatar">AY</div></div></header>

        <div className="content">
          <section className="page-heading"><div><div className="eyebrow">CONTROL CENTER</div><h1>{active}</h1><p>{active === 'Overview' ? 'Monitor Telegram, webhooks, media and automation from one place.' : `Manage your ${active.toLowerCase()} from the BerTele2 control center.`}</p></div><div className="heading-actions"><button className="secondary-button">Last 24 hours⌄</button><button className="primary-button" onClick={() => setActive('Messages')}><Icon name="send" size={16} /> Send message</button></div></section>

          {active === 'Overview' ? <>
            <section className="stats-grid"><Stat label="Messages today" value="1,284" change="+18.4%" tone="green" icon="message" /><Stat label="Active sessions" value="4 / 5" change="80% online" tone="blue" icon="session" /><Stat label="Webhook deliveries" value="98.7%" change="+2.1%" tone="purple" icon="webhook" /><Stat label="Media processed" value="3.8 GB" change="+12.6%" tone="orange" icon="media" /></section>
            <section className="dashboard-grid"><div className="panel traffic-panel"><div className="panel-header"><div><h2>Message activity</h2><p>Incoming and outgoing messages</p></div><span className="live-pill"><i /> Live</span></div><div className="chart"><div className="chart-y"><span>400</span><span>300</span><span>200</span><span>100</span><span>0</span></div><div className="chart-area"><div className="grid-lines"><i /><i /><i /><i /><i /></div><svg viewBox="0 0 700 240" preserveAspectRatio="none" aria-label="Message activity chart"><defs><linearGradient id="fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="currentColor" stopOpacity=".22" /><stop offset="1" stopColor="currentColor" stopOpacity="0" /></linearGradient></defs><path className="area" d="M0 190 C45 178 55 120 95 145 S150 190 185 120 S245 90 280 118 S330 160 370 85 S430 115 470 105 S520 48 555 78 S610 118 650 62 S680 55 700 35 V240 H0Z" /><path className="line" d="M0 190 C45 178 55 120 95 145 S150 190 185 120 S245 90 280 118 S330 160 370 85 S430 115 470 105 S520 48 555 78 S610 118 650 62 S680 55 700 35" /></svg><div className="chart-x"><span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>Now</span></div></div></div><div className="legend"><span><i className="incoming" /> Incoming <b>842</b></span><span><i className="outgoing" /> Outgoing <b>442</b></span></div></div>
              <div className="panel health-panel"><div className="panel-header"><div><h2>System health</h2><p>Live service status</p></div><button className="more">•••</button></div><div className="health-score"><div className="score-ring"><strong>98</strong><span>/100</span></div><div><strong>Excellent</strong><p>All critical services are healthy.</p></div></div><div className="service-list"><Service name="Telegram engine" detail="MTProto connection" status="Operational" /><Service name="Webhook dispatcher" detail="Delivery queue" status="Operational" /><Service name="Media pipeline" detail="Storage + processing" status="Operational" /><Service name="n8n integration" detail="Automation bridge" status="Operational" /></div></div></section>
            <section className="bottom-grid"><div className="panel activity-panel"><div className="panel-header"><div><h2>Recent activity</h2><p>Latest events across your workspace</p></div><button className="link-button" onClick={() => setActive('Activity')}>View all <Icon name="arrow" size={15} /></button></div><div className="activity-list">{filteredActivity.map((item) => <div className="activity-item" key={item.title}><div className={`activity-icon ${item.type}`}><Icon name={item.type === 'message' ? 'message' : 'check'} size={16} /></div><div><strong>{item.title}</strong><span>{item.detail}</span></div><time>{item.time}</time></div>)}</div></div><div className="panel quick-panel"><div className="panel-header"><div><h2>Quick actions</h2><p>Common tasks</p></div></div><div className="quick-actions"><QuickAction icon="send" title="Send Telegram message" onClick={() => setActive('Messages')} /><QuickAction icon="webhook" title="Create webhook" onClick={() => setActive('Webhooks')} /><QuickAction icon="session" title="Manage sessions" onClick={() => setActive('Sessions')} /><QuickAction icon="key" title="Create API key" onClick={() => setActive('API Keys')} /></div></div></section>
          </> : <section className="panel placeholder"><div className="placeholder-icon"><Icon name={navGroups.flatMap((group) => group.items).find((item) => item.label === active)?.icon || 'grid'} size={26} /></div><h2>{active}</h2><p>The UI foundation is ready. This module is connected to the existing BerTele2 API architecture and can be wired to its endpoint without changing the dashboard shell.</p><button className="primary-button" onClick={() => setActive('Overview')}>Back to overview</button></section>}
        </div>
      </main>
    </div>
  )
}

function Stat({ label, value, change, tone, icon }: { label: string; value: string; change: string; tone: string; icon: IconName }) { return <div className="stat-card"><div className={`stat-icon ${tone}`}><Icon name={icon} /></div><div className="stat-copy"><span>{label}</span><strong>{value}</strong><small className={tone === 'green' || tone === 'blue' ? 'positive' : ''}>{change}</small></div><span className="stat-period">Today</span></div> }
function Service({ name, detail, status }: { name: string; detail: string; status: string }) { return <div className="service"><div className="service-status"><i /></div><div><strong>{name}</strong><span>{detail}</span></div><b>{status}</b></div> }
function QuickAction({ icon, title, onClick }: { icon: IconName; title: string; onClick: () => void }) { return <button className="quick-action" onClick={onClick}><span><Icon name={icon} size={17} /></span><strong>{title}</strong><Icon name="arrow" size={15} /></button> }

export default App
