function renderSidebar() {
    const container = document.getElementById('sidebar-container');
    if (!container) return;

    const currentTheme = localStorage.getItem('mq_theme') || 'dark';
    const currentAccent = localStorage.getItem('mq_accent') || '#38bdf8';

    container.innerHTML = `
        <!-- Mobile Menu Toggle Button -->
        <button id="mobile-menu-toggle" class="fixed md:hidden top-4 left-4 z-50 w-10 h-10 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center text-xl hover:bg-white/20 transition" onclick="toggleMobileSidebar()">☰</button>

        <!-- Overlay for mobile -->
        <div id="sidebar-overlay" class="hidden md:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-30" onclick="closeMobileSidebar()"></div>

        <!-- Sidebar -->
        <aside id="mobile-sidebar" class="w-64 min-h-screen p-4 flex flex-col justify-between border-r fixed md:static left-0 top-0 h-screen z-40 md:z-auto transition-transform duration-300 -translate-x-full md:translate-x-0" style="border-color: var(--border-color); background-color: var(--bg-card);">
            <div class="space-y-6">
                <div class="flex items-center gap-2 px-2 justify-between">
                    <div class="flex items-center gap-2">
                        <span class="text-xl">🚀</span>
                        <span class="font-black text-lg tracking-wider" style="color: var(--text-main)">MoneyQuest.AI</span>
                    </div>
                    <button class="md:hidden text-2xl text-slate-400 hover:text-white" onclick="closeMobileSidebar()">✕</button>
                </div>

                <nav class="space-y-1 text-xs font-bold">
                    <a href="/terminal" onclick="closeMobileSidebar()" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/10 transition" style="color: var(--text-main)">📈 Terminal</a>
                    <a href="/budget" onclick="closeMobileSidebar()" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/10 transition" style="color: var(--text-main)">📊 Budget Planner</a>
                    <a href="/credit" onclick="closeMobileSidebar()" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/10 transition" style="color: var(--text-main)">💳 Debt Engine</a>
                    <a href="/news" onclick="closeMobileSidebar()" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/10 transition" style="color: var(--text-main)">📰 Market News</a>
                    <a href="/chatbot" onclick="closeMobileSidebar()" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/10 transition" style="color: var(--text-main)">🤖 AI Advisor</a>
                    <a href="/quiz" onclick="closeMobileSidebar()" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/10 transition" style="color: var(--text-main)">🎯 Quiz</a>
                </nav>
            </div>

            <div class="pt-4 border-t space-y-3" style="border-color: var(--border-color);">
                <div class="text-[10px] uppercase font-extrabold tracking-wider" style="color: var(--text-muted)">UI Customizer</div>
                
                <button id="theme-toggle-btn" onclick="toggleGlobalTheme()" class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-bold border transition" style="border-color: var(--border-color); color: var(--text-main);">
                    <span>Mode</span>
                    <span id="theme-icon-label">${currentTheme === 'dark' ? '🌙 Dark' : '☀️ Light'}</span>
                </button>

                <div class="flex items-center justify-between px-3 py-2 rounded-xl border text-xs font-bold" style="border-color: var(--border-color); color: var(--text-main);">
                    <span>Accent</span>
                    <input type="color" id="accent-color-picker" value="${currentAccent}" oninput="updateAccentColor(this.value)" class="w-6 h-6 rounded cursor-pointer border-0 bg-transparent">
                </div>
            </div>
        </aside>
    `;

    applyTheme(currentTheme);
    updateAccentColor(currentAccent, false);
}

function toggleMobileSidebar() {
    const sidebar = document.getElementById('mobile-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    sidebar.classList.toggle('-translate-x-full');
    overlay.classList.toggle('hidden');
}

function closeMobileSidebar() {
    const sidebar = document.getElementById('mobile-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    sidebar.classList.add('-translate-x-full');
    overlay.classList.add('hidden');
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

// Close sidebar when pressing Escape on mobile
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeMobileSidebar();
    }
});

document.addEventListener('DOMContentLoaded', renderSidebar);