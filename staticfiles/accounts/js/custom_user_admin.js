document.addEventListener('DOMContentLoaded', function () {
    const isTeacherCheckbox = document.querySelector('#id_is_teacher');
    const subjectsTaughtRow = document.querySelector('.form-row.field-subjects_taught');

    function toggleSubjectsTaught() {
        if (isTeacherCheckbox.checked) {
            subjectsTaughtRow.style.display = '';
        } else {
            subjectsTaughtRow.style.display = 'none';
        }
    }

    if (isTeacherCheckbox && subjectsTaughtRow) {
        toggleSubjectsTaught();
        isTeacherCheckbox.addEventListener('change', toggleSubjectsTaught);
    }
});
