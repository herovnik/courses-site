export default function Footer() {
  return (
    <footer className="bg-slate-950 text-slate-400 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          {/* Brand */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
                <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                  <path d="M6 12v5c3 3 9 3 12 0v-5" />
                </svg>
              </div>
              <div>
                <div className="text-white font-extrabold text-base">КурсоМир</div>
                <div className="text-[10px] text-violet-400 font-medium">агрегатор курсов</div>
              </div>
            </div>
            <p className="text-sm leading-relaxed text-slate-500">
              Помогаем найти лучшие онлайн-курсы для вашей карьеры и роста.
            </p>
          </div>

          {/* Catalog */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Каталог</h4>
            <ul className="space-y-2.5 text-sm">
              {["Программирование", "Дизайн", "Маркетинг", "Аналитика", "Менеджмент", "Финансы"].map((cat) => (
                <li key={cat}>
                  <a href="#catalog" className="hover:text-violet-400 transition-colors">{cat}</a>
                </li>
              ))}
            </ul>
          </div>

          {/* Schools */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Школы</h4>
            <ul className="space-y-2.5 text-sm">
              {["Яндекс Практикум", "Skillbox", "Нетология", "GeekBrains", "Coursera", "OTUS"].map((school) => (
                <li key={school}>
                  <a href="#catalog" className="hover:text-violet-400 transition-colors">{school}</a>
                </li>
              ))}
            </ul>
          </div>

          {/* Info */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Информация</h4>
            <ul className="space-y-2.5 text-sm">
              {["О сервисе", "Как мы выбираем", "Отзывы", "Помощь", "Контакты", "Политика конфиденциальности"].map((item) => (
                <li key={item}>
                  <a href="#" className="hover:text-violet-400 transition-colors">{item}</a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-slate-600">
            © 2025 КурсоМир. Все права защищены.
          </p>
          <div className="flex items-center gap-4">
            <span className="text-xs text-slate-600">Сделано с ❤️ для тех, кто учится</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
