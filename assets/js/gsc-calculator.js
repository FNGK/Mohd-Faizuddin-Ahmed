/* GSC Error Priority Calculator (free-tools/gsc-error-priority-calculator.html).
   Kept as an external file because the site's CSP blocks inline scripts. */
(function () {
  const TOP_N = 10;
  const DEFAULT_PAGE_VALUE = 5;
  const DEFAULT_EFFORT = 5;

  const fileInput = document.getElementById("gscCsvFile");
  const parseStatus = document.getElementById("gscParseStatus");
  const recalcBtn = document.getElementById("gscRecalcBtn");
  const clearBtn = document.getElementById("gscClearBtn");
  const fileNameEl = document.getElementById("gscFileName");
  const resultsWrap = document.getElementById("gscResultsWrap");
  const resultsSummary = document.getElementById("gscResultsSummary");
  const issuesBody = document.getElementById("gscIssuesBody");

  let allIssues = [];

  function setFileName(name) {
    if (!fileNameEl) return;
    if (name) {
      fileNameEl.textContent = name;
      fileNameEl.classList.add("gsc-file-picker__name--chosen");
    } else {
      fileNameEl.textContent = "No file chosen";
      fileNameEl.classList.remove("gsc-file-picker__name--chosen");
    }
  }

  const IMPACT_RULES = [
    { re: /manual action|security|hacked|malware/i, score: 10 },
    { re: /5\d\d|server error|internal error/i, score: 9 },
    { re: /noindex|blocked by robots|forbidden|403/i, score: 9 },
    { re: /404|not found|soft 404/i, score: 8 },
    { re: /canonical|duplicate|alternate page/i, score: 7 },
    { re: /redirect|redirected/i, score: 6 },
    { re: /crawled.*not indexed/i, score: 6 },
    { re: /discovered.*not indexed/i, score: 5 },
    { re: /indexed/i, score: 3 }
  ];

  function clampScore(n) {
    return Math.min(10, Math.max(1, Math.round(n)));
  }

  function suggestImpact(label) {
    for (let i = 0; i < IMPACT_RULES.length; i += 1) {
      if (IMPACT_RULES[i].re.test(label)) return IMPACT_RULES[i].score;
    }
    return 6;
  }

  function priorityScore(impact, pageValue, volume, effort) {
    return impact * 0.45 + pageValue * 0.35 + volume * 0.2 - effort * 0.3;
  }

  function priorityLabel(score) {
    if (score >= 6.5) return { text: "Critical", cls: "priority-pill--critical" };
    if (score >= 4.5) return { text: "High", cls: "priority-pill--high" };
    if (score >= 3) return { text: "Moderate", cls: "priority-pill--moderate" };
    return { text: "Low", cls: "priority-pill--low" };
  }

  function volumeFromCount(count, maxCount) {
    if (maxCount <= 1) return clampScore(count);
    const ratio = count / maxCount;
    return clampScore(ratio * 9 + 1);
  }

  function normalizeHeader(h) {
    return String(h || "")
      .replace(/^\uFEFF/, "")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  function parseCSV(text) {
    const rows = [];
    let row = [];
    let field = "";
    let inQuotes = false;
    for (let i = 0; i < text.length; i += 1) {
      const ch = text[i];
      const next = text[i + 1];
      if (inQuotes) {
        if (ch === '"' && next === '"') {
          field += '"';
          i += 1;
        } else if (ch === '"') {
          inQuotes = false;
        } else {
          field += ch;
        }
      } else if (ch === '"') {
        inQuotes = true;
      } else if (ch === ",") {
        row.push(field);
        field = "";
      } else if (ch === "\n" || (ch === "\r" && next === "\n")) {
        row.push(field);
        field = "";
        if (row.some(function (c) { return String(c).trim() !== ""; })) {
          rows.push(row);
        }
        row = [];
        if (ch === "\r") i += 1;
      } else if (ch !== "\r") {
        field += ch;
      }
    }
    row.push(field);
    if (row.some(function (c) { return String(c).trim() !== ""; })) {
      rows.push(row);
    }
    return rows;
  }

  function findColumn(headers, candidates) {
    for (let c = 0; c < candidates.length; c += 1) {
      const want = candidates[c];
      const idx = headers.indexOf(want);
      if (idx !== -1) return idx;
    }
    for (let h = 0; h < headers.length; h += 1) {
      const label = headers[h];
      for (let c = 0; c < candidates.length; c += 1) {
        if (label.indexOf(candidates[c]) !== -1) return h;
      }
    }
    return -1;
  }

  function parseGscCsv(text) {
    const rows = parseCSV(text.replace(/^\uFEFF/, ""));
    if (rows.length < 2) {
      throw new Error("CSV needs a header row and at least one data row.");
    }
    const headers = rows[0].map(normalizeHeader);
    const urlIdx = findColumn(headers, ["url", "page", "address", "target page", "page url"]);
    const issueIdx = findColumn(headers, [
      "reason",
      "issue",
      "status",
      "indexing",
      "indexing state",
      "coverage state",
      "state",
      "problem",
      "type",
      "category",
      "page indexing"
    ]);
    const countIdx = findColumn(headers, ["pages", "page count", "affected", "items", "count", "urls", "number of pages"]);

    const groups = Object.create(null);

    function addIssue(label, url, explicitCount) {
      const key = label.trim();
      if (!key) return;
      if (!groups[key]) {
        groups[key] = { label: key, urls: [], count: 0 };
      }
      if (explicitCount != null && !isNaN(explicitCount)) {
        groups[key].count = Math.max(groups[key].count, explicitCount);
      } else if (url) {
        groups[key].urls.push(url);
        groups[key].count += 1;
      } else {
        groups[key].count += 1;
      }
    }

    const summaryMode = issueIdx !== -1 && countIdx !== -1 && urlIdx === -1;

    for (let r = 1; r < rows.length; r += 1) {
      const cells = rows[r];
      if (!cells.length) continue;

      if (summaryMode) {
        const label = cells[issueIdx] || "Unknown issue";
        const n = parseInt(String(cells[countIdx] || "").replace(/,/g, ""), 10);
        addIssue(label, null, isNaN(n) ? 1 : n);
        continue;
      }

      let label = issueIdx !== -1 ? cells[issueIdx] : "";
      const url = urlIdx !== -1 ? (cells[urlIdx] || "").trim() : "";

      if (!label && urlIdx !== -1 && headers[urlIdx]) {
        label = "Unspecified";
      }
      if (!label && issueIdx === -1 && url) {
        label = "URL row (no reason column)";
      }
      if (!label) continue;

      if (countIdx !== -1 && !url) {
        const n = parseInt(String(cells[countIdx] || "").replace(/,/g, ""), 10);
        addIssue(label, null, isNaN(n) ? 1 : n);
      } else {
        addIssue(label, url || null, null);
      }
    }

    const list = Object.keys(groups).map(function (key) {
      const g = groups[key];
      const urlSet = {};
      g.urls.forEach(function (u) {
        if (u) urlSet[u] = true;
      });
      const uniqueUrls = Object.keys(urlSet);
      const count = uniqueUrls.length > 0 ? uniqueUrls.length : g.count;
      return {
        label: g.label,
        urlCount: count,
        urls: uniqueUrls.slice(0, 50),
        impact: suggestImpact(g.label),
        pageValue: DEFAULT_PAGE_VALUE,
        effort: DEFAULT_EFFORT
      };
    });

    if (!list.length) {
      throw new Error("Could not detect issue/reason columns. Export from Page indexing with URL + reason, or an issue summary with Pages count.");
    }

    return { issues: list, headers: headers, summaryMode: summaryMode };
  }

  function setStatus(msg, ok) {
    parseStatus.textContent = msg;
    parseStatus.className = "gsc-meta" + (ok === true ? " gsc-meta--ok" : ok === false ? " gsc-meta--err" : "");
  }

  function renderTable(showList) {
    const maxCount = Math.max.apply(
      null,
      showList.map(function (i) { return i.urlCount; })
    );
    issuesBody.innerHTML = "";
    showList.forEach(function (issue, index) {
      const vol = volumeFromCount(issue.urlCount, maxCount);
      const score = Math.max(0, priorityScore(issue.impact, issue.pageValue, vol, issue.effort));
      const band = priorityLabel(score);
      const tr = document.createElement("tr");
      tr.dataset.issueKey = issue.label;

      const sampleHtml =
        issue.urls.length > 0
          ? "<details><summary>Sample URLs (" +
            Math.min(issue.urls.length, 20) +
            ")</summary><ul class=\"gsc-url-list\">" +
            issue.urls
              .slice(0, 20)
              .map(function (u) {
                return "<li>" + escapeHtml(u) + "</li>";
              })
              .join("") +
            "</ul></details>"
          : "";

      tr.innerHTML =
        "<td>" +
        (index + 1) +
        "</td>" +
        "<td><strong>" +
        escapeHtml(issue.label) +
        "</strong>" +
        sampleHtml +
        "</td>" +
        "<td>" +
        issue.urlCount.toLocaleString() +
        "</td>" +
        '<td><input type="number" min="1" max="10" value="' +
        issue.impact +
        '" data-field="impact" aria-label="Impact for ' +
        escapeHtml(issue.label) +
        '"></td>' +
        '<td><input type="number" min="1" max="10" value="' +
        issue.pageValue +
        '" data-field="pageValue" aria-label="Page value for ' +
        escapeHtml(issue.label) +
        '"></td>' +
        '<td><input type="number" min="1" max="10" value="' +
        issue.effort +
        '" data-field="effort" aria-label="Effort for ' +
        escapeHtml(issue.label) +
        '"></td>' +
        "<td>" +
        vol +
        "</td>" +
        "<td data-score>" +
        score.toFixed(2) +
        "</td>" +
        '<td><span class="priority-pill ' +
        band.cls +
        '" data-label>' +
        band.text +
        "</span></td>";

      issuesBody.appendChild(tr);
    });

    issuesBody.querySelectorAll("input[data-field]").forEach(function (input) {
      input.addEventListener("change", syncFromTable);
      input.addEventListener("input", syncFromTable);
    });
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function syncFromTable() {
    const rows = issuesBody.querySelectorAll("tr");
    rows.forEach(function (tr) {
      const key = tr.dataset.issueKey;
      const issue = allIssues.find(function (i) { return i.label === key; });
      if (!issue) return;
      issue.impact = clampScore(tr.querySelector('[data-field="impact"]').value);
      issue.pageValue = clampScore(tr.querySelector('[data-field="pageValue"]').value);
      issue.effort = clampScore(tr.querySelector('[data-field="effort"]').value);
    });
    const ranked = rankIssues(allIssues);
    const top = ranked.slice(0, TOP_N);
    renderTable(top);
    updateSummary(allIssues.length, top.length);
  }

  function rankIssues(list) {
    const maxCount = Math.max.apply(
      null,
      list.map(function (i) { return i.urlCount; })
    );
    return list
      .slice()
      .map(function (issue) {
        const vol = volumeFromCount(issue.urlCount, maxCount);
        const score = Math.max(0, priorityScore(issue.impact, issue.pageValue, vol, issue.effort));
        return { issue: issue, score: score };
      })
      .sort(function (a, b) {
        return b.score - a.score;
      })
      .map(function (x) {
        return x.issue;
      });
  }

  function updateSummary(totalIssues, shown) {
    resultsSummary.textContent =
      "Found " +
      totalIssues +
      " unique issue" +
      (totalIssues === 1 ? "" : "s") +
      ". Showing top " +
      shown +
      " by priority score. Edit impact, page value, or effort — scores update live.";
  }

  function runAnalysis() {
    const ranked = rankIssues(allIssues);
    const top = ranked.slice(0, TOP_N);
    renderTable(top);
    resultsWrap.hidden = false;
    updateSummary(allIssues.length, top.length);
    recalcBtn.disabled = false;
    clearBtn.disabled = false;
  }

  function loadCsvText(text, fileLabel) {
    try {
      const parsed = parseGscCsv(String(text || ""));
      allIssues = parsed.issues;
      const mode = parsed.summaryMode ? "issue summary" : "per-URL";
      setStatus(
        (fileLabel ? fileLabel + " — " : "") +
          "Parsed " +
          allIssues.length +
          " issues (" +
          mode +
          " format). Columns: " +
          parsed.headers.slice(0, 6).join(", ") +
          (parsed.headers.length > 6 ? "…" : ""),
        true
      );
      runAnalysis();
    } catch (err) {
      allIssues = [];
      resultsWrap.hidden = true;
      recalcBtn.disabled = true;
      clearBtn.disabled = true;
      setStatus(err.message || "Could not parse CSV.", false);
    }
  }

  if (fileInput) {
    fileInput.addEventListener("change", function () {
      const file = fileInput.files && fileInput.files[0];
      if (!file) {
        setFileName("");
        return;
      }
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = function () {
        loadCsvText(reader.result, file.name);
      };
      reader.onerror = function () {
        setStatus("Failed to read file.", false);
      };
      reader.readAsText(file);
    });
  }

  if (recalcBtn) {
    recalcBtn.addEventListener("click", function () {
      syncFromTable();
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      allIssues = [];
      fileInput.value = "";
      setFileName("");
      issuesBody.innerHTML = "";
      resultsWrap.hidden = true;
      recalcBtn.disabled = true;
      clearBtn.disabled = true;
      setStatus("Upload a file to analyze your top 10 issues.", null);
    });
  }

  const form = document.getElementById("gscCalcForm");
  const result = document.getElementById("priorityResult");
  if (form && result) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      const impact = Number(document.getElementById("impact").value || 0);
      const pageValue = Number(document.getElementById("pageValue").value || 0);
      const issueVolume = Number(document.getElementById("issueVolume").value || 0);
      const effort = Number(document.getElementById("effort").value || 0);
      const score = priorityScore(impact, pageValue, issueVolume, effort);
      const rounded = Math.max(0, score).toFixed(2);
      const band = priorityLabel(score);
      result.innerHTML =
        "<strong>Priority score:</strong> " +
        rounded +
        ' (<span class="priority-pill ' +
        band.cls +
        '">' +
        band.text +
        "</span>).";
    });
  }
})();
