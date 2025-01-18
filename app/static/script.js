const API_URL = "/api/zadaci";
async function dohvatiZadatke() {
    const response = await fetch(API_URL);
    const zadaci = await response.json();
    prikaziZadatke(zadaci);
}
function prikaziZadatke(zadaci) {
    const lista = document.getElementById("lista-zadataka");
    lista.innerHTML = "";
    zadaci.forEach(zadatak => {
        const li = document.createElement("li");
        li.innerHTML = `
            ${zadatak.naslov}
            <button onclick="obrisiZadatak(${zadatak.id})">Obriši</button>
        `;
        lista.appendChild(li);
    });
}
async function dodajZadatak(event) {
    event.preventDefault();
    const naslov = document.getElementById("naslov-zadatka").value;
    const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ naslov }),
    });
    if (response.ok) {
        dohvatiZadatke();
        document.getElementById("naslov-zadatka").value = "";
    }
}
async function obrisiZadatak(id) {
    const response = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
    if (response.ok) {
        dohvatiZadatke();
    }
}

document.getElementById("forma-zadatak").addEventListener("submit", dodajZadatak);

dohvatiZadatke();