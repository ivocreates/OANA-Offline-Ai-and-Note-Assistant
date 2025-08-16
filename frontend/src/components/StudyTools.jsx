import React, { useState } from 'react';
import { Box, Typography, Tabs, Tab, Card, CardContent, Button, TextField, CircularProgress, Divider, Alert, Snackbar, Grid } from '@mui/material';
import { School as SchoolIcon, Quiz as QuizIcon, Article as ArticleIcon, Psychology as PsychologyIcon, Note as NoteIcon } from '@mui/icons-material';
import { generateFlashcards, generateQuiz, generateConceptMap, saveStudyNotes, getStudyNotes } from '../api/study';
import { getDocumentSummary } from '../api/chat';

// Tab Panel component
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`study-tabpanel-${index}`}
      aria-labelledby={`study-tab-${index}`}
      {...other}
      style={{ height: '100%' }}
    >
      {value === index && (
        <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// Flashcard component
const Flashcard = ({ question, answer }) => {
  const [flipped, setFlipped] = useState(false);

  return (
    <Card 
      sx={{ 
        mb: 2, 
        minHeight: 200, 
        cursor: 'pointer',
        transition: 'transform 0.6s',
        transformStyle: 'preserve-3d',
        transform: flipped ? 'rotateY(180deg)' : 'rotateY(0deg)'
      }} 
      onClick={() => setFlipped(!flipped)}
    >
      <CardContent sx={{ 
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%',
        backfaceVisibility: 'hidden',
        position: flipped ? 'absolute' : 'relative',
        width: '100%'
      }}>
        <Typography variant="h6" component="div" align="center">
          {question}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          (Click to reveal answer)
        </Typography>
      </CardContent>
      
      <CardContent sx={{ 
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%',
        backfaceVisibility: 'hidden',
        position: flipped ? 'relative' : 'absolute',
        transform: 'rotateY(180deg)',
        width: '100%',
        bgcolor: 'primary.light',
        color: 'primary.contrastText'
      }}>
        <Typography variant="body1" component="div" align="center">
          {answer}
        </Typography>
      </CardContent>
    </Card>
  );
};

// Quiz component
const QuizQuestion = ({ question, options, correctAnswer, index }) => {
  const [selectedOption, setSelectedOption] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    setSubmitted(true);
  };

  return (
    <Card sx={{ mb: 3, p: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Question {index + 1}: {question}
        </Typography>
        
        {options.map((option, idx) => (
          <Box 
            key={idx} 
            sx={{ 
              p: 1.5, 
              mb: 1, 
              border: 1,
              borderColor: 
                submitted 
                  ? (idx === correctAnswer 
                      ? 'success.main' 
                      : (idx === selectedOption && idx !== correctAnswer 
                        ? 'error.main' 
                        : 'divider'))
                  : (idx === selectedOption ? 'primary.main' : 'divider'),
              borderRadius: 1,
              cursor: submitted ? 'default' : 'pointer',
              bgcolor: 
                submitted 
                  ? (idx === correctAnswer 
                      ? 'success.light' 
                      : (idx === selectedOption && idx !== correctAnswer 
                        ? 'error.light' 
                        : 'background.paper'))
                  : (idx === selectedOption ? 'primary.light' : 'background.paper'),
            }}
            onClick={() => {
              if (!submitted) setSelectedOption(idx);
            }}
          >
            <Typography>
              {String.fromCharCode(65 + idx)}. {option}
            </Typography>
          </Box>
        ))}
        
        {!submitted ? (
          <Button 
            variant="contained" 
            onClick={handleSubmit} 
            disabled={selectedOption === null}
            sx={{ mt: 2 }}
          >
            Submit Answer
          </Button>
        ) : (
          <Alert 
            severity={selectedOption === correctAnswer ? "success" : "error"}
            sx={{ mt: 2 }}
          >
            {selectedOption === correctAnswer 
              ? "Correct! Well done." 
              : `Incorrect. The correct answer is ${String.fromCharCode(65 + correctAnswer)}: ${options[correctAnswer]}`
            }
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

// Main StudyTools component
const StudyTools = ({ documentId, documentTitle }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [flashcards, setFlashcards] = useState([]);
  const [quiz, setQuiz] = useState([]);
  const [summary, setSummary] = useState('');
  const [notes, setNotes] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    
    // Load study notes when switching to notes tab
    if (newValue === 3) {
      const savedNotes = getStudyNotes(documentId);
      if (savedNotes) {
        setNotes(savedNotes);
      }
    }
  };

  const handleGenerateFlashcards = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await generateFlashcards(documentId);
      setFlashcards(Array.isArray(data) ? data : []);
    } catch (error) {
      setError(`Failed to generate flashcards: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await generateQuiz(documentId);
      setQuiz(Array.isArray(data) ? data : []);
    } catch (error) {
      setError(`Failed to generate quiz: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGetSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getDocumentSummary(documentId);
      setSummary(data.summary);
    } catch (error) {
      setError(`Failed to generate summary: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNotes = () => {
    try {
      saveStudyNotes(documentId, notes);
      setSnackbarMessage('Notes saved successfully!');
      setSnackbarOpen(true);
    } catch (error) {
      setError(`Failed to save notes: ${error.message}`);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={handleTabChange} variant="fullWidth">
          <Tab icon={<SchoolIcon />} label="Flashcards" />
          <Tab icon={<QuizIcon />} label="Quiz" />
          <Tab icon={<ArticleIcon />} label="Summary" />
          <Tab icon={<NoteIcon />} label="Notes" />
        </Tabs>
      </Box>

      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        {/* Flashcards Tab */}
        <TabPanel value={activeTab} index={0}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Flashcards for: {documentTitle}
            </Typography>
            <Button 
              variant="contained" 
              onClick={handleGenerateFlashcards}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              Generate Flashcards
            </Button>
          </Box>
          <Divider sx={{ mb: 2 }} />
          
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
              <CircularProgress />
            </Box>
          ) : flashcards.length > 0 ? (
            <Grid container spacing={2}>
              {flashcards.map((card, idx) => (
                <Grid item xs={12} md={6} lg={4} key={idx}>
                  <Flashcard question={card.question} answer={card.answer} />
                </Grid>
              ))}
            </Grid>
          ) : (
            <Box sx={{ textAlign: 'center', p: 5, color: 'text.secondary' }}>
              <PsychologyIcon sx={{ fontSize: 60, opacity: 0.5, mb: 2 }} />
              <Typography>
                Generate flashcards to help you memorize key concepts from this document.
              </Typography>
            </Box>
          )}
        </TabPanel>

        {/* Quiz Tab */}
        <TabPanel value={activeTab} index={1}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Quiz for: {documentTitle}
            </Typography>
            <Button 
              variant="contained" 
              onClick={handleGenerateQuiz}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              Generate Quiz
            </Button>
          </Box>
          <Divider sx={{ mb: 2 }} />
          
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
              <CircularProgress />
            </Box>
          ) : quiz.length > 0 ? (
            quiz.map((q, idx) => (
              <QuizQuestion 
                key={idx}
                index={idx}
                question={q.question}
                options={q.options}
                correctAnswer={q.correctAnswer}
              />
            ))
          ) : (
            <Box sx={{ textAlign: 'center', p: 5, color: 'text.secondary' }}>
              <QuizIcon sx={{ fontSize: 60, opacity: 0.5, mb: 2 }} />
              <Typography>
                Generate a quiz to test your understanding of the material.
              </Typography>
            </Box>
          )}
        </TabPanel>

        {/* Summary Tab */}
        <TabPanel value={activeTab} index={2}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Summary of: {documentTitle}
            </Typography>
            <Button 
              variant="contained" 
              onClick={handleGetSummary}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              Generate Summary
            </Button>
          </Box>
          <Divider sx={{ mb: 2 }} />
          
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
              <CircularProgress />
            </Box>
          ) : summary ? (
            <Card>
              <CardContent>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {summary}
                </Typography>
              </CardContent>
            </Card>
          ) : (
            <Box sx={{ textAlign: 'center', p: 5, color: 'text.secondary' }}>
              <ArticleIcon sx={{ fontSize: 60, opacity: 0.5, mb: 2 }} />
              <Typography>
                Generate a summary to get a quick overview of the document's content.
              </Typography>
            </Box>
          )}
        </TabPanel>

        {/* Notes Tab */}
        <TabPanel value={activeTab} index={3}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Your Notes for: {documentTitle}
            </Typography>
            <Button 
              variant="contained" 
              onClick={handleSaveNotes}
              disabled={loading}
            >
              Save Notes
            </Button>
          </Box>
          <Divider sx={{ mb: 2 }} />
          
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          <TextField
            multiline
            fullWidth
            minRows={10}
            maxRows={20}
            variant="outlined"
            placeholder="Type your study notes here..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </TabPanel>
      </Box>
      
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={handleSnackbarClose}
        message={snackbarMessage}
      />
    </Box>
  );
};

export default StudyTools;
