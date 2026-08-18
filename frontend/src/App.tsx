import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SessionProvider } from "./lib/session";
import Home from "./pages/Home";
import CreateRoom from "./pages/CreateRoom";
import JoinRoom from "./pages/JoinRoom";
import RoomLobby from "./pages/RoomLobby";
import SwipeDeck from "./pages/SwipeDeck";
import MatchesReveal from "./pages/MatchesReveal";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SessionProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/create" element={<CreateRoom />} />
            <Route path="/join" element={<JoinRoom />} />
            <Route path="/room/:roomCode" element={<RoomLobby />} />
            <Route path="/room/:roomCode/swipe" element={<SwipeDeck />} />
            <Route path="/room/:roomCode/matches" element={<MatchesReveal />} />
          </Routes>
        </BrowserRouter>
      </SessionProvider>
    </QueryClientProvider>
  );
}

export default App;
