import React, { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Divider,
  CircularProgress,
  Alert,
} from "@mui/material";
import { Send as SendIcon } from "@mui/icons-material";
import ReactMarkdown from "react-markdown";
import { fetchDocumentDetails, sendChatMessage } from "../api/documents";

function Chat() {
  const { documentId } = useParams();
  const [document, setDocument] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const loadDocument = async () => {
      try {
        setLoading(true);
        const doc = await fetchDocumentDetails(documentId);
        setDocument(doc);
        setError(null);
      } catch (err) {
        setError("Failed to load document details");
        console.error("Error loading document:", err);
      } finally {
        setLoading(false);
      }
    };

    loadDocument();
  }, [documentId]);

  useEffect(() => {
    // Scroll to bottom when messages change
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    try {
      setSending(true);
      setError(null);

      // Add user message
      const userMessage = {
        role: "user",
        content: input,
      };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");

      // Create chat history for context
      const history = messages
        .reduce((acc, msg, index) => {
          if (index % 2 === 0 && index + 1 < messages.length) {
            acc.push({
              user: msg.content,
              assistant: messages[index + 1].content,
            });
          }
          return acc;
        }, []);

      // Send to API
      const response = await sendChatMessage(documentId, input, history);

      // Add assistant response
      const assistantMessage = {
        role: "assistant",
        content: response,
      };
      setMessages((prev) => [...prev, assistantMessage]);

    } catch (err) {
      setError("Failed to send message. Is the backend server running?");
      console.error("Error sending message:", err);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "60vh",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!document) {
    return (
      <Alert severity="warning" sx={{ mt: 2 }}>
        Document not found
      </Alert>
    );
  }

  return (
    <Box sx={{ height: "calc(100vh - 140px)", display: "flex", flexDirection: "column" }}>
      <Box sx={{ mb: 2 }}>
        <Typography variant="h5" component="h1">
          Chat with: {document.title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Ask questions about your document
        </Typography>
      </Box>

      <Paper
        elevation={3}
        sx={{
          p: 2,
          flexGrow: 1,
          mb: 2,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {messages.length === 0 ? (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              height: "100%",
              color: "text.secondary",
            }}
          >
            <Typography variant="body1" gutterBottom>
              No messages yet
            </Typography>
            <Typography variant="body2">
              Start asking questions about your document
            </Typography>
          </Box>
        ) : (
          messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                mb: 2,
                alignSelf:
                  message.role === "user" ? "flex-end" : "flex-start",
                maxWidth: "75%",
              }}
            >
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  backgroundColor:
                    message.role === "user"
                      ? "primary.light"
                      : "background.paper",
                }}
              >
                {message.role === "assistant" ? (
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                ) : (
                  <Typography>{message.content}</Typography>
                )}
              </Paper>
            </Box>
          ))
        )}
        <div ref={messagesEndRef} />
      </Paper>

      <Box sx={{ display: "flex", mb: 2 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={sending}
          multiline
          maxRows={4}
          sx={{ mr: 1 }}
        />
        <Button
          variant="contained"
          color="primary"
          endIcon={sending ? <CircularProgress size={20} /> : <SendIcon />}
          onClick={handleSend}
          disabled={sending || !input.trim()}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
}

export default Chat;
