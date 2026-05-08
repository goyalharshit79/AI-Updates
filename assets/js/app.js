'use strict';

const PER_PAGE = 8;
let allPosts = [], filtered = [], page = 1, activeCat = 'all';

/* ─── Neural Canvas ─────────────────────────── */
function initCanvas() {
  const c = document.getElementById('neural-canvas');
  if (!c) return;
  const ctx = c.getContext('2d');
  let P = [], W, H;

  function resize() {
    W = c.width = innerWidth;
    H = c.height = innerHeight;
    P = Array.from({ length: Math.floor(W * H / 13000) }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - .5) * .36, vy: (Math.random() - .5) * .36,
      r: Math.random() * 1.5 + .5
    }));
  }

  function frame() {
    ctx.clearRect(0, 0, W, H);
    P.forEach(p => {
      p.x = (p.x + p.vx + W) % W;
      p.y = (p.y + p.vy + H) % H;
    });
    for (let i = 0; i < P.length; i++) {
      for (let j = i + 1; j < P.length; j++) {
        const d = Math.hypot(P[i].x - P[j].x, P[i].y - P[j].y);
        if (d < 125) {
          ctx.beginPath();
          ctx.moveTo(P[i].x, P[i].y);
          ctx.lineTo(P[j].x, P[j].y);
          ctx.strokeStyle = `rgba(139,92,246,${.13 * (1 - d / 125)})`;
          ctx.lineWidth = .6;
          ctx.stroke();
        }
      }
      ctx.beginPath();
      ctx.arc(P[i].x, P[i].y, P[i].r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(168,85,247,.55)';
      ctx.fill();
    }
    requestAnimationFrame(frame);
  }

  resize();
  frame();
  addEventListener('resize', resize);
}

/* ─── Helpers ───────────────────────────────── */
const fmtDate = d => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
const catClass = c => ({ Models: 'cat-models', Tools: 'cat-tools', Research: 'cat-research', Industry: 'cat-industry', News: 'cat-news' }[c] || 'cat-news');

function postCard(p, feat = false) {
  const tags = (p.tags || []).slice(0, 3).map(t => `<span class="tag">${t}</span>`).join('');
  return `<a href="post.html?slug=${p.slug}" class="post-card${feat ? ' feat' : ''}">
    <div class="card-body">
      <div class="card-meta">
        <span class="cat ${catClass(p.category)}">${p.category}</span>
        <span class="card-date">${fmtDate(p.date)}</span>
      </div>
      <h3 class="card-title">${p.title}</h3>
      <p class="card-excerpt">${p.excerpt}</p>
    </div>
    <div class="card-foot">
      <div class="card-tags">${tags}</div>
      <span class="read-time">${p.readTime || '3 min'} read</span>
    </div>
  </a>`;
}

function emptyState() {
  return `<div class="empty"><div class="empty-icon">◉</div><p class="empty-txt">No posts match this filter.</p></div>`;
}

/* ─── Render ─────────────────────────────────── */
function render() {
  const fg = document.getElementById('featuredGrid');
  const pg = document.getElementById('postsGrid');
  const lm = document.getElementById('loadMore');
  const fh = document.getElementById('featuredHead');
  if (!pg) return;

  const isAll = activeCat === 'all';
  const featured = isAll ? allPosts.filter(p => p.featured).slice(0, 3) : [];
  const rest = isAll ? allPosts.filter(p => !p.featured) : filtered;
  const paged = rest.slice(0, page * PER_PAGE);

  if (fg) {
    const show = featured.length > 0;
    fg.style.display = show ? 'grid' : 'none';
    if (fh) fh.style.display = show ? 'flex' : 'none';
    fg.innerHTML = featured.map(p => postCard(p, true)).join('');
  }

  pg.innerHTML = paged.length ? paged.map(p => postCard(p)).join('') : emptyState();
  if (lm) lm.style.display = rest.length > page * PER_PAGE ? 'block' : 'none';
}

/* ─── Filter ─────────────────────────────────── */
window.setCategory = function (cat) {
  activeCat = cat;
  page = 1;
  filtered = cat === 'all' ? [...allPosts] : allPosts.filter(p => p.category === cat);
  document.querySelectorAll('.ftab').forEach(t => t.classList.toggle('active', t.dataset.cat === cat));
  render();
  document.getElementById('latest')?.scrollIntoView({ behavior: 'smooth' });
};

