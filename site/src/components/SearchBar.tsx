type Props = {
  query: string;
  onChange: (q: string) => void;
  total: number;
  filtered: number;
};

export default function SearchBar({ query, onChange, total, filtered }: Props) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center gap-3">
      <div className="relative flex-1">
        <svg
          className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Поиск курсов: React, Python, дизайн..."
          className="w-full pl-12 pr-4 py-3.5 bg-white border border-slate-200 rounded-2xl text-slate-700 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent shadow-sm transition-all"
        />
        {query && (
          <button
            onClick={() => onChange("")}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
      <div className="flex items-center gap-2 flex-shrink-0">
        <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3.5 shadow-sm">
          <span className="text-sm text-slate-500">Найдено: </span>
          <span className="text-sm font-bold text-violet-700">{filtered}</span>
          <span className="text-sm text-slate-400"> из {total}</span>
        </div>
      </div>
    </div>
  );
}
