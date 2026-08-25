import { useState, useMemo } from "react";
import Header from "./components/Header";
import Hero from "./components/Hero";
import CategoryTabs from "./components/CategoryTabs";
import FilterSidebar, { Filters } from "./components/FilterSidebar";
import CourseCard from "./components/CourseCard";
import SearchBar from "./components/SearchBar";
import Footer from "./components/Footer";
import { courses } from "./data/courses";
import { PRICE_DEFAULT_MAX } from "./components/FilterSidebar";

const defaultFilters: Filters = {
  priceMin: 0,
  priceMax: PRICE_DEFAULT_MAX,
  durationMin: 1,
  durationMax: 24,
  selectedSchools: [],
  level: "Любой",
  sortBy: "rating",
};

export default function App() {
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [category, setCategory] = useState("Все");
  const [query, setQuery] = useState("");
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  const filtered = useMemo(() => {
    let result = courses.filter((c) => {
      const matchCategory = category === "Все" || c.category === category;
      const matchPrice = c.price >= filters.priceMin && c.price <= filters.priceMax;
      const matchDuration =
        c.duration >= filters.durationMin && c.duration <= filters.durationMax;
      const matchSchool =
        filters.selectedSchools.length === 0 ||
        filters.selectedSchools.includes(c.school);
      const matchLevel = filters.level === "Любой" || c.level === filters.level;
      const matchQuery =
        !query ||
        c.title.toLowerCase().includes(query.toLowerCase()) ||
        c.description.toLowerCase().includes(query.toLowerCase()) ||
        c.tags.some((t) => t.toLowerCase().includes(query.toLowerCase())) ||
        c.school.toLowerCase().includes(query.toLowerCase());

      return (
        matchCategory &&
        matchPrice &&
        matchDuration &&
        matchSchool &&
        matchLevel &&
        matchQuery
      );
    });

    // Sort
    switch (filters.sortBy) {
      case "rating":
        result.sort((a, b) => b.rating - a.rating);
        break;
      case "price_asc":
        result.sort((a, b) => {
          // Put free courses (price=0) at the end when sorting by cheapest first
          if (a.price === 0 && b.price === 0) return 0;
          if (a.price === 0) return 1;
          if (b.price === 0) return -1;
          return a.price - b.price;
        });
        break;
      case "price_desc":
        result.sort((a, b) => {
          // Put free courses at the end when sorting by most expensive first too
          if (a.price === 0 && b.price === 0) return 0;
          if (a.price === 0) return 1;
          if (b.price === 0) return -1;
          return b.price - a.price;
        });
        break;
      case "duration_asc":
        result.sort((a, b) => a.duration - b.duration);
        break;
      case "popular":
        result.sort((a, b) => b.studentsCount - a.studentsCount);
        break;
    }

    return result;
  }, [filters, category, query]);

  return (
    <div className="min-h-screen bg-slate-50 font-[Inter,system-ui,sans-serif]">
      <Header />
      <Hero />
      <CategoryTabs activeCategory={category} onChange={setCategory} />

      {/* Main Content */}
      <main id="catalog" className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Search bar */}
        <div className="mb-6">
          <SearchBar
            query={query}
            onChange={setQuery}
            total={courses.length}
            filtered={filtered.length}
          />
        </div>

        {/* Mobile filter toggle */}
        <div className="lg:hidden mb-4">
          <button
            onClick={() => setMobileFiltersOpen(!mobileFiltersOpen)}
            className="flex items-center gap-2 bg-white border border-slate-200 text-slate-700 font-medium text-sm px-4 py-3 rounded-xl shadow-sm hover:border-violet-300 hover:text-violet-700 transition-all w-full justify-center"
          >
            <svg
              className="w-4 h-4"
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
            {mobileFiltersOpen ? "Скрыть фильтры" : "Показать фильтры"}
            {(filters.selectedSchools.length > 0 ||
              filters.level !== "Любой" ||
              filters.priceMax < 15000) && (
              <span className="bg-violet-600 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">
                !
              </span>
            )}
          </button>
        </div>

        <div className="flex gap-6 items-start">
          {/* Sidebar — desktop always visible, mobile togglable */}
          <div className={`${mobileFiltersOpen ? "block" : "hidden"} lg:block`}>
            <FilterSidebar
              filters={filters}
              onChange={setFilters}
              totalCount={filtered.length}
            />
          </div>

          {/* Course Grid */}
          <div className="flex-1 min-w-0">
            {filtered.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-24 text-center">
                <div className="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mb-4">
                  <svg
                    className="w-10 h-10 text-slate-300"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={1.5}
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-slate-700 mb-2">
                  Ничего не найдено
                </h3>
                <p className="text-slate-500 text-sm mb-6 max-w-sm">
                  Попробуйте изменить фильтры или поисковый запрос, чтобы
                  найти подходящий курс.
                </p>
                <button
                  onClick={() => {
                    setFilters(defaultFilters);
                    setQuery("");
                    setCategory("Все");
                  }}
                  className="bg-violet-600 text-white font-semibold text-sm px-6 py-3 rounded-xl hover:bg-violet-700 transition-colors"
                >
                  Сбросить всё
                </button>
              </div>
            ) : (
              <>
                {/* Active filter chips */}
                {(filters.selectedSchools.length > 0 ||
                  filters.level !== "Любой" ||
                  filters.priceMax < 15000 ||
                  filters.durationMax < 24 ||
                  query) && (
                  <div className="flex flex-wrap gap-2 mb-5">
                    {query && (
                      <span className="inline-flex items-center gap-1.5 bg-violet-100 text-violet-700 text-xs font-medium px-3 py-1.5 rounded-full border border-violet-200">
                        🔍 {query}
                        <button
                          onClick={() => setQuery("")}
                          className="hover:text-violet-900"
                        >
                          ×
                        </button>
                      </span>
                    )}
                    {filters.selectedSchools.map((s) => (
                      <span
                        key={s}
                        className="inline-flex items-center gap-1.5 bg-violet-100 text-violet-700 text-xs font-medium px-3 py-1.5 rounded-full border border-violet-200"
                      >
                        🏫 {s}
                        <button
                          onClick={() =>
                            setFilters({
                              ...filters,
                              selectedSchools: filters.selectedSchools.filter(
                                (x) => x !== s
                              ),
                            })
                          }
                          className="hover:text-violet-900 font-bold"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                    {filters.level !== "Любой" && (
                      <span className="inline-flex items-center gap-1.5 bg-violet-100 text-violet-700 text-xs font-medium px-3 py-1.5 rounded-full border border-violet-200">
                        📚 {filters.level}
                        <button
                          onClick={() =>
                            setFilters({ ...filters, level: "Любой" })
                          }
                          className="hover:text-violet-900 font-bold"
                        >
                          ×
                        </button>
                      </span>
                    )}
                    {filters.priceMax < 15000 && (
                      <span className="inline-flex items-center gap-1.5 bg-violet-100 text-violet-700 text-xs font-medium px-3 py-1.5 rounded-full border border-violet-200">
                        💰 до {filters.priceMax.toLocaleString("ru-RU")} ₽
                        <button
                          onClick={() =>
                            setFilters({ ...filters, priceMax: 15000 })
                          }
                          className="hover:text-violet-900 font-bold"
                        >
                          ×
                        </button>
                      </span>
                    )}
                    {(filters.durationMin > 1 || filters.durationMax < 24) && (
                      <span className="inline-flex items-center gap-1.5 bg-violet-100 text-violet-700 text-xs font-medium px-3 py-1.5 rounded-full border border-violet-200">
                        ⏱️ {filters.durationMin}–{filters.durationMax} мес.
                        <button
                          onClick={() =>
                            setFilters({
                              ...filters,
                              durationMin: 1,
                              durationMax: 24,
                            })
                          }
                          className="hover:text-violet-900 font-bold"
                        >
                          ×
                        </button>
                      </span>
                    )}
                  </div>
                )}

                {/* Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
                  {filtered.map((course) => (
                    <CourseCard key={course.id} course={course} />
                  ))}
                </div>

                {/* Load more placeholder */}
                <div className="mt-10 text-center">
                  <p className="text-sm text-slate-400 mb-3">
                    Показано {filtered.length} курсов
                  </p>
                  <button className="bg-white border border-slate-200 text-slate-600 font-medium text-sm px-8 py-3 rounded-xl hover:border-violet-300 hover:text-violet-700 transition-all shadow-sm">
                    Загрузить ещё
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
