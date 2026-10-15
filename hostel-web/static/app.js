const roomList = document.querySelector("#room-list");
const form = document.querySelector("#room-form");
const message = document.querySelector("#form-message");

function makeCell(text, className = "") {
  const cell = document.createElement("td");
  cell.textContent = text;
  if (className) cell.className = className;
  return cell;
}

function renderRooms(rooms) {
  roomList.replaceChildren();
  document.querySelector("#directory-count").textContent = `${rooms.length} ${rooms.length === 1 ? "room" : "rooms"}`;

  if (rooms.length === 0) {
    const row = document.createElement("tr");
    row.append(makeCell("No rooms yet. Add the first room using the form.", "empty-row"));
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
    row.append(name, occupancy, availability);
    roomList.append(row);
  }
}

async function refreshDashboard() {
  try {
    const response = await fetch("/api/rooms");
    if (!response.ok) throw new Error("Could not load room information.");
    const data = await response.json();
    document.querySelector("#room-count").textContent = data.summary.room_count;
    document.querySelector("#capacity-count").textContent = data.summary.capacity;
    document.querySelector("#occupied-count").textContent = data.summary.occupied;
    document.querySelector("#available-count").textContent = data.summary.available;
    renderRooms(data.rooms);
  } catch (error) {
    roomList.replaceChildren();
    const row = document.createElement("tr");
    row.append(makeCell(error.message, "empty-row"));
    roomList.append(row);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  const formData = new FormData(form);
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
  if (!response.ok) {
    message.textContent = result.error || "Could not add the room.";
    message.classList.add("error");
    return;
  }

  form.reset();
  document.querySelector("#room-capacity").value = 2;
  document.querySelector("#room-occupied").value = 0;
  message.textContent = `${result.room.name} was added.`;
  message.classList.remove("error");
  await refreshDashboard();
});

refreshDashboard();
