import { Course } from "../data/courses";

type Props = {
  course: Course;
};

const schoolColors: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  "Яндекс Практикум": { bg: "bg-yellow-50", text: "text-yellow-700", border: "border-yellow-200", dot: "bg-yellow-400" },
  Skillbox: { bg: "bg-green-50", text: "text-green-700", border: "border-green-200", dot: "bg-green-400" },
  GeekBrains: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200", dot: "bg-red-400" },
  Нетология: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200", dot: "bg-blue-400" },
  Coursera: { bg: "bg-cyan-50", text: "text-cyan-700", border: "border-cyan-200", dot: "bg-cyan-400" },
  OTUS: { bg: "bg-violet-50", text: "text-violet-700", border: "border-violet-200", dot: "bg-violet-400" },
};

const levelColors: Record<string, string> = {
  Начинающий: "bg-emerald-50 text-emerald-700 border-emerald-200",
  Средний: "bg-amber-50 text-amber-700 border-amber-200",
  Продвинутый: "bg-rose-50 text-rose-700 border-rose-200",
};

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <svg
          key={star}
          className={`w-3.5 h-3.5 ${
            star <= Math.floor(rating)
              ? "text-amber-400"
              : star - 0.5 <= rating
              ? "text-amber-300"
              : "text-slate-200"
          }`}
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
}

export default function CourseCard({ course }: Props) {
  const sc = schoolColors[course.school] || { bg: "bg-slate-50", text: "text-slate-700", border: "border-slate-200", dot: "bg-slate-400" };
  const discount = course.oldPrice
    ? Math.round((1 - course.price / course.oldPrice) * 100)
    : 0;

  return (
    <div className="group bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:shadow-slate-200/60 hover:border-violet-100 transition-all duration-300 overflow-hidden flex flex-col">
      {/* Image */}
      <div className="relative overflow-hidden h-44 flex-shrink-0">
        <img
          src={course.image}
          alt={course.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        {/* Overlay gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent" />

        {/* Badges */}
        <div className="absolute top-3 left-3 flex gap-1.5">
          {course.isHot && (
            <span className="flex items-center gap-1 bg-gradient-to-r from-orange-500 to-red-500 text-white text-[10px] font-bold px-2 py-1 rounded-lg shadow-lg">
              🔥 Хит
            </span>
          )}
          {course.isNew && (
            <span className="flex items-center gap-1 bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-[10px] font-bold px-2 py-1 rounded-lg shadow-lg">
              ✨ Новый
            </span>
          )}
          {discount > 0 && (
            <span className="bg-emerald-500 text-white text-[10px] font-bold px-2 py-1 rounded-lg shadow-lg">
              -{discount}%
            </span>
          )}
        </div>

        {/* Duration badge */}
        <div className="absolute bottom-3 right-3 flex items-center gap-1 bg-black/60 backdrop-blur-sm text-white text-[11px] font-medium px-2.5 py-1 rounded-lg">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {course.duration} мес.
        </div>

        {/* School badge */}
        <div className="absolute bottom-3 left-3">
          <div className={`flex items-center gap-1.5 ${sc.bg} border ${sc.border} px-2.5 py-1 rounded-lg`}>
            <span className={`w-1.5 h-1.5 rounded-full ${sc.dot}`} />
            <span className={`text-[11px] font-semibold ${sc.text}`}>{course.school}</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col flex-1">
        {/* Level + Certificate */}
        <div className="flex items-center gap-2 mb-2.5">
          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md border ${levelColors[course.level]}`}>
            {course.level}
          </span>
          {course.certificate && (
            <span className="flex items-center gap-1 text-[10px] font-medium text-slate-500 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded-md">
              <svg className="w-3 h-3 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Сертификат
            </span>
          )}
        </div>

        {/* Title */}
        <h3 className="text-base font-bold text-slate-900 mb-1.5 leading-tight group-hover:text-violet-700 transition-colors line-clamp-2">
          {course.title}
        </h3>

        {/* Description */}
        <p className="text-xs text-slate-500 leading-relaxed mb-3 line-clamp-2 flex-1">
          {course.description}
        </p>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-3">
          {course.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="text-[10px] font-medium text-slate-500 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded-md">
              {tag}
            </span>
          ))}
          {course.tags.length > 3 && (
            <span className="text-[10px] font-medium text-violet-500 bg-violet-50 border border-violet-100 px-2 py-0.5 rounded-md">
              +{course.tags.length - 3}
            </span>
          )}
        </div>

        {/* Rating + Students */}
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center gap-1.5">
            <StarRating rating={course.rating} />
            <span className="text-xs font-bold text-slate-800">{course.rating}</span>
            <span className="text-xs text-slate-400">({course.reviewsCount.toLocaleString("ru-RU")})</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-slate-400">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            {course.studentsCount.toLocaleString("ru-RU")}
          </div>
        </div>

        {/* Price + CTA */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-100">
          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-xl font-extrabold text-slate-900">
                {course.price.toLocaleString("ru-RU")} ₽
              </span>
              <span className="text-xs text-slate-400">/мес</span>
            </div>
            {course.oldPrice && (
              <span className="text-xs text-slate-400 line-through">
                {course.oldPrice.toLocaleString("ru-RU")} ₽
              </span>
            )}
          </div>
          <a
            href={course.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-sm font-semibold px-4 py-2.5 rounded-xl hover:from-violet-700 hover:to-indigo-700 hover:scale-105 transition-all shadow-md shadow-violet-200 group-hover:shadow-violet-300"
          >
            Узнать
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
}
