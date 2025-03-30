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
    // Если поле пустое - возвращаем null
    if (!phone || phone.trim() === "") {
      return null;
    }
    // Удаляем все нецифровые символы
    const cleaned = phone.replace(/\D/g, "");

    if (cleaned.length === 10 || cleaned.length === 11) {
      return null; // Номер валиден
    } else {
      return "Неправильный формат номера";
    }
  }

  function validateFill(listener_value) {
    // Если поле пустое - возвращаем null
    if (!listener_value || listener_value.trim() === "") return null;
  }

  // Функция для создания/обновления сообщения об ошибке
  function updateError(inputElement, message) {
    // Удаляем предыдущее сообщение об ошибке, если оно есть
    let errorElement = inputElement.nextElementSibling;
    if (errorElement && errorElement.classList.contains("error-message")) {
      errorElement.remove();
    }

    // Если есть сообщение об ошибке, создаем элемент для него
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

  // Получаем оба поля для телефона
  const contactPhone = document.getElementById("contact_phone");
  const relativeContactPhone = document.getElementById(
    "relative_contact_phone"
  );

  // ПОлучаем место работы и должность
  const workplace = document.getElementById("workplace");
  const position = document.getElementById("position");

  // Обработчик для основного телефона
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

  // Обработчик для дополнительного телефона
  if (relativeContactPhone) {
    relativeContactPhone.addEventListener("blur", function () {
      if (!this.value || this.value.trim() === "") {
        this.value = "не указан";
        this.classList.add("text-muted"); // Делаем текст серым
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

    // Инициализация при загрузке
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

    // Инициализация при загрузке
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

    // Инициализация при загрузке
    if (!position.value || position.value.trim() === "") {
      position.value = "не работает";
      position.classList.add("text-muted");
    }
  }
});

$(document).ready(function () {
  // Загружаем все диагнозы с сервера
  $.ajax({
    url: "/api/diagnoses",
    method: "GET",
    dataType: "json",
    success: function (data) {
      // Инициализируем Select2 после загрузки данных
      $("#diagnosis_select").select2({
        theme: "bootstrap-5",
        placeholder: "Выберите или введите диагноз",
        allowClear: true,
        // tags: true, // Разрешаем ввод новых значений
        data: data, // Передаём загруженные данные
        minimumInputLength: 0, // Показывать список без ввода
        language: "ru", // Локализация (если нужно)
      });
    },
    error: function (error) {
      console.error("Ошибка загрузки диагнозов:", error);
    },
  });
});
