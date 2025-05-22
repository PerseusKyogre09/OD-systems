// Main JavaScript functionality for OD System

// Initialize UI components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize ScrollCue.js for animations
    if (typeof scrollCue !== 'undefined') {
        scrollCue.init({
            duration: 600,
            interval: -100,
            percentage: 0.75,
            docSlider: false,
            pageChangeReset: false
        });
    }

    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('border-red-500');
                    
                    // Create error message if it doesn't exist
                    if (!field.nextElementSibling?.classList.contains('error-message')) {
                        const errorMsg = document.createElement('p');
                        errorMsg.classList.add('error-message', 'text-red-500', 'text-sm', 'mt-1');
                        errorMsg.textContent = 'This field is required';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                } else {
                    field.classList.remove('border-red-500');
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg?.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });

    // Flash message auto-dismiss
    setTimeout(function() {
        document.querySelectorAll('[role="alert"]').forEach(function(alert) {
            alert.remove();
        });
    }, 5000);
    
    // Document preview (if applicable)
    const fileInput = document.querySelector('input[type="file"]');
    const preview = document.getElementById('document-preview');

    if (fileInput && preview) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    preview.src = e.target.result;
                    preview.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        });
    }
});
