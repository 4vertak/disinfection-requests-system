document.getElementById("area_size").addEventListener("input", function () {
  this.value = this.value.replace(",", ".");

  const areaSize = parseFloat(this.value) || 0;
  const volumeSize = areaSize * 3.0;
  const sprayingTime = volumeSize * 3.6;
  const formattedSprayingTime = formatTimer(sprayingTime);

  document.getElementById("volume_size").value = volumeSize;
  document.getElementById("spraying_time").value = formattedSprayingTime;
});

function toggleReasonField() {
  var userTypeSelect = document.getElementById("rejection");
  var reasonField = document.getElementById("reasonField");
  var areaField = document.getElementById("areaField");
  var volumeField = document.getElementById("volumeField");
  var sprayingField = document.getElementById("sprayingField");
  if (userTypeSelect.checked) {
    // Изменяем здесь
    reasonField.style.display = "block";
    areaField.style.display = "none";
    volumeField.style.display = "none";
    sprayingField.style.display = "none";
  } else {
    reasonField.style.display = "none";
    areaField.style.display = "block";
    volumeField.style.display = "block";
    sprayingField.style.display = "block";
  }
}

document.addEventListener("DOMContentLoaded", function () {
  toggleReasonField();
});
