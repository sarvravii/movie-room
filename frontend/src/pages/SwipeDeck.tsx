import { useEffect, useRef, useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { getRoomMovies } from "../api/movies";
import { submitSwipe } from "../api/rooms";
import { useSession } from "../lib/session";
import { useRoomSocket } from "../lib/useRoomSocket";
import { Button, Card } from "../components/ui";
import SwipeCard, { type SwipeCardHandle } from "../components/swipe/SwipeCard";
import type { MovieResponse } from "../types/movie";
import type { RoomSwipeProgress } from "../types/ws";

const STACK_DEPTH = 3;

export default function SwipeDeck() {
  const { roomCode } = useParams<{ roomCode: string }>();
  const { session } = useSession();
  const navigate = useNavigate();

  const [remaining, setRemaining] = useState<MovieResponse[] | null>(null);
  const [progress, setProgress] = useState<RoomSwipeProgress | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const topCardRef = useRef<SwipeCardHandle>(null);

  const query = useQuery({
    queryKey: ["room-movies", roomCode],
    queryFn: () => getRoomMovies(roomCode!),
    enabled: Boolean(roomCode) && Boolean(session),
  });

  // Seed the local, mutable deck once from the fetched data — swiping
  // shouldn't re-shuffle or re-fetch, it just drains this local list.
  useEffect(() => {
    if (query.data && remaining === null) {
      setRemaining(query.data);
    }
  }, [query.data, remaining]);

  useRoomSocket(roomCode, (event) => {
    if (event.type === "user_swiped") {
      setProgress(event.room_swipe_progress);
    }
  });

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(null), 3000);
    return () => clearTimeout(timer);
  }, [toast]);

  if (!roomCode || !session || session.roomCode.toUpperCase() !== roomCode.toUpperCase()) {
    return <Navigate to="/" replace />;
  }

  const handleSwiped = (movie: MovieResponse, liked: boolean) => {
    setRemaining((prev) => (prev ? prev.filter((m) => m.id !== movie.id) : prev));

    // Fire-and-forget: the UI has already advanced, this just persists it.
    submitSwipe(roomCode, session.userId, movie.id, liked).catch((err) => {
      const status = axios.isAxiosError(err) ? err.response?.status : undefined;
      if (status === 409) {
        // Already swiped on this movie in a previous session — the
        // preference is already recorded, nothing to tell the user.
        return;
      }
      setToast("Couldn't save that swipe — it may not be recorded.");
    });
  };

  if (query.isLoading || remaining === null) {
    return (
      <div className="flex min-h-svh items-center justify-center px-6">
        <p className="text-ink-secondary">Loading movies…</p>
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="flex min-h-svh flex-col items-center justify-center px-6 py-16">
        <Card className="max-w-md text-center">
          <h1 className="mb-2 text-xl font-semibold text-ink">Couldn't load the deck</h1>
          <p className="mb-6 text-ink-secondary">
            Something went wrong fetching movies for this room.
          </p>
          <Button onClick={() => query.refetch()}>Try again</Button>
        </Card>
      </div>
    );
  }

  const isDone = remaining.length === 0;

  if (isDone) {
    const finishedCount = progress
      ? progress.members.filter((m) => m.swiped_count >= progress.deck_size).length
      : null;
    const totalCount = progress?.members.length ?? null;

    return (
      <div className="flex min-h-svh flex-col items-center justify-center px-6 py-16">
        <Card className="max-w-md text-center">
          <h1 className="mb-2 text-2xl font-semibold text-ink">You're done! 🎬</h1>
          <p className="mb-6 text-ink-secondary">Waiting for others to finish swiping…</p>

          {finishedCount !== null && totalCount !== null && (
            <p className="mb-8 text-sm text-ink-muted">
              <span className="font-semibold text-accent">{finishedCount}</span> of{" "}
              {totalCount} people have finished swiping
            </p>
          )}

          <Button className="w-full" onClick={() => navigate(`/room/${roomCode}/matches`)}>
            View Matches So Far
          </Button>
        </Card>
      </div>
    );
  }

  const visibleStack = remaining.slice(0, STACK_DEPTH);

  return (
    <div className="flex min-h-svh flex-col items-center px-6 py-10">
      <div className="mb-6 flex w-full max-w-sm items-center justify-between text-sm text-ink-secondary">
        <Link to={`/room/${roomCode}`} className="hover:text-ink">
          ← Lobby
        </Link>
        <span>{remaining.length} left</span>
      </div>

      <div className="relative h-[560px] w-full max-w-sm">
        {visibleStack.map((movie, stackIndex) => (
          <SwipeCard
            key={movie.id}
            ref={stackIndex === 0 ? topCardRef : undefined}
            movie={movie}
            active={stackIndex === 0}
            stackIndex={stackIndex}
            onSwiped={(liked) => handleSwiped(movie, liked)}
          />
        ))}
      </div>

      <div className="mt-8 flex items-center gap-6">
        <button
          onClick={() => topCardRef.current?.swipe(false)}
          aria-label="Dislike"
          className="flex h-16 w-16 items-center justify-center rounded-full border border-base-border bg-base-surface text-2xl text-red-400 shadow-panel transition-transform hover:scale-105"
        >
          ✕
        </button>
        <button
          onClick={() => topCardRef.current?.swipe(true)}
          aria-label="Like"
          className="flex h-16 w-16 items-center justify-center rounded-full border border-base-border bg-base-surface text-2xl text-emerald-400 shadow-panel transition-transform hover:scale-105"
        >
          ♥
        </button>
      </div>

      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 rounded-xl border border-base-border bg-base-raised px-4 py-3 text-sm text-ink shadow-panel">
          {toast}
        </div>
      )}
    </div>
  );
}
