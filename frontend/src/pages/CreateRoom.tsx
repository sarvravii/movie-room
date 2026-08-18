import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { createRoom } from "../api/rooms";
import { useSession } from "../lib/session";
import { Button, Card, ErrorText, TextInput } from "../components/ui";

// Values must match TMDB's exact genre names (verified against the live
// TMDB /genre/movie/list response) since the backend validates genre
// against TMDB, not an internal enum. Note "Sci-Fi" -> "Science Fiction".
const GENRES = [
  { label: "Action", value: "Action" },
  { label: "Comedy", value: "Comedy" },
  { label: "Horror", value: "Horror" },
  { label: "Romance", value: "Romance" },
  { label: "Sci-Fi", value: "Science Fiction" },
  { label: "Thriller", value: "Thriller" },
  { label: "Animation", value: "Animation" },
];

export default function CreateRoom() {
  const navigate = useNavigate();
  const { setSession } = useSession();
  const [name, setName] = useState("");
  const [genre, setGenre] = useState(GENRES[0].value);

  const mutation = useMutation({
    mutationFn: () => createRoom(name.trim(), genre),
    onSuccess: (room) => {
      setSession({
        userId: room.user_id,
        displayName: name.trim(),
        roomCode: room.code,
      });
      navigate(`/room/${room.code}`);
    },
  });

  const canSubmit = name.trim().length > 0 && !mutation.isPending;

  return (
    <div className="flex min-h-svh flex-col items-center justify-center px-6 py-16">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="w-full max-w-md"
      >
        <Link to="/" className="mb-6 inline-block text-sm text-ink-secondary hover:text-ink">
          ← Back
        </Link>

        <Card>
          <h1 className="mb-2 text-3xl font-semibold text-ink">Create a Room</h1>
          <p className="mb-8 text-ink-secondary">
            Pick a genre, and we'll build the deck everyone swipes through.
          </p>

          <form
            className="flex flex-col gap-6"
            onSubmit={(e) => {
              e.preventDefault();
              if (canSubmit) mutation.mutate();
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="name" className="text-sm font-medium text-ink-secondary">
                Your name
              </label>
              <TextInput
                id="name"
                placeholder="e.g. Sarv"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus
              />
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="genre" className="text-sm font-medium text-ink-secondary">
                Genre
              </label>
              <div className="grid grid-cols-2 gap-2">
                {GENRES.map((g) => (
                  <button
                    key={g.value}
                    type="button"
                    onClick={() => setGenre(g.value)}
                    className={`rounded-xl border px-4 py-3 text-sm font-medium transition-colors ${
                      genre === g.value
                        ? "border-accent bg-accent-subtle text-ink"
                        : "border-base-border bg-base-raised text-ink-secondary hover:border-accent/50"
                    }`}
                  >
                    {g.label}
                  </button>
                ))}
              </div>
            </div>

            {mutation.isError && (
              <ErrorText>
                Couldn't create the room. Please try again.
              </ErrorText>
            )}

            <Button type="submit" disabled={!canSubmit} className="w-full">
              {mutation.isPending ? "Creating…" : "Create Room"}
            </Button>
          </form>
        </Card>
      </motion.div>
    </div>
  );
}
