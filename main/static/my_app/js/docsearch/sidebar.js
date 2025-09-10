(() => {
  'use strict';

  const onReady = (fn) => {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  };

  onReady(() => {
    // DOM refs
    const $ = (id) => document.getElementById(id);
    const root = $('docSearchSidebar');
    if (!root) return console.warn('[docsearch] root not found');

    const els = {
      input: $('docSearchInput'),
      btn: $('docSearchBtn'),
      status: $('docSearchStatus'),
      results: $('docSearchResults'),
      count: $('docSearchCount'),
      th: $('similarityThreshold'),
      copyAll: $('copyAllBtn'),
    };

    // Endpoint (절대 URL)
    const getEndpoint = () => {
      // 1) 템플릿에서 주입된 경로 사용 ex) "/main/api/docsearch/"
      const raw = (root.dataset.endpoint || '').trim();
      if (raw) return new URL(raw, window.location.origin).toString();

      // 2) 주입이 없으면 현재 경로의 첫 세그먼트 기준으로 추론
      const seg1 = window.location.pathname.split('/')[1] || '';
      const path = `/${seg1 ? seg1 + '/' : ''}api/docsearch/`;
      return new URL(path, window.location.origin).toString();
    };
    const ENDPOINT = getEndpoint();
    console.info('[docsearch] endpoint:', ENDPOINT);

    // Utils
    const debounce = (fn, ms = 300) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
    const setStatus = (msg) => { if (els.status) els.status.textContent = msg || ''; };

    // Render
    function renderResults(items) {
      els.results.innerHTML = '';
      if (!items || items.length === 0) {
        setStatus('결과 없음');
        els.count.textContent = '0건';
        return;
      }
      setStatus('');
      els.count.textContent = `${items.length}건`;

      const frag = document.createDocumentFragment();

      items.forEach((it) => {
        const li = document.createElement('li');

        // 제목
        let titleText =
        (it.title && it.title.trim()) ||
        (it.source ? new URL(it.source).hostname : '문서');
        titleText = titleText.replace(/\.txt$/i, '');
        titleText = titleText.replace(/\_hl=ko$/i, '');
        titleText = titleText.replace(/(?:^|[_-])(hl|lang)=[a-z-]+$/i, '');

        const h4 = document.createElement('h4');
        h4.className = 'result-title';

        const titleLink = document.createElement('a');
        titleLink.href = it.source || '#';
        titleLink.target = '_blank';
        titleLink.rel = 'noopener noreferrer';
        titleLink.textContent = titleText;

        h4.appendChild(titleLink);

        // 메타: 원본 URL + 점수 배지
        const meta = document.createElement('div');
        meta.className = 'result-meta';

        const urlSpan = document.createElement('span');
        urlSpan.className = 'result-url';
        urlSpan.textContent = it.source || '(no url)';
        meta.appendChild(urlSpan);

        if (typeof it.score === 'number') {
        const score = document.createElement('span');
        score.className = 'score-badge';
        score.title = 'similarity score';
        score.textContent = it.score.toFixed(3);
        meta.appendChild(score);
        }

        li.appendChild(h4);
        li.appendChild(meta);
        frag.appendChild(li);
    });

      els.results.appendChild(frag);
    }

    // Search
    let controller = null;

    async function doSearch(q) {
      if (!q || q.trim() === '') {
        setStatus('검색 대기 중…');
        els.results.innerHTML = '';
        els.count.textContent = '0건';
        return;
      }

      // 이전 요청 취소
      if (controller) controller.abort();
      controller = new AbortController();

      setStatus('검색 중…');
      els.results.innerHTML = '';

      const thresh = parseFloat(els.th?.value || '0.6');

      try {
        const url = new URL(ENDPOINT);
        url.searchParams.set('q', q);
        url.searchParams.set('threshold', String(thresh));

        const res = await fetch(url.toString(), {
          method: 'GET',
          headers: { 'Accept': 'application/json' },
          credentials: 'same-origin',
          signal: controller.signal,
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        renderResults(data.results);  // 먼저 렌더(비면 '결과 없음' 찍힘)
        if ((!Array.isArray(data.results) || data.results.length === 0) && data.warning) {
        setStatus(String(data.warning)); // 경고로 덮어쓰기
        } else if (!data.warning) {
        setStatus(''); // 경고 없으면 빈 상태
        }
      } catch (err) {
        if (err.name === 'AbortError') return; // 사용자가 재검색해서 취소된 경우
        console.error('[docsearch]', err);
        setStatus('검색 오류가 발생했어요.');
      }
    }

    // Events
    const runSearch = debounce(() => doSearch(els.input?.value), 300);

    // 폼 새로고침 방지
    const parentForm = els.btn?.closest('form');
    if (parentForm) parentForm.addEventListener('submit', (e) => { e.preventDefault(); doSearch(els.input?.value); });
    els.btn?.setAttribute('type', 'button');

    els.btn?.addEventListener('click', (e) => { e.preventDefault(); doSearch(els.input?.value); });
    els.input?.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); doSearch(els.input.value); }});
    els.input?.addEventListener('input', runSearch);
    els.th?.addEventListener('change', () => doSearch(els.input?.value));
    els.copyAll?.addEventListener('click', async () => {
      const links = Array.from(els.results.querySelectorAll('a')).map(a => a.href).join('\n');
      try { await navigator.clipboard.writeText(links); setStatus('URL들을 클립보드에 복사했어요.'); }
      catch { setStatus('복사 실패. 수동으로 선택해 주세요.'); }
    });
  });
})();
