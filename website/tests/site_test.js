/* SaiLang website tests: run the real pages in jsdom and check search and the checksum checker. */
const { JSDOM } = require("jsdom");
const fs = require("fs");
const path = require("path");
// Run after building the site:  cd website/tests && npm install jsdom@24 && node site_test.js
const SITE = process.env.SITE_DIR || path.join(__dirname, "..", "..", "dist", "SaiLang-Website");

function load(page, query = "", extra = {}) {
  const html = fs.readFileSync(path.join(SITE, page), "utf8");
  const dom = new JSDOM(html, {
    url: "file://" + path.join(SITE, page) + query,
    runScripts: "outside-only",
    pretendToBeVisual: true,
  });
  const w = dom.window;
  // Load the same scripts a browser would, in page order.
  const idx = fs.readFileSync(path.join(SITE, "search-index.js"), "utf8");
  Object.defineProperty(w, "crypto", { value: require("crypto").webcrypto, configurable: true }); // jsdom lacks crypto.subtle; browsers have it
  if (!w.File.prototype.arrayBuffer) {   // browsers have File.arrayBuffer; add it for jsdom
    w.File.prototype.arrayBuffer = function () {
      const file = this;
      return new Promise((resolve, reject) => {
        const reader = new w.FileReader();
        reader.onload = () => resolve(new Uint8Array(reader.result).buffer);
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
      });
    };
  }
  w.eval(idx);
  w.eval(fs.readFileSync(path.join(SITE, "assets/site.js"), "utf8"));
  w.document.dispatchEvent(new w.Event("DOMContentLoaded"));
  return w;
}

let failures = 0;
function check(name, cond, detail = "") {
  console.log((cond ? "PASS " : "FAIL ") + name + (detail ? "  [" + detail + "]" : ""));
  if (!cond) failures++;
}

// 1. Search results for a word known to be in the download page
let w = load("search.html", "?q=checksum");
let summary = w.document.getElementById("search-summary").textContent;
let items = w.document.querySelectorAll("#results li");
check("search finds 'checksum'", items.length > 0, summary);
check("search result links to a real page", [...items].some(li => /download\.html|instructions\.html/.test(li.innerHTML)));

// 2. Search for a word that is not in the site
w = load("search.html", "?q=zxqwvy");
check("no-result message shown", /No results/.test(w.document.getElementById("search-summary").textContent));

// 3. Multi-word search narrows results
w = load("search.html", "?q=book+chapters");
check("multi-word search finds book page", w.document.querySelectorAll("#results li").length >= 1 &&
  /book\.html/.test(w.document.getElementById("results").innerHTML));

// 4. Search for IDLE
w = load("search.html", "?q=IDLE");
const idleHits = w.document.querySelectorAll("#results li").length;
check("search finds IDLE (case-insensitive)", idleHits >= 2, idleHits + " hits");

// 5. Search results are escaped (no script injection)
w = load("search.html", "?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E");
check("query is shown escaped, no script tag created", w.document.querySelectorAll("#results script").length === 0);

// 6. Header search box exists on every page
for (const p of ["index.html", "about.html", "download.html", "instructions.html", "book.html"]) {
  const d = load(p).document;
  check(`header search on ${p}`, !!d.querySelector('header form[action="search.html"] input[name="q"]'));
}

// 7. Checksum verifier: matching and non-matching file
const expected = fs.readFileSync(path.join(SITE, "downloads/SaiLang-v1.0.0.zip.sha256"), "utf8").split(/\s+/)[0];
const zipBytes = fs.readFileSync(path.join(SITE, "downloads/SaiLang-v1.0.0.zip"));
async function verify(bytes, name) {
  const page = load("download.html");
  const input = page.document.getElementById("verify-file");
  const file = new page.File([bytes], name);
  Object.defineProperty(input, "files", { value: [file] });
  input.dispatchEvent(new page.Event("change"));
  // wait for async read + digest
  for (let i = 0; i < 100; i++) {
    await new Promise(r => setTimeout(r, 50));
    const t = page.document.getElementById("verify-result").textContent;
    if (!/Checking/.test(t)) return { text: t, cls: page.document.getElementById("verify-result").className };
  }
  return { text: "TIMEOUT", cls: "" };
}
(async () => {
  const good = await verify(zipBytes, "SaiLang-v1.0.0.zip");
  check("verifier accepts the genuine ZIP", good.cls === "ok", good.text);
  const bad = await verify(Buffer.concat([zipBytes, Buffer.from("x")]), "SaiLang-v1.0.0.zip");
  check("verifier rejects a changed ZIP", bad.cls === "bad", bad.text);
  console.log(failures ? `\n${failures} FAILED` : "\nALL PASSED");
  process.exit(failures ? 1 : 0);
})();
