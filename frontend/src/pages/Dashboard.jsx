import React from "react";
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { fetchDocuments } from "../api/documents";

function Dashboard() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadDocuments = async () => {
      try {
        setLoading(true);
        const docs = await fetchDocuments();
        setDocuments(docs);
      } catch (err) {
        setError("Failed to load documents. Is the backend server running?");
        console.error("Error loading documents:", err);
      } finally {
        setLoading(false);
      }
    };

    loadDocuments();
  }, []);

  const handleUpload = () => {
    navigate("/upload");
  };

  const handleChatClick = (documentId) => {
    navigate(`/chat/${documentId}`);
  };

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 4,
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom>
          Your Notes
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          sx={{ borderRadius: 2 }}
        >
          Upload New Note
        </Button>
      </Box>

      {loading ? (
        <Typography>Loading documents...</Typography>
      ) : error ? (
        <Paper
          sx={{
            p: 3,
            backgroundColor: "error.light",
            color: "error.contrastText",
          }}
        >
          {error}
        </Paper>
      ) : documents.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: "center" }}>
          <Typography variant="h6" gutterBottom>
            No documents found
          </Typography>
          <Typography variant="body1" color="textSecondary" paragraph>
            Upload your first document to get started.
          </Typography>
          <Button variant="contained" color="primary" onClick={handleUpload}>
            Upload Document
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {documents.map((doc) => (
            <Grid item key={doc.id} xs={12} sm={6} md={4}>
              <Card sx={{ height: "100%" }}>
                <CardContent>
                  <Typography variant="h6" component="div" noWrap>
                    {doc.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Uploaded: {new Date(doc.upload_time).toLocaleString()}
                  </Typography>
                  <Typography
                    variant="body2"
                    color={
                      doc.status === "completed"
                        ? "success.main"
                        : doc.status === "error"
                        ? "error.main"
                        : "warning.main"
                    }
                    sx={{ mt: 1 }}
                  >
                    Status: {doc.status}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    onClick={() => handleChatClick(doc.id)}
                    disabled={doc.status !== "completed"}
                  >
                    Chat with this note
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}

export default Dashboard;
