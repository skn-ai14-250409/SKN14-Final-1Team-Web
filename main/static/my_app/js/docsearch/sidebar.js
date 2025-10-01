(() => {
  "use strict";

  const onReady = (fn) => {
    if (document.readyState === "loading")
      document.addEventListener("DOMContentLoaded", fn);
    else fn();
  };

  onReady(() => {
    // DOM refs
    const $ = (id) => document.getElementById(id);
    const root = $("docSearchSidebar");
    if (!root) return console.warn("[docsearch] root not found");

    const els = {
      input: $("docSearchInput"),
      btn: $("docSearchBtn"),
      status: $("docSearchStatus"),
      results: $("docSearchResults"),
      count: $("docSearchCount"),
      k: $("resultCount"),
      kValue: $("kValue"),
      copyAll: $("copyAllBtn"),
    };

    // Endpoint
    const getEndpoint = () => {
      const raw = (root.dataset.endpoint || "").trim();
      if (raw) return new URL(raw, window.location.origin).toString();
      const seg1 = window.location.pathname.split("/")[1] || "";
      const path = `/${seg1 ? seg1 + "/" : ""}api/docsearch/`;
      return new URL(path, window.location.origin).toString();
    };
    const ENDPOINT = getEndpoint();
    console.info("[docsearch] endpoint:", ENDPOINT);

    // Utils
    const debounce = (fn, ms = 300) => {
      let t;
      return (...a) => {
        clearTimeout(t);
        t = setTimeout(() => fn(...a), ms);
      };
    };
    const setStatus = (msg) => {
      if (els.status) els.status.textContent = msg || "";
    };

    // Render
    function renderResults(items) {
      els.results.innerHTML = "";
      if (!items || items.length === 0) {
        setStatus("결과 없음");
        els.count.textContent = "0건";
        return;
      }
      setStatus("");
      els.count.textContent = `${items.length}건`;

      const frag = document.createDocumentFragment();

      items.forEach((it) => {
        const li = document.createElement("li");

        // 제목
        let titleText =
          (it.title && it.title.trim()) ||
          (it.source ? new URL(it.source).hostname : "문서");
        titleText = titleText
          .replace(/\.txt$/i, "")
          .replace(/\_hl=ko$/i, "")
          .replace(/(?:^|[_-])(hl|lang)=[a-z-]+$/i, "");

        const h4 = document.createElement("h4");
        h4.className = "result-title";

        const titleLink = document.createElement("a");
        titleLink.href = it.source || "#";
        titleLink.target = "_blank";
        titleLink.rel = "noopener noreferrer";
        titleLink.textContent = titleText;

        h4.appendChild(titleLink);

        // 메타
        const meta = document.createElement("div");
        meta.className = "result-meta";

        const urlSpan = document.createElement("span");
        urlSpan.className = "result-url";
        urlSpan.textContent = it.source || "(no url)";
        meta.appendChild(urlSpan);

        li.appendChild(h4);
        li.appendChild(meta);
        frag.appendChild(li);
      });

      els.results.appendChild(frag);
    }

    // Search
    let controller = null;

    async function doSearch(q) {
      if (!q || q.trim() === "") {
        setStatus("검색 대기 중…");
        els.results.innerHTML = "";
        els.count.textContent = "0건";
        return;
      }

      if (controller) controller.abort();
      controller = new AbortController();

      setStatus("검색 중…");
      els.results.innerHTML = "";

      try {
        const url = new URL(ENDPOINT);
        const k = parseInt(els.k?.value || "10", 10);
        url.searchParams.set("q", q);
        url.searchParams.set("k", String(k));

        const res = await fetch(url.toString(), {
          method: "GET",
          headers: { Accept: "application/json" },
          credentials: "same-origin",
          signal: controller.signal,
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        renderResults(data.results);
        els.count.textContent = `${data.results.length}건`;
      } catch (err) {
        if (err.name === "AbortError") return;
        console.error("[docsearch]", err);
        setStatus("검색 오류가 발생했어요.");
      }
    }

    // Events
    const runSearch = debounce(() => doSearch(els.input?.value), 300);

    // 폼 새로고침 방지
    const parentForm = els.btn?.closest("form");
    if (parentForm)
      parentForm.addEventListener("submit", (e) => {
        e.preventDefault();
        doSearch(els.input?.value);
      });
    els.btn?.setAttribute("type", "button");

    els.btn?.addEventListener("click", (e) => {
      e.preventDefault();
      doSearch(els.input?.value);
    });
    els.input?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        doSearch(els.input.value);
      }
    });
    els.input?.addEventListener("input", runSearch);

    // 슬라이더 값 변경 이벤트 (k 표시 + 즉시 검색)
    els.k?.addEventListener("input", () => {
      const val = els.k.value;
      if (els.kValue) els.kValue.textContent = val;
    });
    els.k?.addEventListener("change", () => doSearch(els.input?.value));

    // URL 복사
    els.copyAll?.addEventListener("click", async () => {
      const links = Array.from(els.results.querySelectorAll("a"))
        .map((a) => a.href)
        .join("\n");
      try {
        await navigator.clipboard.writeText(links);
        setStatus("URL들을 클립보드에 복사했어요.");
      } catch {
        setStatus("복사 실패. 수동으로 선택해 주세요.");
      }
    });

    const layout = document.querySelector(".layout");
    const sidebar = document.getElementById("docSearchSidebar");
    const toggleBtn = document.getElementById("toggleSidebarBtn");

    toggleBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
         <polyline points="9 18 15 12 9 6" />
       </svg>`;

    toggleBtn.addEventListener("click", () => {
      layout.classList.toggle("sidebar-closed");
      sidebar.classList.toggle("closed");

      toggleBtn.innerHTML = layout.classList.contains("sidebar-closed")
        ? `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
         <polyline points="15 18 9 12 15 6" />
       </svg>`
        : `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
         <polyline points="9 18 15 12 9 6" />
       </svg>`;
    });
  });
})();
