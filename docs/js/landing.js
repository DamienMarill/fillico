/**
 * 🍭 Fillico Landing Page - JavaScript
 * Interactions et animations
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavToggle();
    initSmoothScroll();
    initScrollAnimations();
    initMascotInteraction();
});

/**
 * Navigation mobile toggle
 */
function initNavToggle() {
    const toggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (toggle && navLinks) {
        toggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            toggle.classList.toggle('active');
        });
        
        // Fermer le menu au clic sur un lien
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                toggle.classList.remove('active');
            });
        });
    }
}

/**
 * Smooth scroll pour les ancres
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = target.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Animations au scroll (Intersection Observer)
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observer les éléments à animer
    const animatedElements = document.querySelectorAll(
        '.feature-card, .mascot-state, .demo-step, .download-card'
    );
    
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(el);
    });
    
    // Style pour l'animation
    const style = document.createElement('style');
    style.textContent = `
        .animate-in {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);
}

/**
 * Interaction avec la mascotte
 */
function initMascotInteraction() {
    const mascot = document.querySelector('.mascot-img');
    const speech = document.querySelector('.mascot-speech');
    
    const expressions = [
        '( ≧◡≦ )',
        '( • ᴗ • )',
        '( ◕ ω ◕ )',
        '( ✧ω✧ )',
        '( ^o^ )',
    ];
    
    if (mascot && speech) {
        mascot.addEventListener('click', () => {
            // Animation de bounce
            mascot.style.animation = 'none';
            mascot.offsetHeight; // Trigger reflow
            mascot.style.animation = 'bounce 0.5s ease';
            
            // Changer l'expression
            const randomExpr = expressions[Math.floor(Math.random() * expressions.length)];
            speech.textContent = randomExpr;
            
            // Animation du speech bubble
            speech.style.transform = 'scale(1.2)';
            setTimeout(() => {
                speech.style.transform = 'scale(1)';
            }, 200);
        });
    }
}

/**
 * Header shrink on scroll
 */
window.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    if (window.scrollY > 100) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Ajouter le style pour le header scrolled
const headerStyle = document.createElement('style');
headerStyle.textContent = `
    .header.scrolled {
        padding: 0.5rem 0;
        box-shadow: 0 4px 20px rgba(244, 114, 182, 0.2);
    }
`;
document.head.appendChild(headerStyle);
