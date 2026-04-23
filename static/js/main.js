document.addEventListener('DOMContentLoaded', function() {
    console.log("MSU Library System Loaded");
    
    // Example: Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => alert.style.display = 'none');
        }, 5000);
    }
});