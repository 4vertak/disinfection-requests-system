// Обновление текста на странице
function updateText() {
  const totalUsers = parseInt(
    document.getElementById("total-users").textContent,
    10
  );
  const totalApplications = parseInt(
    document.getElementById("total-applications").textContent,
    10
  );

  const inProgressApplications = parseInt(
    document.getElementById("application-in-progress").textContent,
    10
  );

  const applicationsCompleted = parseInt(
    document.getElementById("applications-completed").textContent,
    10
  );

  const totalChanges = parseInt(
    document.getElementById("total-changes").textContent,
    10
  );

  const countAdmins = parseInt(
    document.getElementById("adminCount").textContent,
    10
  );

  const countDoctors = parseInt(
    document.getElementById("doctorCount").textContent,
    10
  );
  const countDisinfectors = parseInt(
    document.getElementById("disinfectorCount").textContent,
    10
  );

  // Склонение для пользователей
  document.getElementById("users-text").textContent = declensionWord(
    totalUsers,
    ["пользователь", "пользователя", "пользователей"]
  );

  // Склонение для заявок
  document.getElementById("applications-text").textContent = declensionWord(
    totalApplications,
    ["заявка", "заявки", "заявок"]
  );
  // Склонение для заявок
  document.getElementById("total-text").textContent = declensionWord(
    totalApplications,
    ["заявка", "заявки", "заявок"]
  );
  document.getElementById("in-progress-text").textContent = declensionWord(
    inProgressApplications,
    ["заявка", "заявки", "заявок"]
  );

  document.getElementById("completed-text").textContent = declensionWord(
    applicationsCompleted,
    ["заявка", "заявки", "заявок"]
  );

  // Склонение для изменений
  document.getElementById("changes-text").textContent = declensionWord(
    totalChanges,
    ["изменение", "изменения", "изменений"]
  );

  // Склонение для админов
  document.getElementById("admins-count-text").textContent = declensionWord(
    countAdmins,
    ["администратор", "администратора", "администраторов"]
  );

  // Склонение для врачей
  document.getElementById("doctors-count-text").textContent = declensionWord(
    countDoctors,
    ["врач", "врача", "врачей"]
  );

  // Склонение для дезинфекторов
  document.getElementById("disinfectors-count-text").textContent =
    declensionWord(countDisinfectors, [
      "дезинфектор",
      "дезинфектора",
      "дезинфекторов",
    ]);
}

// Вызов функции при загрузке страницы
document.addEventListener("DOMContentLoaded", updateText);
