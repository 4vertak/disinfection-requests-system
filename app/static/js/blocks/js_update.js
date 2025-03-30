document.addEventListener("DOMContentLoaded", function () {
  const changePasswordCheckbox = document.getElementById("change_password");
  const passwordFields = document.getElementById("password_fields");
  const currentPasswordField = document.querySelector(
    ".current-password-field"
  );
  const currentPasswordInput = document.getElementById("current_password");

  if (changePasswordCheckbox && passwordFields) {
    changePasswordCheckbox.addEventListener("change", function () {
      // Показываем/скрываем блок с полями пароля
      passwordFields.style.display = this.checked ? "block" : "none";

      // Устанавливаем обязательность полей
      const required = this.checked;

      // Для текущего пароля (если поле существует на странице)
      if (
        currentPasswordInput &&
        currentPasswordField.style.display !== "none"
      ) {
        currentPasswordInput.required = required;
      }

      document.getElementById("new_password").required = required;
      document.getElementById("confirm_new_password").required = required;
    });

    // Инициализация при загрузке страницы
    if (changePasswordCheckbox.checked) {
      passwordFields.style.display = "block";
    }
  }
});
