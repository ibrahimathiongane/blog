document.addEventListener('DOMContentLoaded', () => {
    // ── Mobile Menu Toggle ──
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // ── Copy URL to Clipboard ──
    const copyUrlBtn = document.getElementById('copy-url-btn');
    if (copyUrlBtn) {
        copyUrlBtn.addEventListener('click', () => {
            const url = copyUrlBtn.getAttribute('data-url');
            navigator.clipboard.writeText(url).then(() => {
                const originalText = copyUrlBtn.innerHTML;
                copyUrlBtn.innerHTML = '✅ Copié !';
                setTimeout(() => {
                    copyUrlBtn.innerHTML = originalText;
                }, 2000);
            });
        });
    }

    // ── Theme Toggle (Light/Dark) ──
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    // Check for saved theme in localStorage
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Apply theme
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        htmlElement.classList.add('dark');
    } else {
        htmlElement.classList.remove('dark');
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const isDark = htmlElement.classList.toggle('dark');
            const theme = isDark ? 'dark' : 'light';
            htmlElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            updateThemeIcon();
        });

        // Initialize icon
        updateThemeIcon();
    }

    function updateThemeIcon() {
        if (!themeToggleBtn) return;
        const isDark = htmlElement.classList.contains('dark');
        const sunIcon = themeToggleBtn.querySelector('.sun-icon');
        const moonIcon = themeToggleBtn.querySelector('.moon-icon');
        
        if (isDark) {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        } else {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        }
    }

    // ── TOC Generation (Article Page) ──
    const tocContainer = document.getElementById('toc-container');
    const articleContent = document.querySelector('.prose-article');

    if (tocContainer && articleContent) {
        const headings = articleContent.querySelectorAll('h2, h3');
        if (headings.length > 0) {
            const tocList = document.createElement('ul');
            tocList.className = 'space-y-2';

            headings.forEach((heading, index) => {
                // Ensure heading has an ID
                if (!heading.id) {
                    heading.id = `heading-${index}`;
                }

                const li = document.createElement('li');
                li.className = heading.tagName === 'H3' ? 'pl-4' : '';

                const a = document.createElement('a');
                a.href = `#${heading.id}`;
                a.textContent = heading.textContent.replace('¶', '').trim();
                a.className = 'hover:text-brand-400 transition-colors block py-0.5';

                li.appendChild(a);
                tocList.appendChild(li);
            });

            tocContainer.innerHTML = '';
            tocContainer.appendChild(tocList);
        } else {
            const aside = tocContainer.closest('aside');
            if (aside) aside.classList.add('hidden');
        }
    }
});
