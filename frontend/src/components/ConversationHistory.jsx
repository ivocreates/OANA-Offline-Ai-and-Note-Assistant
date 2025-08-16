import React, { useState, useEffect } from 'react';
import { Box, Typography, List, ListItem, ListItemText, Divider, CircularProgress, Button, IconButton, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from '@mui/material';
import { Delete as DeleteIcon, Chat as ChatIcon, History as HistoryIcon } from '@mui/icons-material';
import { fetchServerConversations, fetchConversationById, deleteConversation } from '../api/chat';

const ConversationHistory = ({ onSelectConversation }) => {
  const [loading, setLoading] = useState(true);
  const [conversations, setConversations] = useState([]);
  const [error, setError] = useState(null);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversationDetails, setConversationDetails] = useState(null);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState(null);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await fetchServerConversations();
      setConversations(data.conversations);
      setError(null);
    } catch (err) {
      setError('Failed to load conversations. Is the backend server running?');
      console.error('Error loading conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectConversation = async (conversation) => {
    try {
      setSelectedConversation(conversation);
      setLoading(true);
      const details = await fetchConversationById(conversation.id);
      setConversationDetails(details);
    } catch (err) {
      setError(`Failed to load conversation details: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmDeleteConversation = (conversation, event) => {
    event.stopPropagation();
    setConversationToDelete(conversation);
    setOpenDeleteDialog(true);
  };

  const handleDeleteConversation = async () => {
    if (!conversationToDelete) return;
    
    try {
      await deleteConversation(conversationToDelete.id);
      
      // If deleted conversation was selected, clear selection
      if (selectedConversation && selectedConversation.id === conversationToDelete.id) {
        setSelectedConversation(null);
        setConversationDetails(null);
      }
      
      // Refresh conversation list
      loadConversations();
    } catch (err) {
      setError(`Failed to delete conversation: ${err.message}`);
    } finally {
      setOpenDeleteDialog(false);
      setConversationToDelete(null);
    }
  };

  const handleContinueConversation = () => {
    if (conversationDetails && onSelectConversation) {
      onSelectConversation(conversationDetails);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown date';
    
    try {
      return new Date(dateStr).toLocaleString();
    } catch (e) {
      return dateStr;
    }
  };

  if (loading && !conversations.length) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error && !conversations.length) {
    return (
      <Box sx={{ p: 2, color: 'error.main' }}>
        <Typography variant="body1">{error}</Typography>
        <Button variant="outlined" sx={{ mt: 2 }} onClick={loadConversations}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      {/* Conversation List */}
      <Box sx={{ width: 300, borderRight: 1, borderColor: 'divider', overflow: 'auto' }}>
        <Typography variant="h6" sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
          <HistoryIcon sx={{ mr: 1 }} />
          Conversation History
        </Typography>
        <Divider />
        
        {conversations.length === 0 ? (
          <Box sx={{ p: 2 }}>
            <Typography variant="body2" color="text.secondary">
              No saved conversations yet.
            </Typography>
          </Box>
        ) : (
          <List>
            {conversations.map((convo) => (
              <ListItem
                button
                key={convo.id}
                selected={selectedConversation?.id === convo.id}
                onClick={() => handleSelectConversation(convo)}
                secondaryAction={
                  <IconButton 
                    edge="end" 
                    aria-label="delete" 
                    onClick={(e) => handleConfirmDeleteConversation(convo, e)}
                  >
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemText 
                  primary={convo.title} 
                  secondary={`${formatDate(convo.timestamp)} • ${convo.message_count} messages`} 
                />
              </ListItem>
            ))}
          </List>
        )}
      </Box>

      {/* Conversation Details */}
      <Box sx={{ flex: 1, p: 2, overflow: 'auto', bgcolor: 'background.paper' }}>
        {selectedConversation ? (
          conversationDetails ? (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">{conversationDetails.title}</Typography>
                <Button 
                  variant="contained" 
                  startIcon={<ChatIcon />}
                  onClick={handleContinueConversation}
                >
                  Continue Conversation
                </Button>
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Box>
                {conversationDetails.messages.map((message, idx) => (
                  <Box 
                    key={idx} 
                    sx={{ 
                      mb: 2, 
                      p: 2, 
                      borderRadius: 1,
                      backgroundColor: message.role === 'user' ? 'primary.light' : 'background.default',
                      color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                      maxWidth: '80%',
                      ml: message.role === 'user' ? 'auto' : 0,
                      mr: message.role === 'user' ? 0 : 'auto'
                    }}
                  >
                    <Typography variant="body1">{message.content}</Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          )
        ) : (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <Typography variant="body1" color="text.secondary">
              Select a conversation to view its details
            </Typography>
          </Box>
        )}
      </Box>

      {/* Delete Dialog */}
      <Dialog
        open={openDeleteDialog}
        onClose={() => setOpenDeleteDialog(false)}
      >
        <DialogTitle>Delete Conversation</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the conversation "{conversationToDelete?.title}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteDialog(false)}>Cancel</Button>
          <Button onClick={handleDeleteConversation} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ConversationHistory;
