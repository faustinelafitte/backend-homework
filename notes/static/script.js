document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("create-note-form");

  // Création d'une note
  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const title = form.title.value;
      const content = form.content.value;

      fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content }),
      })
        .then((res) => res.json())
        .then(() => form.reset());
    });
  }

  // Ajoute les gestionnaires d'événements sur les cases à cocher
  function attachDoneListeners() {
    document.querySelectorAll(".note input[type=checkbox]").forEach((checkbox) => {
      checkbox.onchange = () => {
        const id = checkbox.dataset.id;
        const done = checkbox.checked;

        fetch(`/api/notes/${id}/done`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ done }),
        });
      };
    });
  }

  // Met à jour dynamiquement le DOM des notes
  function updateNotes(notes) {
    const container = document.getElementById("notes");
    container.innerHTML = "";

    for (const note of notes) {
      const div = document.createElement("div");
      div.className = "note" + (note.done ? " done" : "");

      const h2 = document.createElement("h2");
      h2.textContent = note.title;

      const p = document.createElement("p");
      p.textContent = note.content;

      const form = document.createElement("form");
      const label = document.createElement("label");
      label.textContent = "done";

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = note.done;
      checkbox.dataset.id = note.id;

      form.appendChild(label);
      form.appendChild(checkbox);

      div.appendChild(h2);
      div.appendChild(p);
      div.appendChild(form);

      container.appendChild(div);
    }

    attachDoneListeners();
  }

  // Polling pour synchro
  let lastUpdate = Date.now();
  function startPolling() {
    fetch(`/api/notes/stream?since=${lastUpdate}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.notes.length > 0) {
          updateNotes(data.notes);
        }
        lastUpdate = data.timestamp;
        setTimeout(startPolling, 500);
      })
      .catch(() => setTimeout(startPolling, 2000));
  }

  startPolling();
  attachDoneListeners();
});
