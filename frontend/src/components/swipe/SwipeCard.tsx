import { forwardRef, useImperativeHandle, useRef } from "react";
import { motion, useMotionValue, useTransform, animate, type PanInfo } from "framer-motion";
import type { MovieResponse } from "../../types/movie";

export interface SwipeCardHandle {
  swipe: (liked: boolean) => void;
}

interface SwipeCardProps {
  movie: MovieResponse;
  active: boolean;
  stackIndex: number;
  onSwiped: (liked: boolean) => void;
}

const SWIPE_THRESHOLD = 100;
const VELOCITY_THRESHOLD = 500;
const EXIT_X = 700;

const SwipeCard = forwardRef<SwipeCardHandle, SwipeCardProps>(function SwipeCard(
  { movie, active, stackIndex, onSwiped },
  ref,
) {
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-300, 300], [-18, 18]);
  const likeOpacity = useTransform(x, [20, 120], [0, 1]);
  const nopeOpacity = useTransform(x, [-120, -20], [1, 0]);
  const hasSwipedRef = useRef(false);

  const finishSwipe = (liked: boolean) => {
    if (hasSwipedRef.current) return;
    hasSwipedRef.current = true;
    // A fixed-duration tween (not a spring) so the fly-off has a
    // predictable, snappy timeline instead of a lingering settle.
    animate(x, liked ? EXIT_X : -EXIT_X, {
      type: "tween",
      duration: 0.28,
      ease: "easeOut",
      onComplete: () => onSwiped(liked),
    });
  };

  useImperativeHandle(ref, () => ({ swipe: finishSwipe }));

  const handleDragEnd = (_event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    if (info.offset.x > SWIPE_THRESHOLD || info.velocity.x > VELOCITY_THRESHOLD) {
      finishSwipe(true);
    } else if (info.offset.x < -SWIPE_THRESHOLD || info.velocity.x < -VELOCITY_THRESHOLD) {
      finishSwipe(false);
    } else {
      animate(x, 0, { type: "spring", stiffness: 400, damping: 30 });
    }
  };

  const scale = 1 - stackIndex * 0.05;
  const yOffset = stackIndex * 14;

  return (
    <motion.div
      className="absolute inset-0"
      style={{ x, rotate, zIndex: 10 - stackIndex }}
      initial={false}
      animate={{ scale, y: yOffset, opacity: stackIndex > 2 ? 0 : 1 - stackIndex * 0.15 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      drag={active ? "x" : false}
      dragElastic={0.9}
      onDragEnd={active ? handleDragEnd : undefined}
    >
      <div className="relative flex h-full w-full flex-col overflow-hidden rounded-xl2 border border-base-border bg-base-surface shadow-panel">
        <div className="relative h-2/3 w-full shrink-0 overflow-hidden bg-base-raised">
          {movie.poster_url ? (
            <img
              src={movie.poster_url}
              alt={movie.title}
              className="h-full w-full object-cover"
              draggable={false}
            />
          ) : (
            <div className="flex h-full items-center justify-center text-ink-muted">
              No poster available
            </div>
          )}

          {active && (
            <>
              <motion.div
                style={{ opacity: likeOpacity }}
                className="absolute right-4 top-4 rotate-[-12deg] rounded-lg border-4 border-emerald-400 px-3 py-1 text-xl font-extrabold uppercase tracking-wide text-emerald-400"
              >
                Like
              </motion.div>
              <motion.div
                style={{ opacity: nopeOpacity }}
                className="absolute left-4 top-4 rotate-[12deg] rounded-lg border-4 border-red-400 px-3 py-1 text-xl font-extrabold uppercase tracking-wide text-red-400"
              >
                Nope
              </motion.div>
            </>
          )}
        </div>

        <div className="flex flex-1 flex-col gap-2 overflow-y-auto p-5">
          <div className="flex items-start justify-between gap-3">
            <h2 className="text-xl font-semibold text-ink">{movie.title}</h2>
            {movie.rating != null && (
              <span className="shrink-0 rounded-full bg-accent-subtle px-2.5 py-1 text-sm font-medium text-accent">
                ★ {movie.rating.toFixed(1)}
              </span>
            )}
          </div>
          <p className="text-sm text-ink-secondary">{movie.release_year ?? "Unknown year"}</p>

          {movie.genres.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {movie.genres.map((genre) => (
                <span
                  key={genre}
                  className="rounded-full border border-base-border px-2.5 py-0.5 text-xs text-ink-secondary"
                >
                  {genre}
                </span>
              ))}
            </div>
          )}

          {movie.overview && (
            <p className="mt-1 text-xs leading-relaxed text-ink-muted">{movie.overview}</p>
          )}
        </div>
      </div>
    </motion.div>
  );
});

export default SwipeCard;