/* ─── Search overlay ────────────────────────── */
function initSearch() {
  const overlay = document.getElementById('searchOverlay');
  const inp = document.getElementById('searchInput');
  const res = document.getElementById('searchRes');
  if (!overlay) return;

  function open() { overlay.classList.add('open'); setTimeout(() => inp.focus(), 80); }
  function close() { overlay.classList.remove('open'); inp.value = ''; res.innerHTML = ''; }

  document.querySelectorAll('.open-search').forEach(b => b.addEventListener('click', open));
  document.getElementById('searchClose')?.addEventListener('click', close);
  overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') close();
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); open(); }
  });

  inp.addEventListener('input', () => {
    const q = inp.value.toLowerCase().trim();
    if (!q) { res.innerHTML = ''; return; }
    const hits = allPosts.filter(p =>
      p.title.toLowerCase().includes(q) ||
      p.excerpt.toLowerCase().includes(q) ||
      (p.tags || []).some(t => t.toLowerCase().includes(q))
    ).slice(0, 8);
    res.innerHTML = hits.length
      ? hits.map(p => `<a href="post.html?slug=${p.slug}" class="s-item">
          <div class="s-item-title">${p.title}</div>
          <div class="s-item-meta">${p.category} · ${fmtDate(p.date)} · ${p.readTime || '3 min'} read</div>
        </a>`).join('')
      : '<p style="color:var(--text-3);padding:1.5rem 0;font-size:.84rem">No results found.</p>';
  });
}

/* ─── Ticker ────────────────────────────────── */
function buildTicker(posts) {
  const el = document.getElementById('tickerInner');
  if (!el || !posts.length) return;
  const items = posts.slice(0, 12).map(p => `<span class="ticker-item">${p.title}</span>`).join('');
  el.innerHTML = items + items;
}

/* ─── Stats ──────────────────────────────────── */
function updateStats(posts) {
  const g = id => document.getElementById(id);
  if (g('stat-posts')) g('stat-posts').textContent = posts.length;
  if (g('stat-models')) g('stat-models').textContent = posts.filter(p => p.category === 'Models').length;
  if (g('stat-tools')) g('stat-tools').textContent = posts.filter(p => p.category === 'Tools').length;
  ['models','tools','research','industry','news'].forEach(c => {
    const el = g(`count-${c}`);
    if (el) el.textContent = posts.filter(p => p.category === (c.charAt(0).toUpperCase() + c.slice(1))).length;
  });
}

/* ─── Affiliates ─────────────────────────────── */
async function loadAffiliates() {
  try {
    const data = await fetch('./affiliates.json').then(r => r.json());
    const tools = data.affiliates.filter(a => a.category === 'Tools');
    const learn = data.affiliates.filter(a => a.category !== 'Tools');

    const renderSection = (items, elId) => {
      const el = document.getElementById(elId);
      if (!el) return;
      el.innerHTML = items.map(a => `
        <a href="${a.url}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="aff-card" data-aff-id="${a.id}">
          <div class="aff-icon" style="background:${a.bg || 'rgba(139,92,246,.15)'}">${a.icon}</div>
          <div>
            <div class="aff-name">${a.name}</div>
            <div class="aff-desc">${a.description}</div>
          </div>
        </a>`).join('');
      el.querySelectorAll('a[data-aff-id]').forEach(a => {
        a.addEventListener('click', () => {
          if (typeof gtag === 'function') {
            gtag('event', 'affiliate_click', {
              event_category: 'engagement',
              event_label: a.dataset.affId,
              transport_type: 'beacon'
            });
          }
        });
      });
    };

    renderSection(tools, 'affTools');
    renderSection(learn, 'affLearn');
  } catch (e) {
    console.warn('Affiliates not loaded:', e);
  }
}

/* ─── Init ───────────────────────────────────── */
async function init() {
  initCanvas();
  initSearch();

  document.querySelectorAll('.ftab').forEach(t =>
    t.addEventListener('click', () => setCategory(t.dataset.cat))
  );
  document.getElementById('loadMore')?.addEventListener('click', () => { page++; render(); });

  try {
    const data = await fetch('./posts/index.json').then(r => r.json());
    allPosts = (data.posts || []).sort((a, b) => new Date(b.date) - new Date(a.date));
    filtered = [...allPosts];
    updateStats(allPosts);
    buildTicker(allPosts);
    render();
  } catch (e) {
    console.error('Failed to load posts:', e);
    const pg = document.getElementById('postsGrid');
    if (pg) pg.innerHTML = emptyState();
  }

  loadAffiliates();
}

document.addEventListener('DOMContentLoaded', init);
