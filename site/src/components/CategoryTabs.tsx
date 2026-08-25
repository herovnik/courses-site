import { categories } from "../data/courses";

const categoryIcons: Record<string, string> = {
  Все: "🌐",
  Программирование: "💻",
  Дизайн: "🎨",
  Маркетинг: "📣",
  Аналитика: "📊",
  Менеджмент: "🗂️",
  Финансы: "💰",
};

type Props = {
  activeCategory: string;
  onChange: (cat: string) => void;
};

export default function CategoryTabs({ activeCategory, onChange }: Props) {
  return (
    <div id="categories" className="bg-white border-b border-slate-100 sticky top-16 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center gap-1 overflow-x-auto scrollbar-none py-3">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => onChange(cat)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all flex-shrink-0 ${
                activeCategory === cat
                  ? "bg-violet-600 text-white shadow-md shadow-violet-200"
                  : "text-slate-600 hover:text-violet-600 hover:bg-violet-50"
              }`}
            >
              <span className="text-base leading-none">{categoryIcons[cat]}</span>
              {cat}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
