function renderSidebar() {
    const container = document.getElementById('sidebar-container');
    if (!container) return;

    const currentTheme = localStorage.getItem('mq_theme') || 'dark';
    const currentAccent = localStorage.getItem('mq_accent') || '#38bdf8';

    container.innerHTML = `
        <aside class="w-64 min-h-screen p-4 flex flex-col justify-between border-r" style="border-color: var(--border-color); background-color: var(--bg-card);">
            <div class="space-y-6">
                <!-- App Title / Brand -->
                <div class="flex items-center gap-2 px-2">
                    <span class="text-xl">🚀</span>
                    <span class="font-black text-lg tracking-wider" style="color: var(--text-main)">MoneyQuest.AI</span>
                </div>

                <!-- Main Navigation Links -->
                <nav class="space-y-1 text-xs font-bold">
                    <div class="nav-section-label">Explore / 01</div>
                    <a href="/terminal" class="nav-chapter" style="color: var(--text-main)"><span>01</span><b>Terminal</b><em>↗</em></a>
                    <a href="/budget" class="nav-chapter" style="color: var(--text-main)"><span>02</span><b>Budget Planner</b><em>↗</em></a>
                    <a href="/credit" class="nav-chapter" style="color: var(--text-main)"><span>03</span><b>Debt Engine</b><em>↗</em></a>
                    <a href="/news" class="nav-chapter" style="color: var(--text-main)"><span>04</span><b>Market News</b><em>↗</em></a>
                    <div class="nav-section-label nav-section-spacer">Learn / 02</div>
                    <a href="/chatbot" class="nav-chapter" style="color: var(--text-main)"><span>05</span><b>AI Advisor</b><em>↗</em></a>
                    <a href="/quiz" class="nav-chapter" style="color: var(--text-main)"><span>06</span><b>Financial Literacy</b><em>↗</em></a>
                    <a href="/roadmap" class="nav-chapter" style="color: var(--text-main)"><span>07</span><b>Roadmap Lab</b><em>↗</em></a>
                    <div class="nav-section-label nav-section-spacer">Extras / 03</div>
                    <a href="/store" class="nav-chapter" style="color: var(--text-main)"><span>08</span><b>MoneyQuest Store</b><em>↗</em></a>
                </nav>
            </div>

            <!-- Global UI Theme & Color Controls -->
            <div class="pt-4 border-t space-y-3" style="border-color: var(--border-color);">
                <div class="text-[10px] uppercase font-extrabold tracking-wider" style="color: var(--text-muted)">UI Customizer</div>
                
                <!-- Theme Toggle Button -->
                <button id="theme-toggle-btn" onclick="toggleGlobalTheme()" class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-bold border" style="border-color: var(--border-color); color: var(--text-main);">
                    <span>Mode</span>
                    <span id="theme-icon-label">${currentTheme === 'dark' ? '🌙 Dark' : '☀️ Light'}</span>
                </button>

                <!-- Dynamic Accent Color Picker -->
                <div class="flex items-center justify-between px-3 py-2 rounded-xl border text-xs font-bold" style="border-color: var(--border-color); color: var(--text-main);">
                    <span>Accent</span>
                    <input type="color" id="accent-color-picker" value="${currentAccent}" oninput="updateAccentColor(this.value)" class="w-6 h-6 rounded cursor-pointer border-0 bg-transparent">
                </div>
            </div>
        </aside>
    `;

    applyTheme(currentTheme);
    updateAccentColor(currentAccent, false);

    const activePath = window.location.pathname;
    container.querySelectorAll('nav a').forEach(link => {
        if (link.getAttribute('href') === activePath) link.setAttribute('aria-current', 'page');
    });
}

function toggleGlobalTheme() {
    const activeTheme = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    applyTheme(activeTheme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('mq_theme', theme);
    
    const label = document.getElementById('theme-icon-label');
    if (label) {
        label.innerText = theme === 'dark' ? '🌙 Dark' : '☀️ Light';
    }
}

function updateAccentColor(hexColor, save = true) {
    if (save) localStorage.setItem('mq_accent', hexColor);
    
    document.documentElement.style.setProperty('--accent-color', hexColor);

    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hexColor);
    if (result) {
        const r = parseInt(result[1], 16), g = parseInt(result[2], 16), b = parseInt(result[3], 16);
        const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
        document.documentElement.style.setProperty('--accent-text', yiq >= 128 ? '#020617' : '#ffffff');
    }
}

document.addEventListener('DOMContentLoaded', renderSidebar);