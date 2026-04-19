'use strict';

/* ─── Canvas (reduced density for post page) ─── */
function initCanvas() {
  const c = document.getElementById('neural-canvas');
  if (!c) return;
  const ctx = c.getContext('2d');
  let P = [], W, H;

  function resize() {
    W = c.width = innerWidth; H = c.height = innerHeight;
    P = Array.from({ length: Math.floor(W * H / 20000) }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - .5) * .28, vy: (Math.random() - .5) * .28,
      r: Math.random() * 1.2 + .4
    }));
  }

  function frame() {
    ctx.clearRect(0, 0, W, H);
    P.forEach(p => { p.x = (p.x + p.vx + W) % W; p.y = (p.y + p.vy + H) % H; });
    for (let i = 0; i < P.length; i++) {
      for (let j = i + 1; j < P.length; j++) {
        const d = Math.hypot(P[i].x - P[j].x, P[i].y - P[j].y);
        if (d < 130) {
          ctx.beginPath(); ctx.moveTo(P[i].x, P[i].y); ctx.lineTo(P[j].x, P[j].y);
          ctx.strokeStyle = `rgba(139,92,246,${.1 * (1 - d / 130)})`; ctx.lineWidth = .5; ctx.stroke();
        }
      }
      ctx.beginPath(); ctx.arc(P[i].x, P[i].y, P[i].r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(168,85,247,.45)'; ctx.fill();
    }
    requestAnimationFrame(frame);
  }

  resize(); frame(); addEventListener('resize', resize);
}

/* ─── Reading progress bar ──────────────────── */
function initProgress() {
  const bar = document.getElementById('progressBar');
  if (!bar) return;
  addEventListener('scroll', () => {
    const pct = scrollY / (document.documentElement.scrollHeight - innerHeight) * 100;
    bar.style.width = Math.min(pct, 100) + '%';
  });
}

/* ─── Helpers ───────────────────────────────── */
const fmtDate = d => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
const catClass = c => ({ Models: 'cat-models', Tools: 'cat-tools', Research: 'cat-research', Industry: 'cat-industry', News: 'cat-news' }[c] || 'cat-news');
const getSlug = () => new URLSearchParams(location.search).get('slug');

/* ─── Parse YAML-ish frontmatter ─────────────── */
function parseFrontmatter(raw) {
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) return { meta: {}, body: raw };

  const meta = {};
  match[1].split('\n').forEach(line => {
    const colon = line.indexOf(':');
    if (colon < 0) return;
    const k = line.slice(0, colon).trim();
    const v = line.slice(colon + 1).trim().replace(/^["']|["']$/g, '');
    if (k) meta[k] = v;
  });

  // Parse tags array: tags: ["a", "b"]
  const tagsMatch = match[1].match(/^tags:\s*\[([^\]]*)\]/m);
  if (tagsMatch) {
    meta.tags = tagsMatch[1].split(',').map(t => t.trim().replace(/^["']|["']$/g, '')).filter(Boolean);
  }

  return { meta, body: match[2] };
}

/* ─── Build table of contents ───────────────── */
function buildTOC(contentEl) {
  const toc = document.getElementById('tocList');
  if (!toc) return;
  const headings = [...contentEl.querySelectorAll('h2, h3')];
  if (headings.length < 2) { document.getElementById('tocBox')?.remove(); return; }

  headings.forEach((h, i) => { h.id = `heading-${i}`; });

  toc.innerHTML = headings.map((h, i) =>
    `<li class="toc-item ${h.tagName === 'H3' ? 'h3' : ''}">
      <a href="#heading-${i}">${h.textContent}</a>
    </li>`
  ).join('');
}

/* ─── Related post card ─────────────────────── */
function postCard(p) {
  return `<a href="post.html?slug=${p.slug}" class="post-card">
    <div class="card-body">
      <div class="card-meta">
        <span class="cat ${catClass(p.category)}">${p.category}</span>
        <span class="card-date">${fmtDate(p.date)}</span>
      </div>
      <h3 class="card-title">${p.title}</h3>
      <p class="card-excerpt">${p.excerpt}</p>
    </div>
    <div class="card-foot">
      <span class="read-time">${p.readTime || '3 min'} read</span>
    </div>
  </a>`;
}

/* ─── Main ───────────────────────────────────── */
async function init() {
  initCanvas();
  initProgress();

  const slug = getSlug();
  if (!slug) { location.href = 'index.html'; return; }

  try {
    const [mdRaw, manifest] = await Promise.all([
      fetch(`./posts/${slug}.md`).then(r => { if (!r.ok) throw new Error(r.status); return r.text(); }),
      fetch('./posts/index.json').then(r => r.json())
    ]);

    const { meta, body } = parseFrontmatter(mdRaw);

    // Render hero
    const hero = document.getElementById('postHero');
    if (hero) {
      const tagList = Array.isArray(meta.tags) ? meta.tags.join(', ') : (meta.tags || '');
      hero.innerHTML = `
        <span class="post-category-badge ${catClass(meta.category || 'News')}">${meta.category || 'News'}</span>
        <h1 class="post-title gradient-text">${meta.title || slug}</h1>
        <div class="post-meta-bar">
          <span>📅 ${fmtDate(meta.date || new Date())}</span>
          <span>⏱ ${meta.readTime || '5 min'} read</span>
          ${tagList ? `<span>🏷 ${tagList}</span>` : ''}
        </div>`;
    }

    // Update page meta
    document.title = `${meta.title || slug} — AI Pulse`;
    const descEl = document.querySelector('meta[name="description"]');
    if (descEl) descEl.setAttribute('content', meta.excerpt || '');

    // Render markdown
    const content = document.getElementById('postContent');
    if (content && typeof marked !== 'undefined') {
      marked.setOptions({ breaks: true, gfm: true });
      content.innerHTML = marked.parse(body);
      buildTOC(content);
    }

    // Related posts (same category, shuffled)
    const all = manifest.posts || [];
    const related = all
      .filter(p => p.slug !== slug && p.category === (meta.category || ''))
      .sort(() => Math.random() - .5)
      .slice(0, 3);

    if (related.length) {
      const sec = document.getElementById('relatedSection');
      const grid = document.getElementById('relatedGrid');
      if (sec && grid) {
        grid.innerHTML = related.map(postCard).join('');
        sec.style.display = 'block';
      }
    }

  } catch (e) {
    console.error('Post load failed:', e);
    const content = document.getElementById('postContent');
    const hero = document.getElementById('postHero');
    if (hero) hero.innerHTML = '';
    if (content) content.innerHTML = `
      <div class="empty" style="grid-column:1/-1">
        <div class="empty-icon">⚠</div>
        <p class="empty-txt">Post not found. <a href="index.html" style="color:var(--accent)">← Go back</a></p>
      </div>`;
  }
}

document.addEventListener('DOMContentLoaded', init);
