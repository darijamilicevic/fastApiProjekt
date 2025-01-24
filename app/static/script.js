window.addEventListener("DOMContentLoaded", () => {
  ucitajKategorije();
  ucitajKorisnike();
  ucitajTagove();
  osvjeziZadatke();
});

async function ucitajKategorije() {
  const res = await fetch("/api/kategorije");
  if (!res.ok) return;
  const kategorije = await res.json();

  const select = document.getElementById("select-kategorija");
  select.innerHTML = `<option value="">-- Odaberi kategoriju --</option>`;
  
  kategorije.forEach((kat) => {
    const option = document.createElement("option");
    option.value = kat.id;
    option.textContent = kat.naziv;
    select.appendChild(option);
  });
}


async function ucitajKorisnike() {
  const res = await fetch("/api/korisnici");
  if (!res.ok) return;
  const korisnici = await res.json();

  const select = document.getElementById("select-korisnik");
  select.innerHTML = `<option value="">-- Odaberi korisnika --</option>`;

  korisnici.forEach((kor) => {
    const option = document.createElement("option");
    option.value = kor.id;
    option.textContent = `${kor.ime} ${kor.prezime}`;
    select.appendChild(option);
  });
}


async function ucitajTagove() {
  const res = await fetch("/api/tagovi");
  if (!res.ok) return;
  const tagovi = await res.json();

  const select = document.getElementById("select-tagovi");
  select.innerHTML = ""; 

  tagovi.forEach((t) => {
    const option = document.createElement("option");
    option.value = t.id;
    option.textContent = t.naziv;
    select.appendChild(option);
  });
}

const formaZadatakKomplet = document.getElementById("forma-zadatak-komplet");
formaZadatakKomplet.addEventListener("submit", async function (e) {
  e.preventDefault();

  const naslov = document.getElementById("naslov").value;
  const kategorija_id = parseInt(document.getElementById("select-kategorija").value);
  const korisnik_id = parseInt(document.getElementById("select-korisnik").value);
  const komentar = document.getElementById("komentar").value || null;

  const selectTagovi = document.getElementById("select-tagovi");
  const selectedOptions = [...selectTagovi.options].filter(o => o.selected);
  const tag_ids = selectedOptions.map(o => parseInt(o.value));


  const bodyData = {
    naslov,
    kategorija_id,
    korisnik_id,
    tag_ids,
    komentar
  };

  const res = await fetch("/api/zadaci_komplet", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bodyData),
  });

  if (res.ok) {
    document.getElementById("naslov").value = "";
    document.getElementById("select-kategorija").value = "";
    document.getElementById("select-korisnik").value = "";
    document.getElementById("select-tagovi").selectedIndex = -1; 
    document.getElementById("komentar").value = "";

  
    osvjeziZadatke();
    alert("Zadatak kreiran!");
  } else {
    const err = await res.json();
    alert(`Greška: ${err.detail || err}`);
  }
});


async function osvjeziZadatke() {
  const res = await fetch("/api/zadaci");
  if (!res.ok) return;
  const zadaci = await res.json();

  const lista = document.getElementById("lista-zadataka");
  lista.innerHTML = "";
  zadaci.forEach((z) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <strong>${z.naslov}</strong>
      <br>Kategorija: ${z.kategorija || "N/A"}
      <br>Korisnik: ${z.korisnik || "N/A"}
      <br>Tagovi: ${z.tagovi.join(", ")}
      <br>Komentari: ${z.komentari.join(" | ")}
    `;
    lista.appendChild(li);
  });
}

document.getElementById("btn-refresh-zadaci").addEventListener("click", () => {
  osvjeziZadatke();
});
