/* Logic trang: gọi API, vẽ bảng. Không có kết quả nào viết sẵn ở đây; mọi số lấy từ /api/*. */
(function () {
  'use strict';

  var LABEL = { dat: 'Đạt', mot_phan: 'Đạt một phần', truot: 'Trượt', chua_ho_tro: 'Chưa hỗ trợ', can_chot: 'Cần Nam chốt' };
  var SEV_CLASS = { 'Cao': 'cao', 'Trung bình': 'trung_binh', 'Thấp': 'thap' };
  var VIA = { agent: 'qua agent', tool: 'gọi thẳng công cụ', file: 'đọc file' };
  var CLIP_LINES = 10; /* output đầy đủ của agent là 9 dòng: hiện trọn, không giấu dòng size */
  var state = { bugs: [] };

  function $(sel, root) { return (root || document).querySelector(sel); }
  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'text') node.textContent = attrs[k];
      else if (k === 'class') node.className = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function clock(iso) {
    var d = iso ? new Date(iso) : new Date();
    return pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
  }
  function getJSON(url) {
    return fetch(url, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
  }
  function tag(status, label) { return el('span', { class: 'tag tag--' + status, text: label || LABEL[status] }); }

  /* khối văn bản mono, cắt gọn 6 dòng kèm "Xem đủ" */
  function textBlock(text, tagName) {
    var wrap = el('div', { class: 'cell-text' });
    var lines = String(text).split('\n');
    var long = lines.length > CLIP_LINES;
    var shown = long ? lines.slice(0, CLIP_LINES).join('\n') + '\n…' : text;
    wrap.appendChild(el(tagName || 'pre', { text: shown }));
    if (long) {
      var det = el('details');
      det.appendChild(el('summary', { text: 'Xem đủ' }));
      det.appendChild(el('pre', { text: text }));
      wrap.appendChild(det);
    }
    return wrap;
  }

  function td(label, children, cls) {
    var cell = el('td', { 'data-label': label, class: 'cell' + (cls ? ' ' + cls : '') }, children);
    return cell;
  }

  function makeTable(caption, cols, headers, bodyCls) {
    var table = el('table', { class: 'res ' + (bodyCls || '') });
    table.appendChild(el('caption', { class: 'visually-hidden', text: caption }));
    var cg = el('colgroup');
    cols.forEach(function (c) { cg.appendChild(el('col', { class: c })); });
    table.appendChild(cg);
    var tr = el('tr');
    headers.forEach(function (h) { tr.appendChild(el('th', { scope: 'col', text: h })); });
    table.appendChild(el('thead', {}, [tr]));
    return table;
  }

  function caseRow(c, index) {
    var tr = el('tr', c.status === 'can_chot' ? { class: 'is-chot' } : {});
    tr.appendChild(td('#', [el('span', { text: c.id })]));
    tr.appendChild(td('Ca', [el('span', { text: c.title })]));
    var inCell = td('Input', [textBlock(c.input, 'code')]);
    inCell.appendChild(el('span', { class: 'via', text: (VIA[c.via] || c.via) + ' · ' + c.data_note }));
    tr.appendChild(inCell);
    var ex = td('Kỳ vọng', [el('span', { text: c.expected })]);
    if (c.status === 'can_chot') ex.appendChild(el('p', { class: 'q', text: 'Câu hỏi cho Nam: ' + c.expected }));
    tr.appendChild(ex);
    tr.appendChild(td('Kết quả thực tế', [textBlock(c.actual, 'pre')]));
    var st = td('Đánh giá', [tag(c.status, c.status_label)]);
    if (c.note) st.appendChild(el('p', { class: 'note', text: c.note }));
    tr.appendChild(st);
    return tr;
  }

  function renderCases(container, cases, groupKey) {
    container.textContent = '';
    var table = makeTable('Kết quả các ca thử',
      ['col-n', 'col-case', 'col-in', 'col-ex', 'col-act', 'col-st'],
      ['#', 'Ca', 'Input', 'Kỳ vọng', 'Kết quả thực tế', 'Đánh giá']);
    var body = el('tbody');
    var last = null;
    cases.forEach(function (c, i) {
      if (c.nhom !== last) {
        last = c.nhom;
        var gr = el('tr', { class: 'grouprow' });
        gr.appendChild(el('th', { colspan: '6', scope: 'colgroup', text: c.nhom }));
        body.appendChild(gr);
      }
      body.appendChild(caseRow(c, i));
    });
    table.appendChild(body);
    container.appendChild(table);
  }

  function summary(cases, ranAt) {
    var ok = cases.filter(function (c) { return c.status === 'dat'; }).length;
    var line = ok + '/' + cases.length + ' đạt · chạy lúc ' + clock(ranAt);
    var chot = cases.filter(function (c) { return c.status === 'can_chot'; }).length;
    if (chot) line += ' · ' + chot + ' ca cần Nam chốt';
    return line;
  }

  function renderBugs(bugs) {
    var box = $('#tbl-loi');
    box.textContent = '';
    var table = makeTable('Danh sách lỗi theo mẫu Input, Kỳ vọng, Kết quả thực tế, Mức độ ảnh hưởng',
      ['col-n', 'col-in', 'col-ex', 'col-act', 'col-imp', 'col-st'],
      ['#', 'Input', 'Kỳ vọng', 'Kết quả thực tế', 'Mức độ ảnh hưởng', 'Trạng thái'], 'bugs');
    var body = el('tbody');
    bugs.forEach(function (b) {
      var tr = el('tr', b.status === 'Đã hết lỗi' ? { class: 'is-fixed' } : {});
      tr.appendChild(td('#', [el('span', { text: String(b.n) })]));
      tr.appendChild(td('Input', [textBlock(b.input, 'code')]));
      tr.appendChild(td('Kỳ vọng', [el('span', { text: b.expected })]));
      tr.appendChild(td('Kết quả thực tế', [textBlock(b.actual, 'pre')]));
      var imp = td('Mức độ ảnh hưởng', [tag(SEV_CLASS[b.severity] || 'thap', b.severity)]);
      imp.appendChild(el('p', { class: 'imp', text: b.impact }));
      tr.appendChild(imp);
      tr.appendChild(td('Trạng thái', [tag(b.status === 'Đã hết lỗi' ? 'dat' : 'truot', b.status)]));
      body.appendChild(tr);
    });
    table.appendChild(body);
    box.appendChild(table);
    var open = bugs.filter(function (b) { return b.status === 'Còn lỗi'; });
    function n(sev) { return open.filter(function (b) { return b.severity === sev; }).length; }
    $('#sum-loi').textContent = open.length + ' lỗi còn mở: ' + n('Cao') + ' Cao, ' + n('Trung bình') + ' Trung bình, ' + n('Thấp') + ' Thấp';
  }

  function loadCases() {
    var running = 'Đang chạy ca thử…';
    ['#sum-yeu-cau', '#sum-quy-tac', '#sum-loi'].forEach(function (s) { $(s).textContent = running; });
    document.querySelectorAll('[data-rerun], #nav-run').forEach(function (b) { b.setAttribute('aria-busy', 'true'); });
    return getJSON('/api/cases').then(function (data) {
      var byId = {};
      data.groups.forEach(function (g) { byId[g.id] = g; });
      renderCases($('#tbl-yeu-cau'), byId.yeu_cau.cases);
      renderCases($('#tbl-quy-tac'), byId.quy_tac.cases);
      $('#sum-yeu-cau').textContent = summary(byId.yeu_cau.cases, data.ran_at);
      $('#sum-quy-tac').textContent = summary(byId.quy_tac.cases, data.ran_at);
      state.bugs = data.bugs;
      renderBugs(data.bugs);
    }).catch(function (err) {
      ['#sum-yeu-cau', '#sum-quy-tac', '#sum-loi'].forEach(function (s) {
        $(s).textContent = 'Không chạy được ca thử: ' + err.message + '. Kiểm tra server còn chạy không.';
      });
    }).then(function () {
      document.querySelectorAll('[data-rerun], #nav-run').forEach(function (b) { b.removeAttribute('aria-busy'); });
    });
  }

  /* ---- thông tin commit ---- */
  function loadInfo() {
    getJSON('/api/info').then(function (i) {
      var parts = ['Bản chạy thử CP2', 'nhánh ' + (i.branch || 'không rõ'), 'commit ' + (i.commit || 'không rõ')];
      if (i.behind_main === 0) parts.push('khớp main');
      else if (i.behind_main > 0) parts.push('chậm ' + i.behind_main + ' commit so với main');
      else parts.push('chưa so được với main');
      if (i.dirty) parts.push('có thay đổi chưa commit');
      $('#fact-line').textContent = parts.join(' · ');
      if (i.commit_subject) $('#fact-line').setAttribute('title', i.commit_subject);
    }).catch(function () {
      $('#fact-line').textContent = 'Bản chạy thử CP2 · không đọc được thông tin commit';
    });
  }

  /* ---- sao chép bảng lỗi ---- */
  function mdCell(s) { return String(s).replace(/\|/g, '\\|').replace(/\r?\n/g, '<br>'); }
  function bugsMarkdown(bugs) {
    var rows = ['| Input | Kỳ vọng | Kết quả thực tế | Mức độ ảnh hưởng |', '| --- | --- | --- | --- |'];
    bugs.forEach(function (b) {
      rows.push('| ' + [b.input, b.expected, b.actual, b.severity + ': ' + b.impact].map(mdCell).join(' | ') + ' |');
    });
    return rows.join('\n');
  }
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve, reject) {
      var ta = el('textarea', { 'aria-hidden': 'true', style: 'position:fixed;left:-9999px;top:0' });
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      ok ? resolve() : reject(new Error('trình duyệt chặn sao chép'));
    });
  }
  $('#copy-bugs').addEventListener('click', function () {
    var status = $('#copy-status');
    if (!state.bugs.length) { status.textContent = 'Chưa có danh sách lỗi để chép.'; return; }
    copyText(bugsMarkdown(state.bugs)).then(function () {
      status.textContent = 'Đã chép ' + state.bugs.length + ' dòng';
    }).catch(function (e) { status.textContent = 'Không chép được: ' + e.message; });
  });

  /* ---- form tra lịch ---- */
  var fMa = $('#f-ma'), fNhan = $('#f-nhan'), fTra = $('#f-tra'), fRaw = $('#f-raw');
  function composed() {
    if (fRaw.value.trim()) return fRaw.value;
    return [fMa.value.trim(), fNhan.value.trim(), fTra.value.trim()].join(' ');
  }
  function refreshSent() { $('#sent-text').textContent = composed(); }
  [fMa, fNhan, fTra, fRaw].forEach(function (f) { f.addEventListener('input', refreshSent); });
  refreshSent();

  function renderSizes(output) {
    var ul = $('#lookup-sizes');
    ul.textContent = '';
    var re = /^- Size (\S+?): (.*)$/gm, m, any = false;
    while ((m = re.exec(output))) {
      any = true;
      var li = el('li', {}, [el('span', { class: 'rows__name', text: 'Size ' + m[1] }), el('span', { class: 'rows__value', text: m[2] })]);
      ul.appendChild(li);
    }
    ul.hidden = !any;
  }

  $('#lookup-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var status = $('#lookup-status');
    status.textContent = 'Đang tra…';
    fetch('/api/answer', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: composed() })
    }).then(function (r) { return r.json(); }).then(function (data) {
      var box = $('#lookup-result');
      box.hidden = false;
      if (data.error) {
        $('#lookup-pre').textContent = 'Lỗi từ code: ' + data.error;
        renderSizes('');
        status.textContent = 'Agent báo lỗi, xem khối bên dưới.';
        return;
      }
      $('#lookup-pre').textContent = data.output;
      renderSizes(data.output);
      status.textContent = 'Đã tra xong.';
    }).catch(function (err) {
      status.textContent = 'Không gọi được server: ' + err.message;
    });
  });

  /* ---- demo ---- */
  var OPEN_ID = { thuong: '#demo-thuong', xac_minh: '#demo-xac-minh' };
  document.querySelectorAll('[data-demo]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var key = btn.getAttribute('data-demo');
      var out = $(OPEN_ID[key] + ' .demo-out');
      out.textContent = 'Đang chạy…';
      getJSON('/api/demo?which=' + encodeURIComponent(key)).then(function (data) {
        var c = data.cases[0];
        out.textContent = '';
        out.appendChild(el('pre', { text: c.actual }));
        out.appendChild(el('div', {}, [tag(c.status, c.status_label)]));
      }).catch(function (err) { out.textContent = 'Không chạy được: ' + err.message; });
    });
  });

  /* ---- chạy lại ---- */
  document.querySelectorAll('[data-rerun]').forEach(function (b) { b.addEventListener('click', loadCases); });
  $('#nav-run').addEventListener('click', function () { loadCases(); });

  loadInfo();
  loadCases();
})();
