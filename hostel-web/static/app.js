const roomList = document.querySelector("#room-list");
const form = document.querySelector("#room-form");
const formMessage = document.querySelector("#form-message");
const directoryMessage = document.querySelector("#directory-message");

function makeCell(text, className = "") {
  const cell = document.createElement("td");
  cell.textContent = text;
  if (className) cell.className = className;
  return cell;
}

function showDirectoryMessage(text, isError = false) {
  directoryMessage.textContent = text;
  directoryMessage.classList.toggle("error", isError);
}

function renderRooms(rooms) {
  roomList.replaceChildren();
  document.querySelector("#directory-count").textContent = `${rooms.length} ${rooms.length === 1 ? "room" : "rooms"}`;

  if (rooms.length === 0) {
    const row = document.createElement("tr");
    row.append(makeCell("No rooms yet. Add the first room using the form.", "empty-row"));
    row.firstElementChild.colSpan = 4;
    roomList.append(row);
    return;
  }

  for (const room of rooms) {
    const row = document.createElement("tr");
    const name = makeCell("");
    const roomName = document.createElement("span");
    roomName.className = "room-name";
    roomName.textContent = room.name;
    name.append(roomName);

    const occupancy = makeCell("");
    const bar = document.createElement("div");
    bar.className = "occupancy-line";
    const fill = document.createElement("span");
    fill.style.width = `${Math.round((room.occupied / room.capacity) * 100)}%`;
    bar.append(fill);
    const occupancyText = document.createElement("span");
    occupancyText.className = "occupancy-text";
    occupancyText.textContent = `${room.occupied} / ${room.capacity} beds`;
    occupancy.append(bar, occupancyText);

    const available = room.capacity - room.occupied;
    const availability = makeCell("");
    const badge = document.createElement("span");
    badge.className = available > 0 ? "availability-badge" : "availability-badge full";
    badge.textContent = available > 0 ? `${available} free` : "Full";
    availability.append(badge);

    const manage = makeCell("");
    const actions = document.createElement("div");
    actions.className = "room-actions";
    const occupiedInput = document.createElement("input");
    occupiedInput.className = "occupancy-input";
    occupiedInput.type = "number";
    occupiedInput.min = "0";
    occupiedInput.max = String(room.capacity);
    occupiedInput.value = String(room.occupied);
    occupiedInput.setAttribute("aria-label", `Occupied beds for ${room.name}`);

    const saveButton = document.createElement("button");
    saveButton.className = "action-button";
    saveButton.type = "button";
    saveButton.textContent = "Save";
    saveButton.setAttribute("aria-label", `Save occupancy for ${room.name}`);
    saveButton.addEventListener("click", () => updateOccupancy(room.id, occupiedInput.value));

    const deleteButton = document.createElement("button");
    deleteButton.className = "action-button danger";
    deleteButton.type = "button";
    deleteButton.textContent = "Delete";
    deleteButton.setAttribute("aria-label", `Delete ${room.name}`);
    deleteButton.addEventListener("click", () => deleteRoom(room));

    actions.append(occupiedInput, saveButton, deleteButton);
    manage.append(actions);
    row.append(name, occupancy, availability, manage);
    roomList.append(row);
  }
}

async function refreshDashboard() {
  try {
    const response = await fetch("/api/rooms");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load room information.");
    document.querySelector("#room-count").textContent = data.summary.room_count;
    document.querySelector("#capacity-count").textContent = data.summary.capacity;
    document.querySelector("#occupied-count").textContent = data.summary.occupied;
    document.querySelector("#available-count").textContent = data.summary.available;
    renderRooms(data.rooms);
  } catch (error) {
    roomList.replaceChildren();
    const row = document.createElement("tr");
    row.append(makeCell(error.message, "empty-row"));
    row.firstElementChild.colSpan = 4;
    roomList.append(row);
  }
}

async function updateOccupancy(roomId, occupiedText) {
  const occupied = Number(occupiedText);
  if (!Number.isInteger(occupied) || occupied < 0) {
    showDirectoryMessage("Enter a non-negative whole number of occupied beds.", true);
    return;
  }

  try {
    const response = await fetch(`/api/rooms/${roomId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ occupied }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not update this room.");
    showDirectoryMessage("Room occupancy saved.");
    await refreshDashboard();
  } catch (error) {
    showDirectoryMessage(error.message, true);
  }
}

async function deleteRoom(room) {
  if (!window.confirm(`Delete room ${room.name}?`)) return;

  try {
    const response = await fetch(`/api/rooms/${room.id}`, { method: "DELETE" });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not delete this room.");
    showDirectoryMessage(`${room.name} was deleted.`);
    await refreshDashboard();
  } catch (error) {
    showDirectoryMessage(error.message, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formMessage.textContent = "";
  formMessage.classList.remove("error");
  const formData = new FormData(form);

  try {
    const response = await fetch("/api/rooms", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: formData.get("name"),
        capacity: Number(formData.get("capacity")),
        occupied: Number(formData.get("occupied")),
      }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not add the room.");

    form.reset();
    document.querySelector("#room-capacity").value = 2;
    document.querySelector("#room-occupied").value = 0;
    formMessage.textContent = `${result.room.name} was added.`;
    await refreshDashboard();
  } catch (error) {
    formMessage.textContent = error.message;
    formMessage.classList.add("error");
  }
});

refreshDashboard();
