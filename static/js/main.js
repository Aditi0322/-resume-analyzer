// Show mobile nav only on small screens
function checkMobileNav() {
    const nav = document.getElementById('mobileNav');
    if (nav) {
        if (window.innerWidth <= 768) {
            nav.style.display = 'flex';
        } else {
            nav.style.display = 'none';
        }
    }
}

checkMobileNav();
window.addEventListener('resize', checkMobileNav);


// =============================================
// THEME TOGGLE
// =============================================

const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', savedTheme);
updateToggleIcon(savedTheme);

function updateToggleIcon(theme) {
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'dark'
            ? '☀️ Light'
            : '🌙 Dark';
    }
}

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const current = html.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateToggleIcon(next);
    });
}

// =============================================
// ANIMATE PROGRESS BARS ON LOAD
// =============================================

document.addEventListener('DOMContentLoaded', () => {
    const fills = document.querySelectorAll('.progress-fill');
    fills.forEach(fill => {
        const width = fill.getAttribute('data-width');
        setTimeout(() => {
            fill.style.width = width + '%';
        }, 300);
    });
});

// =============================================
// FILE UPLOAD DRAG & DROP
// =============================================

const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const fileLabel = document.getElementById('fileLabel');

if (uploadZone && fileInput) {
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = 'var(--primary)';
        uploadZone.style.transform = 'scale(1.02)';
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.style.borderColor = 'var(--border)';
        uploadZone.style.transform = 'scale(1)';
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            updateFileName(files[0].name);
        }
        uploadZone.style.borderColor = 'var(--border)';
        uploadZone.style.transform = 'scale(1)';
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            updateFileName(fileInput.files[0].name);
        }
    });

    function updateFileName(name) {
        if (fileLabel) {
            fileLabel.textContent = '✅ ' + name;
            fileLabel.style.color = 'var(--primary)';
            fileLabel.style.fontWeight = '600';
        }
    }
}
