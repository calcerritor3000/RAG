document.getElementById("ingestForm").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const msg = document.getElementById("ingestMsg");
  const file = document.getElementById("fileInput").files[0];
  if (!file) return;
  msg.textContent = "Guardando embeddings en ChromaDB...";
  msg.className = "";
  const fd = new FormData();
  fd.append("file", file);
  try {
    const res = await fetch("/ingest", { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");
    msg.textContent = `OK: ${data.chunks} chunks guardados con embeddings.`;
    msg.className = "ok";
  } catch (e) {
    msg.textContent = e.message;
    msg.className = "err";
  }
});

document.getElementById("searchForm").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const msg = document.getElementById("searchMsg");
  const box = document.getElementById("chunksBox");
  const results = document.getElementById("results");
  const q = document.getElementById("questionInput").value.trim();
  if (!q) return;
  msg.textContent = "Buscando por similitud semantica...";
  msg.className = "";
  try {
    const res = await fetch("/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");
    msg.textContent = "";
    document.getElementById("questionShown").textContent = "Pregunta: " + data.question;
    box.innerHTML = "";
    const chunks = data.raw_chunks || [];
    if (!chunks.length) {
      box.innerHTML = "<p class='err'>No hay chunks. Sube un documento primero.</p>";
    } else {
      chunks.forEach((item, i) => {
        const div = document.createElement("div");
        div.className = "chunk-card";
        const text = typeof item === "string" ? item : item.chunk || "";
        const sim = typeof item === "object" && item.similarity != null ? item.similarity : "?";
        const src = typeof item === "object" && item.source ? item.source : "";
        div.innerHTML =
          `<div class="chunk-meta">#${i + 1} · similitud: ${sim}` +
          (src ? ` · fuente: ${src}` : "") +
          `</div>${text}`;
        box.appendChild(div);
      });
    }
    results.hidden = false;
  } catch (e) {
    msg.textContent = e.message;
    msg.className = "err";
    results.hidden = true;
  }
});
