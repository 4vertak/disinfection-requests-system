function updateAdminSignature(count) {
  const signatureElement = document.getElementById("adminSignature");
  let signatureText = "";

  switch (count) {
    case 0:
      signatureText = "Сайт работает на магии и кофе.";
      break;
    case 1:
      signatureText = "Один админ — это уже целый отдел.";
      break;
    case 2:
      signatureText = "Один работает, второй думает.";
      break;
    case 3:
      signatureText = "Один реальный, два виртуальных.";
      break;
    case 7:
      signatureText = "Как дней в неделе. И все на выходных.";
      break;
    case 42:
      signatureText =
        "Это ответ на главный вопрос жизни, вселенной и всего такого.";
      break;
    case 404:
      signatureText = "Админ не найден.";
      break;
    case 911:
      signatureText = "Срочная перезагрузка!";
      break;
    case 1000:
      signatureText = "Это уже дата-центр.";
      break;
    default:
      signatureText = `Они как целая армия.`;
      break;
  }

  signatureElement.textContent = signatureText;
}

/// Функция для подписи докторов с пасхалками
function updateDoctorSignature(count) {
  const signatureElement = document.getElementById("doctorSignature");
  let signatureText = "";

  switch (count) {
    case 0:
      signatureText = "Лечимся народными средствами и мемами.";
      break;
    case 1:
      signatureText = "Он как Доктор Хаус, только без трости.";
      break;
    case 7:
      signatureText = "Как дней в неделе. И все на выходных.";
      break;
    case 42:
      signatureText =
        "Это ответ на главный вопрос жизни, вселенной и всего такого.";
      break;
    case 404:
      signatureText = "Доктор не найден.";
      break;
    case 911:
      signatureText = "Срочный вызов!";
      break;
    case 1337:
      signatureText = "Хацкеры медицины.";
      break;
    default:
      signatureText = `Они как целая больница.`;
      break;
  }

  signatureElement.textContent = signatureText;
}

// Функция для подписи дезинфекторов с пасхалками
function updateDisinfectorSignature(count) {
  const signatureElement = document.getElementById("disinfectorSignature");
  let signatureText = "";

  switch (count) {
    case 0:
      signatureText = "Мы просто открываем окна и надеемся на лучшее.";
      break;
    case 1:
      signatureText = "Он как терминатор для микробов.";
      break;
    case 7:
      signatureText = "Как дней в неделе. И все в перчатках.";
      break;
    case 42:
      signatureText =
        "Это ответ на главный вопрос жизни, вселенной и всего такого.";
      break;
    case 404:
      signatureText = "Дезинфектор не найден.";
      break;
    case 911:
      signatureText = "Срочная уборка!";
      break;
    case 1337:
      signatureText = "Хацкеры чистоты.";
      break;
    default:
      signatureText = `Чистота — наше всё!`;
      break;
  }

  signatureElement.textContent = signatureText;
}
const adminCount = parseInt(
  document.getElementById("adminCount").textContent,
  10
);
const doctorCount = parseInt(
  document.getElementById("doctorCount").textContent,
  10
);
const disinfectorCount = parseInt(
  document.getElementById("disinfectorCount").textContent,
  10
);

// // Обновляем подписи
// updateAdminSignature(adminCount);
// updateDoctorSignature(doctorCount);
// updateDisinfectorSignature(disinfectorCount);

document.addEventListener("DOMContentLoaded", updateAdminSignature(adminCount));
document.addEventListener(
  "DOMContentLoaded",
  updateDoctorSignature(doctorCount)
);
document.addEventListener(
  "DOMContentLoaded",
  updateDisinfectorSignature(disinfectorCount)
);
