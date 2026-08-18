import { useEffect, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { getRoomMatches } from "../api/rooms";
import { useSession } from "../lib/session";
import { useRoomSocket } from "../lib/useRoomSocket";
import { Button, Card } from "../components/ui";
import type { MatchResponse } from "../types/match";

function formatScore(match: MatchResponse) {
  return {
    percentage: Math.round(match.group_score * 100),
    fraction: `${match.positive_count}/${match.total_participants}`,
  };
}

export default function MatchesReveal() {
  const { roomCode } = useParams<{ roomCode: string }>();
  const { session } = useSession();
  const queryClient = useQueryClient();

  const [newMatchToast, setNewMatchToast] = useState<string | null>(null);
  const [highlightedMovieId, setHighlightedMovieId] = useState<number | null>(null);

  const query = useQuery({
    queryKey: ["room-matches", roomCode],
    queryFn: () => getRoomMatches(roomCode!),
    enabled: Boolean(roomCode) && Boolean(session),
  });

  useRoomSocket(roomCode, (event) => {
    if (event.type === "movie_matched") {
      queryClient.invalidateQueries({ queryKey: ["room-matches", roomCode] });
      setNewMatchToast(`🔥 New match: ${event.title}!`);
      setHighlightedMovieId(event.movie_id);
    }
  });

  useEffect(() => {
    if (!newMatchToast) return;
    const timer = setTimeout(() => setNewMatchToast(null), 4000);
    return () => clearTimeout(timer);
  }, [newMatchToast]);

  useEffect(() => {
    if (highlightedMovieId === null) return;
    const timer = setTimeout(() => setHighlightedMovieId(null), 4000);
    return () => clearTimeout(timer);
  }, [highlightedMovieId]);

  if (!roomCode || !session || session.roomCode.toUpperCase() !== roomCode.toUpperCase()) {
    return <Navigate to="/" replace />;
  }

  if (query.isLoading) {
    return (
      <div className="flex min-h-svh items-center justify-center px-6">
        <p className="text-ink-secondary">Loading matches…</p>
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="flex min-h-svh flex-col items-center justify-center px-6 py-16">
        <Card className="max-w-md text-center">
          <h1 className="mb-2 text-xl font-semibold text-ink">Couldn't load matches</h1>
          <p className="mb-6 text-ink-secondary">Something went wrong. Please try again.</p>
          <Button onClick={() => query.refetch()}>Try again</Button>
        </Card>
      </div>
    );
  }

  const matches = query.data ?? [];

  if (matches.length === 0) {
    return (
      <div className="flex min-h-svh flex-col items-center justify-center px-6 py-16">
        <Card className="max-w-md text-center">
          <h1 className="mb-2 text-2xl font-semibold text-ink">No matches yet</h1>
          <p className="mb-6 text-ink-secondary">
            Get swiping! Matches will show up here as soon as everyone agrees on something.
          </p>
          <Link to={`/room/${roomCode}/swipe`} className="text-accent hover:underline">
            ← Back to swiping
          </Link>
        </Card>
      </div>
    );
  }

  const [top, ...rest] = matches;
  const topScore = formatScore(top);

  return (
    <div className="flex min-h-svh flex-col items-center px-6 py-10">
      <div className="mb-8 flex w-full max-w-md items-center justify-between text-sm text-ink-secondary">
        <Link to={`/room/${roomCode}`} className="hover:text-ink">
          ← Lobby
        </Link>
        <Link to={`/room/${roomCode}/swipe`} className="hover:text-ink">
          Keep swiping →
        </Link>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 16, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="mb-10 w-full max-w-md"
      >
        <div className="relative overflow-hidden rounded-xl2 border border-accent/40 bg-base-surface p-6 shadow-panel">
          <div className="pointer-events-none absolute -inset-24 bg-accent/15 blur-3xl" />

          <p className="relative mb-4 text-center text-xs font-semibold uppercase tracking-widest text-accent">
            🔥 Top Match
          </p>

          <div className="relative flex flex-col items-center text-center">
            {top.poster_url ? (
              <img
                src={top.poster_url}
                alt={top.title}
                className="mb-4 h-72 w-48 rounded-xl object-cover shadow-panel"
              />
            ) : (
              <div className="mb-4 flex h-72 w-48 items-center justify-center rounded-xl bg-base-raised text-ink-muted">
                No poster
              </div>
            )}

            <h1 className="mb-3 text-2xl font-semibold text-ink">{top.title}</h1>

            <div className="mb-1 text-4xl font-bold text-accent">{topScore.percentage}%</div>
            <p className="text-sm text-ink-secondary">{topScore.fraction} people liked this</p>
            {top.group_score >= 1 && (
              <p className="mt-2 text-xs font-medium text-accent">Everyone's in! 🎉</p>
            )}
          </div>
        </div>
      </motion.div>

      {rest.length > 0 && (
        <div className="w-full max-w-md">
          <p className="mb-3 text-sm font-medium uppercase tracking-wide text-ink-secondary">
            Also in the running
          </p>
          <div className="flex flex-col gap-2">
            {rest.map((match, index) => {
              const score = formatScore(match);
              const position = index + 2;
              const isHighlighted = highlightedMovieId === match.movie_id;

              return (
                <motion.div
                  key={match.movie_id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{
                    opacity: 1,
                    y: 0,
                    boxShadow: isHighlighted
                      ? "0 0 0 2px rgba(108,92,231,0.8), 0 0 24px rgba(108,92,231,0.5)"
                      : "0 0 0 0px rgba(108,92,231,0)",
                  }}
                  transition={{ duration: 0.4, delay: index * 0.04 }}
                  className="flex items-center gap-3 rounded-xl border border-base-border bg-base-surface p-3"
                >
                  <span className="w-6 shrink-0 text-center text-sm font-medium text-ink-muted">
                    #{position}
                  </span>
                  {match.poster_url ? (
                    <img
                      src={match.poster_url}
                      alt={match.title}
                      className="h-16 w-11 shrink-0 rounded-md object-cover"
                    />
                  ) : (
                    <div className="h-16 w-11 shrink-0 rounded-md bg-base-raised" />
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-ink">{match.title}</p>
                    <p className="text-xs text-ink-secondary">{score.fraction} liked it</p>
                  </div>
                  <span className="shrink-0 rounded-full bg-accent-subtle px-2.5 py-1 text-sm font-medium text-accent">
                    {score.percentage}%
                  </span>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      <AnimatePresence>
        {newMatchToast && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 rounded-xl border border-accent/60 bg-base-raised px-4 py-3 text-sm font-medium text-ink shadow-panel"
          >
            {newMatchToast}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
