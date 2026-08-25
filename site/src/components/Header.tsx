import { useState } from "react";

const navLinks = [
  { label: "Каталог", href: "#catalog" },
  { label: "Категории", href: "#categories" },
  { label: "Подборки", href: "#featured" },
  { label: "О сервисе", href: "#about" },
];

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <a href="#" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-200 group-hover:shadow-violet-300 transition-shadow">
              <svg
                className="w-5 h-5 text-white"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={2.2}
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                <path d="M6 12v5c3 3 9 3 12 0v-5" />
              </svg>
            </div>
            <div className="flex flex-col leading-none">
              <span className="text-[17px] font-800 text-slate-900 tracking-tight font-extrabold">
                КурсоМир
              </span>
              <span className="text-[10px] text-violet-500 font-medium tracking-wide">
                агрегатор курсов
              </span>
            </div>
          </a>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-6">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-sm font-medium text-slate-600 hover:text-violet-600 transition-colors relative group"
              >
                {link.label}
                <span className="absolute -bottom-0.5 left-0 right-0 h-0.5 bg-violet-500 scale-x-0 group-hover:scale-x-100 transition-transform origin-left rounded-full" />
              </a>
            ))}
          </nav>

          {/* Right side */}
          <div className="hidden md:flex items-center gap-3">
            <button className="text-sm font-medium text-slate-600 hover:text-violet-600 px-3 py-2 rounded-lg hover:bg-violet-50 transition-all">
              Войти
            </button>
            <button className="text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-2 rounded-xl hover:from-violet-700 hover:to-indigo-700 transition-all shadow-md shadow-violet-200 hover:shadow-violet-300">
              Попробовать бесплатно
            </button>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
            >
              {menuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden py-4 border-t border-slate-100 space-y-2">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="block text-sm font-medium text-slate-600 hover:text-violet-600 py-2 px-2 rounded-lg hover:bg-violet-50 transition-all"
                onClick={() => setMenuOpen(false)}
              >
                {link.label}
              </a>
            ))}
            <div className="pt-2 flex flex-col gap-2">
              <button className="text-sm font-medium text-slate-600 py-2 px-4 rounded-xl border border-slate-200 hover:border-violet-300 transition-all">
                Войти
              </button>
              <button className="text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-indigo-600 py-2 px-4 rounded-xl">
                Попробовать бесплатно
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
