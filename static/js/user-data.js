const currentUser = localStorage.getItem("currentUser");

if (!currentUser) {
  alert("You must log in first.");
  window.location.href = "login.html";
}

document.getElementById("username").innerText = currentUser;

// Load user note if exists
let data = JSON.parse(localStorage.getItem(currentUser + "_data")) || {};
document.getElementById("savedNote").innerText = data.note || "";

function saveNote() {
  const note = document.getElementById("userNote").value;

  data.note = note;
  localStorage.setItem(currentUser + "_data", JSON.stringify(data));

  document.getElementById("status").innerText = "Note saved!";
  document.getElementById("savedNote").innerText = note;
}
