function toggleAreaField() {
    var userTypeSelect = document.getElementById('user_type');
    var areaField = document.getElementById('areaField');
    if (userTypeSelect.value === 'doctor') {
        areaField.style.display = 'block';
    } else {
        areaField.style.display = 'none';
    }
}

document.addEventListener("DOMContentLoaded", function () {
    toggleAreaField();
});