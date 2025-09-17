function toggleReasonField() {
  var userTypeSelect = document.getElementById("reason_application");
  var dateField = document.getElementById("dateField");
  var placeFeald = document.getElementById("placeFeald");
  if (userTypeSelect.value === "hospitalization") {
    dateField.style.display = "block";
    placeFeald.style.display = "block";
  } else {
    dateField.style.display = "none";
    placeFeald.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", function () {
  toggleReasonField();
});

document.addEventListener("DOMContentLoaded", function () {
  // Функция для проверки номера телефона
  function validatePhone(phone) {
    if (!phone || phone.trim() === "") {
      return null;
    }

    const cleaned = phone.replace(/\D/g, "");

    if (cleaned.length === 10 || cleaned.length === 11) {
      return null;
    } else {
      return "Неправильный формат номера";
    }
  }

  function validateFill(listener_value) {
    if (!listener_value || listener_value.trim() === "") return null;
  }

  function updateError(inputElement, message) {
    let errorElement = inputElement.nextElementSibling;
    if (errorElement && errorElement.classList.contains("error-message")) {
      errorElement.remove();
    }

    if (message) {
      errorElement = document.createElement("div");
      errorElement.className = "error-message text-danger mt-1";
      errorElement.textContent = message;
      inputElement.insertAdjacentElement("afterend", errorElement);
      inputElement.classList.add("is-invalid");
    } else {
      inputElement.classList.remove("is-invalid");
    }
  }

  const contactPhone = document.getElementById("contact_phone");
  const relativeContactPhone = document.getElementById(
    "relative_contact_phone"
  );

  const workplace = document.getElementById("workplace");
  const position = document.getElementById("position");

  if (contactPhone) {
    contactPhone.addEventListener("blur", function () {
      const error = validatePhone(this.value);
      updateError(this, error);
    });
    contactPhone.addEventListener("input", function () {
      const error = validatePhone(this.value);
      updateError(this, error);
    });
  }

  if (relativeContactPhone) {
    relativeContactPhone.addEventListener("blur", function () {
      if (!this.value || this.value.trim() === "") {
        this.value = "не указан";
        this.classList.add("text-muted");
      } else {
        const error = validatePhone(this.value);
        updateError(this, error);
        this.classList.remove("text-muted");
      }
    });

    relativeContactPhone.addEventListener("focus", function () {
      if (this.value === "не указан") {
        this.value = "";
        this.classList.remove("text-muted");
      }
    });

    relativeContactPhone.addEventListener("input", function () {
      const error = validatePhone(this.value);
      updateError(this, error);
    });

    if (
      !relativeContactPhone.value ||
      relativeContactPhone.value.trim() === ""
    ) {
      relativeContactPhone.value = "не указан";
      relativeContactPhone.classList.add("text-muted");
    }
  }

  if (workplace) {
    workplace.addEventListener("blur", function () {
      if (!this.value || this.value.trim() === "") {
        this.value = "не работает";
        this.classList.add("text-muted"); // Делаем текст серым
      } else {
        const error = validateFill(this.value);
        updateError(this, error);
        this.classList.remove("text-muted");
      }
    });

    workplace.addEventListener("focus", function () {
      if (this.value === "не работает") {
        this.value = "";
        this.classList.remove("text-muted");
      }
    });

    workplace.addEventListener("input", function () {
      const error = validateFill(this.value);
      updateError(this, error);
    });

    if (!workplace.value || workplace.value.trim() === "") {
      workplace.value = "не работает";
      workplace.classList.add("text-muted");
    }
  }
  if (position) {
    position.addEventListener("blur", function () {
      if (!this.value || this.value.trim() === "") {
        this.value = "не работает";
        this.classList.add("text-muted"); // Делаем текст серым
      } else {
        const error = validateFill(this.value);
        updateError(this, error);
        this.classList.remove("text-muted");
      }
    });

    position.addEventListener("focus", function () {
      if (this.value === "не работает") {
        this.value = "";
        this.classList.remove("text-muted");
      }
    });

    position.addEventListener("input", function () {
      const error = validateFill(this.value);
      updateError(this, error);
    });

    if (!position.value || position.value.trim() === "") {
      position.value = "не работает";
      position.classList.add("text-muted");
    }
  }
});

$(document).ready(function () {
  $.ajax({
    url: "/api/diagnoses",
    method: "GET",
    dataType: "json",
    success: function (data) {
      // Инициализируем Select2
      $("#diagnosis_select").select2({
        theme: "bootstrap-5",
        placeholder: "Выберите или введите диагноз",
        allowClear: true,
        // tags: true
        data: data,
        minimumInputLength: 0,
        language: "ru",
        //выкл сортировки
        sorter: function (data) {
          return data;
        }
      });
    },
    error: function (error) {
      console.error("Ошибка загрузки диагнозов:", error);
    },
  });
});
