import React, { useState, useCallback } from "react";
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Alert,
} from "@mui/material";
import { useDropzone } from "react-dropzone";
import { CloudUpload as UploadIcon } from "@mui/icons-material";
import { uploadDocument } from "../api/documents";
import { useNavigate } from "react-router-dom";

function Upload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
        ".docx",
      ],
      "text/plain": [".txt"],
      "text/markdown": [".md"],
    },
    multiple: false,
  });

  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploading(true);
      setProgress(0);
      
      // Set up a progress interval to simulate upload progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return 95;
          }
          return prev + 5;
        });
      }, 300);

      const docId = await uploadDocument(file);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      // Navigate to dashboard after successful upload
      setTimeout(() => {
        navigate("/");
      }, 1000);
      
    } catch (err) {
      setError("Failed to upload document. Is the backend server running?");
      console.error("Error uploading document:", err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Upload Note
      </Typography>
      <Typography variant="body1" paragraph>
        Upload your documents (PDF, DOCX, TXT, MD) to chat with them.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          border: "2px dashed",
          borderColor: isDragActive ? "primary.main" : "divider",
          backgroundColor: "background.paper",
          textAlign: "center",
          cursor: "pointer",
          mb: 3,
        }}
      >
        <input {...getInputProps()} />
        <UploadIcon
          color="primary"
          sx={{ fontSize: 60, opacity: isDragActive ? 0.7 : 0.5, mb: 1 }}
        />
        <Typography variant="h6" gutterBottom>
          {isDragActive
            ? "Drop the file here"
            : "Drag & drop a file here, or click to select"}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Supported file types: PDF, DOCX, TXT, MD
        </Typography>
      </Paper>

      {file && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body1" gutterBottom>
            Selected file:
          </Typography>
          <Paper sx={{ p: 2, display: "flex", justifyContent: "space-between" }}>
            <Typography>{file.name}</Typography>
            <Typography color="textSecondary">
              {(file.size / 1024).toFixed(1)} KB
            </Typography>
          </Paper>
        </Box>
      )}

      <Button
        variant="contained"
        color="primary"
        startIcon={uploading ? <CircularProgress size={20} /> : <UploadIcon />}
        onClick={handleUpload}
        disabled={!file || uploading}
        sx={{ mt: 1 }}
      >
        {uploading ? `Uploading (${progress}%)` : "Upload Document"}
      </Button>
    </Box>
  );
}

export default Upload;
