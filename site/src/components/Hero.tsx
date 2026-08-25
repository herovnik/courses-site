export default function Hero() {
  return (
    <section className="relative pt-32 pb-20 overflow-hidden bg-gradient-to-br from-slate-950 via-violet-950 to-indigo-950">
      {/* Background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-[700px] h-[700px] bg-violet-600/20 rounded-full blur-[120px]" />
        <div className="absolute -bottom-40 -left-40 w-[600px] h-[600px] bg-indigo-600/20 rounded-full blur-[120px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-purple-800/10 rounded-full blur-[80px]" />
        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)",
            backgroundSize: "60px 60px",
          }}
        />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6">
        <div className="text-center max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-violet-500/15 border border-violet-500/30 text-violet-300 text-sm font-medium px-4 py-2 rounded-full mb-8 backdrop-blur-sm">
            <span className="w-2 h-2 bg-violet-400 rounded-full animate-pulse" />
            Более 500 курсов от ведущих школ
          </div>

          {/* Heading */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white mb-6 leading-tight tracking-tight">
            Найди идеальный{" "}
            <span className="relative">
              <span className="bg-gradient-to-r from-violet-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
                онлайн-курс
              </span>
              <svg
                className="absolute -bottom-1 left-0 right-0 w-full"
                viewBox="0 0 300 8"
                fill="none"
              >
                <path
                  d="M0 5 Q75 0 150 5 Q225 10 300 5"
                  stroke="url(#underlineGrad)"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  fill="none"
                />
                <defs>
                  <linearGradient id="underlineGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#8b5cf6" />
                    <stop offset="100%" stopColor="#6366f1" />
                  </linearGradient>
                </defs>
              </svg>
            </span>{" "}
            <br className="hidden sm:block" />
            для твоей карьеры
          </h1>

          <p className="text-lg text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Сравниваем курсы от Яндекс Практикума, Skillbox, Нетологии и других
            топовых школ. Фильтруй по цене, длительности и уровню — выбирай
            лучшее.
          </p>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-14">
            <a
              href="#catalog"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold px-8 py-4 rounded-2xl shadow-xl shadow-violet-900/50 hover:from-violet-500 hover:to-indigo-500 transition-all hover:scale-105 hover:shadow-violet-800/60"
            >
              Смотреть все курсы
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                strokeWidth={2}
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M17 8l4 4m0 0l-4 4m4-4H3"
                />
              </svg>
            </a>
            <a
              href="#categories"
              className="inline-flex items-center gap-2 text-slate-300 font-medium px-6 py-4 rounded-2xl border border-white/10 hover:border-violet-500/50 hover:text-white hover:bg-white/5 transition-all"
            >
              По категориям
            </a>
          </div>

          {/* Floating school badges */}
          <div className="flex flex-wrap items-center justify-center gap-3">
            {[
              { name: "Яндекс Практикум", color: "from-yellow-500/20 to-orange-500/20", border: "border-yellow-500/20", text: "text-yellow-300", abbr: "ЯП" },
              { name: "Skillbox", color: "from-green-500/20 to-emerald-500/20", border: "border-green-500/20", text: "text-green-300", abbr: "SB" },
              { name: "Нетология", color: "from-blue-500/20 to-cyan-500/20", border: "border-blue-500/20", text: "text-blue-300", abbr: "НТ" },
              { name: "GeekBrains", color: "from-red-500/20 to-pink-500/20", border: "border-red-500/20", text: "text-red-300", abbr: "GB" },
              { name: "Coursera", color: "from-cyan-500/20 to-blue-500/20", border: "border-cyan-500/20", text: "text-cyan-300", abbr: "CR" },
              { name: "OTUS", color: "from-violet-500/20 to-purple-500/20", border: "border-violet-500/20", text: "text-violet-300", abbr: "OT" },
            ].map((school) => (
              <div
                key={school.name}
                className={`flex items-center gap-2 bg-gradient-to-r ${school.color} border ${school.border} backdrop-blur-sm px-3 py-1.5 rounded-full`}
              >
                <div className={`w-5 h-5 rounded-md bg-gradient-to-br ${school.color} flex items-center justify-center`}>
                  <span className={`text-[8px] font-bold ${school.text}`}>{school.abbr}</span>
                </div>
                <span className="text-xs text-slate-300 font-medium">{school.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom fade */}
      <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-slate-50 to-transparent" />
    </section>
  );
}
