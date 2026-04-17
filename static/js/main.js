// TripCraft AI - Global JS

// ── Navigation Toggle ─────────────────────────────────────────────────────────
const navToggle = document.getElementById('nav-toggle');
const navMenu = document.getElementById('nav-menu');

if (navToggle && navMenu) {
  navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    navToggle.classList.toggle('active');
  });

  // Close menu when clicking outside
  document.addEventListener('click', (e) => {
    if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
      navMenu.classList.remove('active');
      navToggle.classList.remove('active');
    }
  });
}

// ── Navbar Scroll Effect ──────────────────────────────────────────────────────
const navbar = document.getElementById('navbar');
let lastScroll = 0;

if (navbar) {
  window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    // Add scrolled class when page is scrolled
    if (currentScroll > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }

    lastScroll = currentScroll;
  });
}

// ── Radio Card Active State ───────────────────────────────────────────────────
document.querySelectorAll('.radio-card input').forEach(input => {
  input.addEventListener('change', () => {
    const group = input.closest('.radio-grid, .radio-grid-2, .radio-grid-3, .radio-cards-2col');
    if (group) {
      group.querySelectorAll('.radio-card, .radio-card-lg').forEach(c => c.classList.remove('active'));
      input.closest('.radio-card, .radio-card-lg')?.classList.add('active');
    }
  });
});

// ── Scroll Animations ─────────────────────────────────────────────────────────
const observerOptions = {
  root: null,
  rootMargin: '0px',
  threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, observerOptions);

// ── Add animation classes to sections ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Add animate-on-scroll class to section elements with fade-in-up effect
  document.querySelectorAll('.step-card, .feature-card').forEach((el, index) => {
    el.classList.add('animate-on-scroll');
    el.style.transitionDelay = `${index * 0.1}s`;
    observer.observe(el);
  });

  // Also animate section headers
  document.querySelectorAll('.section-header').forEach((el) => {
    el.classList.add('animate-on-scroll');
    observer.observe(el);
  });

  // Auto-hide flash messages after 5 seconds
  const flashMessages = document.querySelectorAll('.flash-message');
  flashMessages.forEach((msg, index) => {
    setTimeout(() => {
      msg.style.transition = 'all 0.5s ease';
      msg.style.opacity = '0';
      msg.style.transform = 'translateX(100px)';
      setTimeout(() => msg.remove(), 500);
    }, 5000 + (index * 500));
  });
});

// ── Smooth Scroll for Anchor Links ────────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const href = this.getAttribute('href');
    if (href !== '#' && href.length > 1) {
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    }
  });
});

// ── Button Loading State ──────────────────────────────────────────────────────
function setButtonLoading(button, isLoading) {
  if (isLoading) {
    button.classList.add('loading');
    button.disabled = true;
  } else {
    button.classList.remove('loading');
    button.disabled = false;
  }
}

// ── Form Validation Enhancement ───────────────────────────────────────────────
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function showInputError(input, message) {
  const formGroup = input.closest('.form-group');
  if (formGroup) {
    let errorEl = formGroup.querySelector('.form-error');
    if (!errorEl) {
      errorEl = document.createElement('div');
      errorEl.className = 'form-error hidden';
      formGroup.appendChild(errorEl);
    }
    errorEl.textContent = message;
    errorEl.classList.remove('hidden');
    input.style.borderColor = 'var(--primary)';
  }
}

function clearInputError(input) {
  const formGroup = input.closest('.form-group');
  if (formGroup) {
    const errorEl = formGroup.querySelector('.form-error');
    if (errorEl) {
      errorEl.classList.add('hidden');
    }
    input.style.borderColor = 'var(--gray-200)';
  }
}
