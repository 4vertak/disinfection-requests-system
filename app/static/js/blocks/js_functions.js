function declensionWord(number, words) {
  number = Math.abs(number) % 100;
  const remainder = number % 10;
  if (number > 10 && number < 20) return words[2];
  if (remainder > 1 && remainder < 5) return words[1];
  if (remainder === 1) return words[0];
  return words[2];
}

function formatTimer(value_seconds) {
  const total_seconds = Math.round(value_seconds);
  const minutes = Math.floor(total_seconds / 60);
  const seconds = total_seconds % 60;
  const formattedMinutes = minutes < 10 ? `0${minutes}` : minutes;
  const formattedSeconds = seconds < 10 ? `0${seconds}` : seconds;
  const wordsMinutes = [" минута ", " минуты ", " минут "];
  const wordsSeconds = ["секунда ", "секунды ", " секунд"];
  return `${formattedMinutes} ${declensionWord(
    minutes,
    wordsMinutes
  )}  ${formattedSeconds}  ${declensionWord(seconds, wordsSeconds)}`;
}
