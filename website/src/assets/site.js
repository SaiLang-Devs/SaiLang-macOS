/* SaiLang website scripts. No external libraries, and nothing is sent to a server. */
(function () {
  "use strict";

  function escapeHtml(text) {
    return text.replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ----- search ------------------------------------------------------------
  // Matches a term exactly, or with a trailing "s" removed from either side,
  // so "chapters" finds "chapter" and "downloads" finds "download".
  function termVariants(term) {
    var variants = [term];
    if (term.length > 3 && term.charAt(term.length - 1) === "s") variants.push(term.slice(0, -1));
    return variants;
  }

  function scorePage(page, terms, requireAll) {
    var title = page.title.toLowerCase();
    var body = page.text.toLowerCase();
    var score = 0;
    var firstAt = -1;
    var matched = 0;
    terms.forEach(function (term) {
      var found = false;
      termVariants(term).forEach(function (v) {
        var at = body.indexOf(v);
        if (title.indexOf(v) !== -1) { score += 5; found = true; }
        if (at !== -1) {
          found = true;
          score += 1 + Math.min(body.split(v).length - 1, 5);
          if (firstAt === -1 || at < firstAt) firstAt = at;
        }
      });
      if (found) matched++;
    });
    if (requireAll && matched < terms.length) return null;
    return matched === 0 ? null : { score: score, at: firstAt };
  }

  function runSearch(query) {
    var index = window.SAI_INDEX || [];
    var terms = query.toLowerCase().split(/\s+/).filter(Boolean);
    var hits = [];
    index.forEach(function (page) {
      var result = scorePage(page, terms, true);
      if (result) hits.push({ page: page, score: result.score, at: result.at });
    });
    if (hits.length === 0 && terms.length > 1) {   // nothing has every word: show pages with any word
      index.forEach(function (page) {
        var result = scorePage(page, terms, false);
        if (result) hits.push({ page: page, score: result.score, at: result.at });
      });
    }
    hits.sort(function (a, b) { return b.score - a.score; });
    return hits;
  }

  function snippetFor(page, terms, at) {
    var start = Math.max(0, (at < 0 ? 0 : at) - 60);
    var text = page.text.substring(start, start + 220);
    var html = escapeHtml(text);
    terms.forEach(function (term) {
      if (!term) return;
      var pattern = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
      html = html.replace(pattern, function (m) { return "<mark>" + m + "</mark>"; });
    });
    return (start > 0 ? "&hellip;" : "") + html + "&hellip;";
  }

  function showResults(query) {
    var summary = document.getElementById("search-summary");
    var list = document.getElementById("results");
    if (!summary || !list) return;
    var q = (query || "").trim();
    var input = document.getElementById("q");
    if (input) input.value = q;
    list.innerHTML = "";
    if (!q) {
      summary.textContent = "Type something to search the SaiLang website.";
      return;
    }
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    var hits = runSearch(q);
    summary.textContent = hits.length
      ? hits.length + " result" + (hits.length === 1 ? "" : "s") + " for \u201c" + q + "\u201d"
      : "No results for \u201c" + q + "\u201d. Try a shorter word, such as \u201cdownload\u201d or \u201cIDLE\u201d.";
    hits.forEach(function (hit) {
      var li = document.createElement("li");
      li.innerHTML = '<a class="result-title" href="' + hit.page.url + '">' + escapeHtml(hit.page.title) +
        '</a><br>' + snippetFor(hit.page, terms, hit.at);
      list.appendChild(li);
    });
  }

  // ----- checksum verifier --------------------------------------------------
  function sha256Hex(buffer) {
    return crypto.subtle.digest("SHA-256", buffer).then(function (digest) {
      return Array.prototype.map.call(new Uint8Array(digest), function (b) {
        return ("00" + b.toString(16)).slice(-2);
      }).join("");
    });
  }

  function setupVerifier() {
    var box = document.querySelector(".verify");
    var fileInput = document.getElementById("verify-file");
    var result = document.getElementById("verify-result");
    if (!box || !fileInput || !result) return;
    var expected = (box.getAttribute("data-sha256") || "").toLowerCase();

    fileInput.addEventListener("change", function () {
      var file = fileInput.files && fileInput.files[0];
      result.className = "";
      if (!file) return;
      if (!window.crypto || !window.crypto.subtle) {
        result.textContent = "Your browser cannot check files here. Compare the hash manually with certutil (see the instructions).";
        return;
      }
      result.textContent = "Checking " + file.name + "...";
      file.arrayBuffer().then(sha256Hex).then(function (hex) {
        if (hex === expected) {
          result.className = "ok";
          result.textContent = "Match: " + file.name + " is the genuine SaiLang download.";
        } else {
          result.className = "bad";
          result.textContent = "No match. Do not run " + file.name + ". Download it again from this page.";
        }
      }, function () {
        result.className = "bad";
        result.textContent = "Could not read that file.";
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var params = new URLSearchParams(window.location.search);
    if (document.getElementById("results")) {
      showResults(params.get("q"));
      var form = document.querySelector(".search-page");
      if (form) form.addEventListener("submit", function (e) {
        e.preventDefault();
        var q = document.getElementById("q").value;
        window.location.search = "?q=" + encodeURIComponent(q.trim());
      });
    }
    setupVerifier();
  });
})();
