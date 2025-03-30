// Обновление текста на странице
function updateText() {
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

  // Склонение для заявок
  document.getElementById("total-text").textContent = declensionWord(
    totalApplications,
    [" заявка", " заявки", " заявок"]
  );
  document.getElementById("in-progress-text").textContent = declensionWord(
    inProgressApplications,
    [" заявка", " заявки", " заявок"]
  );

  document.getElementById("completed-text").textContent = declensionWord(
    applicationsCompleted,
    [" заявка", " заявки", " заявок"]
  );
}

// Вызов функции при загрузке страницы
document.addEventListener("DOMContentLoaded", updateText);
