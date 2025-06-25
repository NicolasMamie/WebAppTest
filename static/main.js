

document.addEventListener('DOMContentLoaded', function () {
    function handleFormSubmit(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(form);

            fetch('/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.preview_html !== undefined) {
                    document.getElementById('preview-section').innerHTML = data.preview_html;
                }
                if (data.chart_html !== undefined) {
                    document.getElementById('chart-section').innerHTML = data.chart_html;
                }
            });
        });
    }

    handleFormSubmit('reorder-form');
    handleFormSubmit('upload-form');
});
