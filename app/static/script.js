
window.addEventListener("DOMContentLoaded", () => {
    osvjeziZadatke();
    document.getElementById("btn-refresh-zadaci")
      .addEventListener("click", osvjeziZadatke);
  
    const formaZadatakKomplet = document.getElementById("forma-zadatak-komplet");
    formaZadatakKomplet.addEventListener("submit", async function (e) {
      e.preventDefault();
      await kreirajZadatak();
    });
  });
  
  async function kreirajZadatak() {
    const naslov = document.getElementById("naslov").value.trim();
    const ime = document.getElementById("ime").value.trim();
    const prezime = document.getElementById("prezime").value.trim();
    const kategorija = document.getElementById("kategorija").value.trim();
    const tagoviString = document.getElementById("tagovi").value.trim();
    const komentar = document.getElementById("komentar").value.trim() || null;
  
    let tagovi = [];
    if (tagoviString) {
      tagovi = tagoviString.split(",").map(t => t.trim()).filter(t => t.length > 0);
    }
  
    const bodyData = {
      naslov,
      ime,
      prezime,
      kategorija,
      tagovi,
      komentar
    };
  
    try {
      const res = await fetch("/api/zadaci_komplet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bodyData),
      });
  
      if (res.ok) {

        document.getElementById("naslov").value = "";
        document.getElementById("ime").value = "";
        document.getElementById("prezime").value = "";
        document.getElementById("kategorija").value = "";
        document.getElementById("tagovi").value = "";
        document.getElementById("komentar").value = "";
  
        alert("Zadatak kreiran!");
        osvjeziZadatke();
      } else {
        const err = await res.json();
        alert(`Greška pri kreiranju zadatka: ${err.detail || err}`);
      }
    } catch (error) {
      alert("Dogodila se greška prilikom kreiranja zadatka.");
      console.error(error);
    }
  }
  
  async function osvjeziZadatke() {
    try {
      const res = await fetch("/api/zadaci");
      if (!res.ok) {
        console.error("Greška prilikom dohvata zadataka");
        return;
      }
      const zadaci = await res.json();
  
      const lista = document.getElementById("lista-zadataka");
      lista.innerHTML = "";
  
      zadaci.forEach((z) => {
        const li = document.createElement("li");
  

        li.innerHTML = `
          <strong>${z.naslov}</strong><br>
          Kategorija: ${z.kategorija || "N/A"}<br>
          Korisnik: ${z.korisnik || "N/A"}<br>
          Tagovi: ${z.tagovi.join(", ") || "Nema"}<br>
          Komentari: ${z.komentari.join(" | ") || "Nema"}
        `;
  
  
        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Obriši";
        deleteBtn.classList.add("btn-delete");
        deleteBtn.addEventListener("click", async () => {
          const potvrdi = confirm("Želite li obrisati zadatak?");
          if (potvrdi) {
            await obrisiZadatak(z.id);
          }
        });
  
        li.appendChild(deleteBtn);
        lista.appendChild(li);
      });
    } catch (error) {
      console.error("Greška u osvjeziZadatke:", error);
    }
  }
  
  async function obrisiZadatak(id) {
    try {
      const res = await fetch(`/api/zadaci/${id}`, {
        method: "DELETE",
      });
      if (res.ok) {
        alert("Zadatak obrisan!");
        osvjeziZadatke();
      } else {
        const err = await res.json();
        alert(`Greška pri brisanju: ${err.detail || err}`);
      }
    } catch (error) {
      alert("Dogodila se greška prilikom brisanja zadatka.");
      console.error(error);
    }
  }
  