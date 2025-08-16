import React, { useState, useEffect } from "react";
import { Route, Routes } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import { CssBaseline } from "@mui/material";
import { theme, darkTheme } from "./theme";

// Import pages
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import NotFound from "./pages/NotFound";
import Upload from "./pages/Upload";
import Settings from "./pages/Settings";

// Import components
import AppLayout from "./components/AppLayout";

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [currentTheme, setCurrentTheme] = useState(theme);

  useEffect(() => {
    const savedMode = localStorage.getItem("darkMode");
    if (savedMode) {
      setDarkMode(savedMode === "true");
    }
  }, []);

  useEffect(() => {
    setCurrentTheme(darkMode ? darkTheme : theme);
    localStorage.setItem("darkMode", darkMode);
  }, [darkMode]);

  return (
    <ThemeProvider theme={currentTheme}>
      <CssBaseline />
      <Routes>
        <Route
          path="/"
          element={
            <AppLayout darkMode={darkMode} setDarkMode={setDarkMode} />
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="chat/:documentId" element={<Chat />} />
          <Route path="upload" element={<Upload />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </ThemeProvider>
  );
}

export default App;
