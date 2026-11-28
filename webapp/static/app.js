(function () {
  'use strict';

  // ---------- Tiện ích DOM (không dùng innerHTML với dữ liệu động) ----------
  const SVGNS = 'http://www.w3.org/2000/svg';
  const ICONS = {
    check: ['M20 6 9 17l-5-5'],
    x: ['M18 6 6 18', 'm6 6 12 12'],
    warn: ['m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3', 'M12 9v4', 'M12 17h.01']
  };

  function icon(name, size) {
    const svg = document.createElementNS(SVGNS, 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('width', String(size || 24));
    svg.setAttribute('height', String(size || 24));
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '2');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    svg.setAttribute('aria-hidden', 'true');
    for (const d of ICONS[name]) {
      const p = document.createElementNS(SVGNS, 'path');
      p.setAttribute('d', d);
      svg.appendChild(p);
    }
    return svg;
  }

  function h(tag, props) {
    const el = document.createElement(tag);
    if (props) {
      for (const key of Object.keys(props)) {
        const v = props[key];
        if (v == null || v === false) continue;
        if (key === 'class') el.className = v;
        else if (key === 'text') el.textContent = v;
        else if (key.indexOf('on') === 0) el.addEventListener(key.slice(2), v);
        else el.setAttribute(key, v === true ? '' : v);
      }
    }
    for (let i = 2; i < arguments.length; i++) {
      for (const kid of [].concat(arguments[i])) {
        if (kid == null || kid === false) continue;
        el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
      }
    }
    return el;
  }

  const $ = (id) => document.getElementById(id);
  const reduceMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const ISO_RE = /^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?/;
  function fmtDMY(iso) { const m = ISO_RE.exec(iso || ''); return m ? m[3] + '/' + m[2] + '/' + m[1] : ''; }
  function fmtShort(iso) { const m = ISO_RE.exec(iso || ''); return m ? m[3] + '/' + m[2] + ' ' + (m[4] || '00') + ':' + (m[5] || '00') : ''; }

  const state = { info: null, busy: false, lastAsk: '' };

  // ---------- Trạng thái AI ----------
  const STATUS_TEXT = { loading: 'Đang kiểm tra AI…', that: 'AI thật', chua_co_key: 'Chưa có API key', het_token: 'AI hết token', key_loi: 'API key lỗi' };
  function setAiState(s) {
    $('aiStatus').setAttribute('data-state', s);
    let text = STATUS_TEXT[s] || s;
    if (s === 'that' && state.info && state.info.model_name) text = 'AI thật · ' + state.info.model_name;
    $('aiStatusText').textContent = text;
    $('aiBanner').hidden = s !== 'chua_co_key';
  }

  async function api(path, body) {
    const opts = body === undefined ? {} : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) };
    const res = await fetch(path, opts);
    let data = null;
    try { data = await res.json(); } catch (e) { data = null; }
    return { ok: res.ok, status: res.status, data: data };
  }

  // ---------- Hiển thị câu trả lời của model: chỉ **đậm** và dòng "- " thành phần tử ----------
  function inlineBold(parent, text) {
    text.split(/\*\*(.+?)\*\*/g).forEach((part, i) => {
      if (part) parent.append(i % 2 === 1 ? h('strong', { text: part }) : document.createTextNode(part));
    });
  }
  function renderModelText(text) {
    const frag = document.createDocumentFragment();
    let ul = null;
    for (const raw of String(text).split(/\r?\n/)) {
      const line = raw.replace(/\s+$/, '');
      if (!line.trim()) { ul = null; continue; }
      const li = /^\s*-\s+(.*)$/.exec(line);
      if (li) {
        if (!ul) { ul = h('ul'); frag.append(ul); }
        const item = h('li'); inlineBold(item, li[1]); ul.append(item);
      } else {
        ul = null;
        const p = h('p'); inlineBold(p, line); frag.append(p);
      }
    }
    return frag;
  }

  // ---------- Tủ áo: thẻ size như mắc áo, vẽ từ kết quả công cụ ----------
  function hangerSvg() {
    const svg = document.createElementNS(SVGNS, 'svg');
    svg.setAttribute('viewBox', '0 0 64 40');
    svg.setAttribute('class', 'hanger');
    svg.setAttribute('aria-hidden', 'true');
    [['M32 4c-3 0-5 2-5 4.5S29 13 32 13v4', '2.2'], ['M32 17 6 34h52L32 17', '2']].forEach((p) => {
      const el = document.createElementNS(SVGNS, 'path');
      el.setAttribute('d', p[0]); el.setAttribute('fill', 'none'); el.setAttribute('stroke', 'currentColor');
      el.setAttribute('stroke-width', p[1]); el.setAttribute('stroke-linecap', 'round'); el.setAttribute('stroke-linejoin', 'round');
      svg.append(el);
    });
    return svg;
  }
  // Size hết: rảnh lại từ mốc sẵn sàng muộn nhất trong các đơn trùng của chính size đó (chỉ để hiển thị).
  function freeAgain(name, orders) {
    let best = '';
    for (const o of orders) {
      if (o.size === name && o.quan_he === 'trung_khoang_giu_hoac_giat' && o.san_sang_lai && o.san_sang_lai > best) best = o.san_sang_lai;
    }
    return best;
  }
  function sizeCard(name, info, orders, i) {
    const st = info.trang_thai;
    const cls = st === 'con' ? 'size-con' : st === 'trung_lich' ? 'size-het' : 'size-xm';
    const card = h('div', { class: 'size-card ' + cls });
    if (!reduceMotion()) { card.classList.add('enter'); card.style.animationDelay = (i * 80) + 'ms'; }
    const tag = h('div', { class: 'tag' }, h('div', { class: 'size-name', text: name }));
    card.append(hangerSvg(), tag);
    if (st === 'con') {
      tag.append(h('div', { class: 'size-state' }, icon('check', 15), 'Còn áo'),
        h('div', { class: 'size-num' }, 'còn ', h('strong', { text: String(info.con_lai) }), ' / ' + info.tong_so));
    } else if (st === 'trung_lich') {
      const free = freeAgain(name, orders);
      tag.append(h('div', { class: 'size-state' }, icon('x', 15), 'Hết'),
        h('div', { class: 'size-when', text: free ? 'Rảnh lại từ ' + fmtShort(free) : 'Đang có đơn giữ áo' }));
    } else {
      tag.append(h('div', { class: 'size-state' }, icon('warn', 15), 'Cần xác minh'));
      if (info.ly_do) tag.append(h('div', { class: 'size-when', text: info.ly_do }));
    }
    return card;
  }
  function wardrobe(kq) {
    if (!kq) return null;
    if (kq.trang_thai !== 'da_kiem_tra') {
      return h('div', { class: 'verify', role: 'alert' }, icon('warn', 22),
        h('div', null,
          h('p', { class: 'verify-title', text: 'Cần chị kiểm tra lại' }),
          h('p', { text: kq.ly_do || 'Dữ liệu chưa đủ để kết luận.' }),
          h('p', { class: 'verify-nudge', text: 'Chị xem lại sổ hoặc Sheet giúp em trước khi hẹn khách nhé.' })));
    }
    const box = h('div', { class: 'wardrobe' });
    if (kq.san_sang_lai) {
      const m = ISO_RE.exec(kq.san_sang_lai);
      box.append(h('p', { class: 'ready' }, (kq.ma_ao || '') + ' · khách trả xong, áo sẵn sàng lại lúc ',
        h('strong', { text: m[4] + ':' + m[5] + ' ngày ' + fmtDMY(kq.san_sang_lai) })));
    }
    const grid = h('div', { class: 'sizes' });
    Object.keys(kq.sizes || {}).forEach((name, i) => grid.append(sizeCard(name, kq.sizes[name], kq.don_lien_quan || [], i)));
    box.append(h('div', { class: 'rail', 'aria-hidden': 'true' }), grid);
    return box;
  }

  // ---------- Các bước trong lúc chờ (chỉ là hiển thị) ----------
  const STEPS = ['Xem lịch thuê', 'Tính thời gian giặt', 'Đối chiếu kho'];
  function stepsBubble() {
    const list = h('ol', { class: 'steps', 'aria-label': 'Đang kiểm tra' });
    STEPS.forEach((s) => list.append(h('li', { class: 'step' }, h('span', { class: 'step-dot', 'aria-hidden': 'true' }), s)));
    return list;
  }
  function markStep(list, i) {
    list.querySelectorAll('.step').forEach((li, j) => {
      li.classList.toggle('is-done', j < i);
      li.classList.toggle('is-active', j === i);
      const dot = li.querySelector('.step-dot');
      if (j < i && !dot.firstChild) dot.append(icon('check', 12));
    });
  }
  async function playSteps(list, done) {
    const pause = reduceMotion() ? 60 : 340;
    for (let i = 0; i < STEPS.length; i++) {
      markStep(list, i);
      await sleep(pause);
      // Bước cuối giữ trạng thái "đang làm" cho tới khi máy chủ trả lời (AI thật có thể mất vài giây).
      if (i === STEPS.length - 1) await done;
    }
    markStep(list, STEPS.length);
  }

  // ---------- Chat ----------
  function chatAppend(node) {
    if (!reduceMotion()) node.classList.add('enter');
    $('chatLog').append(node);
    node.scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'end' });
    return node;
  }

  function traceLine(t) {
    const nf = new Intl.NumberFormat('vi-VN');
    const secs = new Intl.NumberFormat('vi-VN', { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(t.latency_s);
    return [t.model === 'fake' ? 'chưa nối AI (fake)' : (t.model || 'không gọi model'), t.model_calls + ' lần gọi model',
      t.tool_calls + ' lần gọi công cụ', nf.format(t.tokens_in) + '→' + nf.format(t.tokens_out) + ' token', secs + ' s'].join(' · ');
  }

  function answerRow(data) {
    const row = h('div', { class: 'msg-row' });
    const bubble = h('div', { class: 'bubble bubble-ai' });
    bubble.append(renderModelText(data.output));
    const card = wardrobe(data.ket_qua);
    if (card) bubble.append(card);
    row.append(bubble);
    if (data.trace) row.append(h('div', { class: 'meta', text: traceLine(data.trace) }));
    const isFake = data.trace && data.trace.model === 'fake';
    row.append(h('div', { class: 'label-ai', text: isFake
      ? 'Bản chạy thử chưa có AI — câu trả lời do code tạo theo cú pháp cố định'
      : 'AI soạn — chị kiểm tra lại trước khi xác nhận với khách' }));
    return row;
  }

  function errorRow(data) {
    const bubble = h('div', { class: 'bubble bubble-err', role: 'alert' }, h('p', { text: data.error || 'AI gặp lỗi.' }));
    if (['gioi_han_toc_do', 'mang', 'khac', 'server'].indexOf(data.loai) >= 0) {
      bubble.append(h('button', { type: 'button', class: 'btn-ghost', onclick: () => ask(state.lastAsk) }, 'Thử lại'));
    }
    return h('div', { class: 'msg-row' }, bubble);
  }

  function setBusy(on) {
    state.busy = on;
    $('askBtn').disabled = on;
    if (on) $('askBtn').setAttribute('aria-busy', 'true'); else $('askBtn').removeAttribute('aria-busy');
  }

  async function ask(textOverride) {
    if (state.busy) return;
    const text = (textOverride != null ? textOverride : $('askText').value).trim();
    if (!text) { $('askText').focus(); return; }
    state.lastAsk = text;
    if (textOverride == null) { $('askText').value = ''; autoGrow(); }
    const ex = $('examples');
    if (ex) ex.remove();
    chatAppend(h('div', { class: 'msg-row user' }, h('div', { class: 'bubble bubble-user', text: text })));
    const steps = stepsBubble();
    const wait = chatAppend(h('div', { class: 'msg-row' }, h('div', { class: 'bubble bubble-ai bubble-wait' }, steps)));
    setBusy(true);
    const req = api('/api/ask', { text: text });
    try {
      const both = await Promise.all([req, playSteps(steps, req.catch(() => null))]);
      const r = both[0];
      if (!r.data) throw new Error('bad-response');
      if (r.ok) {
        wait.replaceWith(answerRow(r.data));
      } else {
        wait.replaceWith(errorRow(r.data));
        if (['het_token', 'key_loi', 'chua_co_key'].indexOf(r.data.loai) >= 0) setAiState(r.data.loai);
      }
    } catch (e) {
      wait.replaceWith(errorRow({ loai: 'server', error: 'Không kết nối được máy chủ — kiểm tra python webapp/server.py còn chạy.' }));
    } finally {
      setBusy(false);
      const last = $('chatLog').lastElementChild;
      if (last) last.scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'nearest' });
    }
  }

  // Ô nhập tự giãn theo nội dung (tối đa 5 dòng).
  function autoGrow() {
    const el = $('askText');
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 160) + 'px';
  }

  $('askForm').addEventListener('submit', (e) => { e.preventDefault(); ask(); });
  $('askText').addEventListener('input', autoGrow);
  $('askText').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing && e.keyCode !== 229) { e.preventDefault(); ask(); }
  });

  // ---------- Ví dụ: bấm là hỏi ngay ----------
  function renderExamples(real) {
    const row = $('examplesRow');
    row.replaceChildren();
    const list = [
      { q: 'AD02 28/11/2026 29/11/2026', sub: 'Ca thường' },
      { q: 'AD99 28/11/2026 29/11/2026', sub: 'Mã không có trong kho' }
    ];
    if (real) list.push({ q: 'Khách hỏi AD26 ngày 20/11 từ 10h đến 16h còn size nào?', sub: 'Câu tự nhiên' });
    for (const item of list) {
      row.append(h('button', { type: 'button', class: 'ex-btn', onclick: () => ask(item.q) },
        h('span', { class: 'ex-main', text: item.q }), h('span', { class: 'ex-sub', text: item.sub })));
    }
    $('helloHint').textContent = real
      ? 'Chị hỏi tự nhiên cũng được, ví dụ "AD26 ngày 20/11 còn size nào?".'
      : 'Bản này chưa nối AI nên chị gõ theo mẫu: MÃ ÁO ngày nhận ngày trả.';
  }

  // ---------- Badge và chân trang: ghi đúng nguồn dữ liệu và model đang chạy ----------
  function renderDemoNotes(info) {
    const mock = info.data_source === 'mock';
    const fake = info.ai_trang_thai !== 'that';
    $('demoBadge').textContent = 'Bản demo · ' + (mock ? 'dữ liệu giả' : 'dữ liệu thật đã ẩn danh');
    const parts = [mock ? 'dữ liệu giả' : 'dữ liệu thật đã ẩn danh (không có tên, số điện thoại khách)'];
    parts.push(fake ? 'model giả, chưa hiểu câu hỏi tự nhiên' : 'AI ' + (info.model_name || 'thật') + ' soạn câu trả lời');
    parts.push('chưa nối Google Sheet');
    $('footNote').textContent = 'Giới hạn bản demo: ' + parts.join(' · ') + '.';
  }

  // Ảnh trang trí: ảnh không có (clone mới, chưa chạy extract_images.py) thì ẩn khung.
  document.querySelectorAll('.arch img').forEach((img) => {
    img.addEventListener('error', () => { img.closest('.arch').hidden = true; });
  });

  async function init() {
    renderExamples(false);
    try {
      const r = await api('/api/info');
      if (!r.ok || !r.data) throw new Error('info');
      state.info = r.data;
      const real = r.data.ai_trang_thai === 'that';
      setAiState(real ? 'that' : 'chua_co_key');
      renderDemoNotes(r.data);
      renderExamples(real);
      $('askText').placeholder = real ? 'VD: AD26 ngày 20/11 còn size nào?' : 'VD: AD02 28/11/2026 29/11/2026';
    } catch (e) {
      $('aiStatus').setAttribute('data-state', 'key_loi');
      $('aiStatusText').textContent = 'Không kết nối máy chủ';
    }
  }
  init();
})();
