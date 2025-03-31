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
  var rejectionCheckbox = document.getElementById("rejection");
  var reasonField = document.getElementById("reasonField");
  var reasonInput = document.getElementById("rejection_reason");
  var areaField = document.getElementById("areaField");
  var volumeField = document.getElementById("volumeField");
  var sprayingField = document.getElementById("sprayingField");

  if (rejectionCheckbox.checked) {
    // Показываем поле причины отказа и скрываем остальные
    reasonField.style.display = "block";
    areaField.style.display = "none";
    volumeField.style.display = "none";
    sprayingField.style.display = "none";

    // Устанавливаем значение по умолчанию, если поле пустое
    if (!reasonInput.value || reasonInput.value.trim() === "") {
      reasonInput.value = "Отказ";
      reasonInput.classList.add("text-muted");
    }
  } else {
    // Скрываем поле причины отказа и показываем остальные
    reasonField.style.display = "none";
    areaField.style.display = "block";
    volumeField.style.display = "block";
    sprayingField.style.display = "block";

    // Очищаем поле причины отказа при снятии чекбокса
    reasonInput.value = "";
    reasonInput.classList.remove("text-muted");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  toggleReasonField();

  var reasonInput = document.getElementById("rejection_reason");
  var rejectionCheckbox = document.getElementById("rejection");

  if (reasonInput) {
    reasonInput.addEventListener("focus", function () {
      if (this.value === "Отказ") {
        this.value = "";
        this.classList.remove("text-muted");
      }
    });

    reasonInput.addEventListener("blur", function () {
      if (
        rejectionCheckbox.checked &&
        (!this.value || this.value.trim() === "")
      ) {
        this.value = "Отказ";
        this.classList.add("text-muted");
      }
    });

    rejectionCheckbox.addEventListener("change", toggleReasonField);

    if (
      rejectionCheckbox.checked &&
      (!reasonInput.value || reasonInput.value.trim() === "")
    ) {
      reasonInput.value = "Отказ";
      reasonInput.classList.add("text-muted");
    }
  }
});
