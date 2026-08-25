import { schools } from "../data/courses";

export type Filters = {
  priceMin: number;
  priceMax: number;
  durationMin: number;
  durationMax: number;
  selectedSchools: string[];
  level: string;
  sortBy: string;
};

type Props = {
  filters: Filters;
  onChange: (filters: Filters) => void;
  totalCount: number;
};

// Price range constants - updated based on actual data
export const PRICE_MAX = 25000;
export const PRICE_DEFAULT_MAX = 20000;

const levelOptions = ["Любой", "Начинающий", "Средний", "Продвинутый"];
const sortOptions = [
  { value: "rating", label: "По рейтингу" },
  { value: "price_asc", label: "Сначала дешевле" },
  { value: "price_desc", label: "Сначала дороже" },
  { value: "duration_asc", label: "Самые короткие" },
  { value: "popular", label: "По популярности" },
];

const schoolColors: Record<string, string> = {
  "Яндекс Практикум": "bg-yellow-100 text-yellow-700 border-yellow-200",
  Skillbox: "bg-green-100 text-green-700 border-green-200",
  GeekBrains: "bg-red-100 text-red-700 border-red-200",
  Нетология: "bg-blue-100 text-blue-700 border-blue-200",
  Coursera: "bg-cyan-100 text-cyan-700 border-cyan-200",
  OTUS: "bg-violet-100 text-violet-700 border-violet-200",
};

