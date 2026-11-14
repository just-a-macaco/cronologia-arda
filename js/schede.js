/* Elenco delle schede. Legge EVENTS da js/data.js e costruisce le card. */
const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[c]));

const normalizza = (t) => String(t ?? "")
  .toLowerCase()
  .normalize("NFD")
  .replace(/[\u0300-\u036f]/g, "");

const cards = document.getElementById("cards");
const input = document.getElementById("q");
const count = document.getElementById("count");

const schede = EVENTS.map((e) => {
  const card = document.createElement("article");
  card.className = "card";
  card.dataset.search = normalizza([
    e.title, e.label, e.type,
    (e.places || []).join(" "),
    (e.people || []).join(" "),
    e.short, e.long,
  ].join(" "));

  const luoghi = (e.places || []).join(" · ");
  const persone = (e.participants || []).map((p) => {
    const parte = p.parte ? ` · ${esc(p.parte)}` : "";
    const ruolo = p.ruolo ? ` — ${esc(p.ruolo)}` : "";
    const esito = p.esito ? ` → ${esc(p.esito)}` : "";
    return `<li><b>${esc(p.nome)}</b>${parte}${ruolo}${esito}</li>`;
  }).join("");
  const fonti = (e.sources || []).map((f) => `${esc(f.opera)}, ${esc(f.riferimento)}`).join(" · ");

  card.innerHTML = `
    <p class="card-top"><span class="card-date">${esc(e.label)}</span><span class="card-type">${esc(e.type)}</span></p>
    <h2>${esc(e.title)}</h2>
    ${luoghi ? `<p class="card-place">${esc(luoghi)}</p>` : ""}
    <p class="card-short">${esc(e.short)}</p>
    <details>
      <summary>Leggi la scheda completa</summary>
      <p class="card-long">${esc(e.long)}</p>
      ${persone ? `<h3>Partecipanti</h3><ul class="people">${persone}</ul>` : ""}
      <p class="card-source">Fonte: ${fonti}</p>
      ${e.note ? `<p class="card-note">Nota: ${esc(e.note)}</p>` : ""}
    </details>`;
  cards.appendChild(card);
  return card;
});

const filtra = () => {
  const q = normalizza(input.value.trim());
  let visibili = 0;
  schede.forEach((card) => {
    const mostra = !q || card.dataset.search.includes(q);
    card.hidden = !mostra;
    if (mostra) visibili++;
  });
  count.textContent = `${visibili} di ${EVENTS.length} schede`;
};

input.addEventListener("input", filtra);
filtra();
