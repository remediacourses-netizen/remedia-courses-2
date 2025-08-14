function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function () {
    const subjectSelect = document.getElementById('id_subject');
    const teacherSelect = document.getElementById('id_teacher');
    const csrftoken = getCookie('csrftoken');

    if (!subjectSelect || !teacherSelect) return;

    function updateTeachers(subjectId) {
        if (!subjectId) {
            teacherSelect.innerHTML = '<option value="">---------</option>';
            return;
        }
        fetch(`/admin/accounts/usersubject/get_teachers/${subjectId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        })
            .then(response => response.json())
            .then(data => {
                teacherSelect.innerHTML = '<option value="">---------</option>';
                data.forEach(teacher => {
                    const opt = document.createElement('option');
                    opt.value = teacher.id;
                    opt.textContent = teacher.name;
                    teacherSelect.appendChild(opt);
                });
            })
            .catch(() => {
                teacherSelect.innerHTML = '<option value="">---------</option>';
            });
    }

    subjectSelect.addEventListener('change', function () {
        updateTeachers(this.value);
    });

    // Если выбран предмет при загрузке, подгружаем сразу учителей
    if (subjectSelect.value) {
        updateTeachers(subjectSelect.value);
    }
});
