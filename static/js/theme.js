// Theme Management
const ThemeManager = {
    init() {
        // Check and apply initial theme
        this.applyTheme();
        // Set up event listeners
        this.setupEventListeners();
        // Update icons to match current theme
        this.updateIcons();
    },

    applyTheme() {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const storedTheme = localStorage.getItem('theme');
        const isDark = storedTheme === 'dark' || (!storedTheme && prefersDark);
        
        if (isDark) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        console.log('Theme applied:', isDark ? 'dark' : 'light');
    },

    toggleTheme() {
        const isDark = document.documentElement.classList.contains('dark');
        
        if (isDark) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            console.log('Changed to light theme');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            console.log('Changed to dark theme');
        }
        
        this.updateIcons();
    },

    updateIcons() {
        const isDark = document.documentElement.classList.contains('dark');
        const lightIcon = document.getElementById('theme-toggle-light-icon');
        const darkIcon = document.getElementById('theme-toggle-dark-icon');
        
        if (lightIcon && darkIcon) {
            if (isDark) {
                lightIcon.classList.add('hidden');
                darkIcon.classList.remove('hidden');
            } else {
                lightIcon.classList.remove('hidden');
                darkIcon.classList.add('hidden');
            }
        }
    },

    setupEventListeners() {
        const themeToggleBtn = document.getElementById('theme-toggle');
        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', () => this.toggleTheme());
        }

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (!localStorage.getItem('theme')) {
                if (e.matches) {
                    document.documentElement.classList.add('dark');
                } else {
                    document.documentElement.classList.remove('dark');
                }
                this.updateIcons();
            }
        });
    }
};

// Initialize theme management when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
});
