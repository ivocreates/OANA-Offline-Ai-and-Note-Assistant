import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Button,
  Divider,
  Alert,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from "@mui/material";
import { fetchAvailableModels, changeModel } from "../api/models";

function Settings() {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [loading, setLoading] = useState(true);
  const [changing, setChanging] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    const loadModels = async () => {
      try {
        setLoading(true);
        const availableModels = await fetchAvailableModels();
        setModels(availableModels);
        
        // Set currently active model if available
        if (availableModels.length > 0) {
          // Assuming the first model is active by default
          setSelectedModel(availableModels[0].filename);
        }
        
      } catch (err) {
        setError("Failed to load available models. Is the backend server running?");
        console.error("Error loading models:", err);
      } finally {
        setLoading(false);
      }
    };

    loadModels();
  }, []);

  const handleModelChange = async () => {
    try {
      setChanging(true);
      setError(null);
      setSuccess(null);
      
      await changeModel(selectedModel);
      
      setSuccess(`Successfully changed model to ${selectedModel}`);
    } catch (err) {
      setError(`Failed to change model: ${err.message}`);
      console.error("Error changing model:", err);
    } finally {
      setChanging(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          LLM Model Settings
        </Typography>
        <Typography variant="body2" color="textSecondary" paragraph>
          Choose which local LLM model to use for answering queries
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: "flex", justifyContent: "center", p: 2 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>LLM Model</InputLabel>
              <Select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                label="LLM Model"
              >
                {models.map((model) => (
                  <MenuItem key={model.filename} value={model.filename}>
                    {model.filename} ({model.size_mb} MB)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Button
              variant="contained"
              color="primary"
              onClick={handleModelChange}
              disabled={changing || !selectedModel}
            >
              {changing ? <CircularProgress size={24} /> : "Apply Model Change"}
            </Button>

            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2">Model Location:</Typography>
              <Typography variant="body2" color="textSecondary">
                To add new models, place GGUF files in the data/models directory
              </Typography>
            </Box>
          </>
        )}
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          About OANA
        </Typography>
        <Typography variant="body2" paragraph>
          OANA is an Offline AI Note Assistant that allows you to chat with your notes without requiring an internet connection.
        </Typography>
        <Typography variant="body2" paragraph>
          Version: 0.1.0
        </Typography>
        <Typography variant="body2">
          Created by: OANA Team
        </Typography>
      </Paper>
    </Box>
  );
}

export default Settings;
