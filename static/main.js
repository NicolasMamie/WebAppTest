
document.addEventListener('DOMContentLoaded', function () {
    function handleFormSubmit(formId) {
        document.getElementById(formId).addEventListener('submit', function (e) {
            e.preventDefault();  // Prevent full reload

            const formData = new FormData(this);

            fetch('/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(html => {
                document.open();
                document.write(html);
                document.close();
            });
        });
    }

    handleFormSubmit('upload-form');
    handleFormSubmit('initial-form');
});

