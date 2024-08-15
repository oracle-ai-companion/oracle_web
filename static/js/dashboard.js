// dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard.js loaded');

    // Function to handle sidebar toggle
    function toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('open');
    }

    // Add event listener to sidebar toggle button
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // Function to handle form submission
    function handleFormSubmit(event) {
        event.preventDefault();
        console.log('Form submitted');
        // Add your form submission logic here
    }

    // Add event listener to settings form
    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', handleFormSubmit);
    }

    // You can add more dashboard-specific JavaScript functionality here
});