import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChatPage from './pages/index';
import SetupPage from './pages/setup';
import ReadyPlayerMeSetup from './pages/setup';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/setup" element={<ReadyPlayerMeSetup />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
