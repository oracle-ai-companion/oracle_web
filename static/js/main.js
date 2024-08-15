document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM content loaded');
    const isLoggedIn = {{ logged_in|tojson }};
    console.log('isLoggedIn:', isLoggedIn);
    updateAuthButton(isLoggedIn);

    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const navItems = document.querySelectorAll('.nav-item');
    const knowledgebaseSubNav = document.getElementById('knowledgebase-sub-nav');

    menuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            navItems.forEach(navItem => navItem.classList.remove('active'));
            item.classList.add('active');

            if (item.dataset.page === 'knowledgebase') {
                knowledgebaseSubNav.style.display = 'block';
            } else {
                knowledgebaseSubNav.style.display = 'none';
            }
        });
    });
});

function updateAuthButton(loggedIn) {
    console.log('Updating auth button, logged in:', loggedIn);
    const authBtn = document.getElementById('auth-btn');
    if (authBtn) {
        if (loggedIn) {
            console.log('Setting button to Logout');
            authBtn.textContent = 'Logout';
            authBtn.href = '/logout';
        } else {
            console.log('Setting button to Login with Discord');
            authBtn.textContent = 'Login with Discord';
            authBtn.href = '/login';
        }
    } else {
        console.log('Auth button not found');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Oracle Bot Dashboard JavaScript loaded');

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add animation to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.transition = 'transform 0.3s ease-in-out';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });

    // Add scroll-based animation for sections
    const sections = document.querySelectorAll('section');
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
        observer.observe(section);
    });

    function updateAuthButton(loggedIn) {
        console.log('Updating auth button, logged in:', loggedIn);
        const authBtn = document.getElementById('auth-btn');
        if (authBtn) {
            if (loggedIn) {
                console.log('Setting button to Logout');
                authBtn.textContent = 'Logout';
                authBtn.href = '/logout';
            } else {
                console.log('Setting button to Login with Discord');
                authBtn.textContent = 'Login with Discord';
                authBtn.href = '/login';
            }
        } else {
            console.log('Auth button not found');
        }
    }

    // Call this function when the page loads
    const isLoggedIn = {{ 'true' if logged_in else 'false' }};
    console.log('DOMContentLoaded: isLoggedIn =', isLoggedIn);
    console.log('Session data:', {{ session|tojson }});
    updateAuthButton(isLoggedIn);

    const authBtn = document.getElementById('auth-btn');
    
    if (authBtn) {
        authBtn.addEventListener('click', (e) => {
            if (authBtn.textContent === 'Logout') {
                e.preventDefault();
                if (confirm('Are you sure you want to log out?')) {
                    window.location.href = authBtn.href;
                }
            }
        });
    }
});