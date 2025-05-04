// You can add any custom JavaScript here if needed
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Set today's date as default for date fields
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('expiry_date').min = today;
});