export default function FilterSidebar({ filters, onChange, totalCount }: Props) {
  const toggleSchool = (school: string) => {
    const updated = filters.selectedSchools.includes(school)
      ? filters.selectedSchools.filter((s) => s !== school)
      : [...filters.selectedSchools, school];
    onChange({ ...filters, selectedSchools: updated });
  };

  const resetFilters = () => {
    onChange({
      priceMin: 0,
      priceMax: PRICE_DEFAULT_MAX,
      durationMin: 1,
      durationMax: 24,
      selectedSchools: [],
      level: "Любой",
      sortBy: "rating",
    });
  };

  return (
    <aside className="w-full lg:w-72 xl:w-80 flex-shrink-0">
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden sticky top-36">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg
              className="w-4 h-4 text-violet-600"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2a1 1 0 01-.293.707L13 13.414V19a1 1 0 01-.553.894l-4 2A1 1 0 017 21v-7.586L3.293 6.707A1 1 0 013 6V4z"
              />
            </svg>
            <h2 className="text-sm font-bold text-slate-800">Фильтры</h2>
            <span className="bg-violet-100 text-violet-700 text-xs font-semibold px-2 py-0.5 rounded-full">
              {totalCount}
            </span>
          </div>
          <button
            onClick={resetFilters}
            className="text-xs text-slate-400 hover:text-violet-600 transition-colors font-medium"
          >
            Сбросить
          </button>
        </div>

        <div className="p-5 space-y-6 max-h-[calc(100vh-200px)] overflow-y-auto">
          {/* Sort */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
              Сортировка
            </label>
            <div className="space-y-1.5">
              {sortOptions.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => onChange({ ...filters, sortBy: opt.value })}
                  className={`w-full text-left px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                    filters.sortBy === opt.value
                      ? "bg-violet-600 text-white shadow-sm"
                      : "text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Price Range */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
              Стоимость в месяц
            </label>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="flex-1">
                  <label className="text-[10px] text-slate-400 font-medium block mb-1">От</label>
                  <div className="relative">
                    <input
                      type="number"
                      value={filters.priceMin}
                      min={0}
                      max={filters.priceMax}
                      onChange={(e) =>
                        onChange({
                          ...filters,
                          priceMin: Number(e.target.value),
                        })
                      }
                      className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400">₽</span>
                  </div>
                </div>
                <div className="flex-1">
                  <label className="text-[10px] text-slate-400 font-medium block mb-1">До</label>
                  <div className="relative">
                    <input
                      type="number"
                      value={filters.priceMax}
                      min={filters.priceMin}
                      max={PRICE_MAX}
                      onChange={(e) =>
                        onChange({
                          ...filters,
                          priceMax: Number(e.target.value),
                        })
                      }
                      className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400">₽</span>
                  </div>
                </div>
              </div>
              <input
                type="range"
                min={0}
                max={PRICE_MAX}
                value={filters.priceMax}
                onChange={(e) =>
                  onChange({ ...filters, priceMax: Number(e.target.value) })
                }
                className="w-full accent-violet-600 cursor-pointer"
              />
              <div className="flex justify-between text-xs text-slate-400">
                <span>0 ₽</span>
                <span>{PRICE_MAX.toLocaleString("ru-RU")} ₽</span>
              </div>
            </div>
          </div>

          {/* Duration */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
              Длительность
            </label>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="flex-1">
                  <label className="text-[10px] text-slate-400 font-medium block mb-1">От (мес)</label>
                  <input
                    type="number"
                    value={filters.durationMin}
                    min={1}
                    max={filters.durationMax}
                    onChange={(e) =>
                      onChange({
                        ...filters,
                        durationMin: Number(e.target.value),
                      })
                    }
                    className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
                  />
                </div>
                <div className="flex-1">
                  <label className="text-[10px] text-slate-400 font-medium block mb-1">До (мес)</label>
                  <input
                    type="number"
                    value={filters.durationMax}
                    min={filters.durationMin}
                    max={24}
                    onChange={(e) =>
                      onChange({
                        ...filters,
                        durationMax: Number(e.target.value),
                      })
                    }
                    className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
                  />
                </div>
              </div>
              <div className="flex gap-2 flex-wrap">
                {[
                  { label: "До 3 мес", min: 1, max: 3 },
                  { label: "3–6 мес", min: 3, max: 6 },
                  { label: "6–12 мес", min: 6, max: 12 },
                  { label: "Год+", min: 12, max: 24 },
                ].map((preset) => (
                  <button
                    key={preset.label}
                    onClick={() =>
                      onChange({
                        ...filters,
                        durationMin: preset.min,
                        durationMax: preset.max,
                      })
                    }
                    className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-all ${
                      filters.durationMin === preset.min &&
                      filters.durationMax === preset.max
                        ? "border-violet-500 bg-violet-50 text-violet-700"
                        : "border-slate-200 text-slate-500 hover:border-violet-300 hover:text-violet-600"
                    }`}
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Schools */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
              Школа
            </label>
            <div className="space-y-2">
              {schools.map((school) => {
                const active = filters.selectedSchools.includes(school);
                return (
                  <button
                    key={school}
                    onClick={() => toggleSchool(school)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border transition-all text-left ${
                      active
                        ? "border-violet-400 bg-violet-50"
                        : "border-slate-100 hover:border-slate-200 bg-white"
                    }`}
                  >
                    <div
                      className={`w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-bold flex-shrink-0 border ${
                        schoolColors[school] || "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {school.slice(0, 2)}
                    </div>
                    <span
                      className={`text-sm font-medium flex-1 ${
                        active ? "text-violet-700" : "text-slate-700"
                      }`}
                    >
                      {school}
                    </span>
                    <div
                      className={`w-4 h-4 rounded border-2 flex-shrink-0 flex items-center justify-center transition-all ${
                        active
                          ? "border-violet-600 bg-violet-600"
                          : "border-slate-200"
                      }`}
                    >
                      {active && (
                        <svg
                          className="w-2.5 h-2.5 text-white"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth={3}
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Level */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
              Уровень
            </label>
            <div className="grid grid-cols-2 gap-2">
              {levelOptions.map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => onChange({ ...filters, level: lvl })}
                  className={`px-3 py-2 rounded-xl text-sm font-medium border transition-all ${
                    filters.level === lvl
                      ? "border-violet-500 bg-violet-50 text-violet-700"
                      : "border-slate-200 text-slate-600 hover:border-violet-300"
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
