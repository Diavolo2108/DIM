import { CalendarPost } from "./types";

interface Props {
  year: number;
  month: number; // 0-indexed
  posts: CalendarPost[];
  onPostClick: (post: CalendarPost) => void;
}

const DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];

const STATUS_COLORS: Record<string, string> = {
  PROGRAMADO: "bg-blue-100 text-blue-800",
  PUBLICADO: "bg-green-100 text-green-800",
  FALLIDO: "bg-red-100 text-red-800",
};

const FORMAT_ICONS: Record<string, string> = {
  IMAGE: "🖼",
  CAROUSEL: "🎠",
  REEL: "🎬",
};

export function CalendarGrid({ year, month, posts, onPostClick }: Props) {
  const firstDay = new Date(year, month, 1);
  // Semana comienza en Lunes (0=Lun ... 6=Dom)
  const startOffset = (firstDay.getDay() + 6) % 7;
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  // Agrupar posts por día
  const postsByDay = new Map<number, CalendarPost[]>();
  for (const post of posts) {
    const d = new Date(post.scheduled_at).getDate();
    if (!postsByDay.has(d)) postsByDay.set(d, []);
    postsByDay.get(d)!.push(post);
  }

  const totalCells = Math.ceil((startOffset + daysInMonth) / 7) * 7;
  const cells: (number | null)[] = [
    ...Array(startOffset).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
    ...Array(totalCells - startOffset - daysInMonth).fill(null),
  ];

  const today = new Date();
  const isToday = (day: number) =>
    today.getFullYear() === year && today.getMonth() === month && today.getDate() === day;

  return (
    <div className="overflow-hidden rounded-xl bg-white shadow">
      {/* Cabecera días de semana */}
      <div className="grid grid-cols-7 border-b border-gray-100 bg-gray-50">
        {DIAS.map((d) => (
          <div key={d} className="py-2 text-center text-xs font-medium text-gray-500">{d}</div>
        ))}
      </div>

      {/* Celdas del mes */}
      <div className="grid grid-cols-7 divide-x divide-y divide-gray-100">
        {cells.map((day, i) => (
          <div
            key={i}
            className={`min-h-[90px] p-1.5 ${day ? "bg-white" : "bg-gray-50"}`}
          >
            {day && (
              <>
                <span
                  className={`mb-1 inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium ${
                    isToday(day)
                      ? "bg-brand text-white"
                      : "text-gray-600"
                  }`}
                >
                  {day}
                </span>
                <div className="space-y-0.5">
                  {(postsByDay.get(day) ?? []).map((p) => (
                    <button
                      key={p.id}
                      onClick={() => onPostClick(p)}
                      className={`w-full truncate rounded px-1 py-0.5 text-left text-xs ${STATUS_COLORS[p.status]}`}
                      title={p.caption ?? p.format}
                    >
                      {FORMAT_ICONS[p.format]} {p.caption?.slice(0, 18) ?? p.format}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
