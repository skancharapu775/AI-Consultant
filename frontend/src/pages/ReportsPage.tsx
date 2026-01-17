import React, { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'
import client from '../api/client'

const ReportsPage: React.FC = () => {
  const [loadingMemo, setLoadingMemo] = useState(false)
  const [loadingDeck, setLoadingDeck] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const downloadMemo = async () => {
    try {
      setLoadingMemo(true)
      setError(null)
      const response = await client.get('/reports/memo', {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'executive_memo.md')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to download memo')
    } finally {
      setLoadingMemo(false)
    }
  }

  const downloadDeck = async () => {
    try {
      setLoadingDeck(true)
      setError(null)
      const response = await client.get('/reports/deck', {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'analysis_deck.pptx')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to download deck')
    } finally {
      setLoadingDeck(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Reports
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Download executive memo and PowerPoint presentation.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      <Paper sx={{ p: 4, mt: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Box>
            <Typography variant="h6" gutterBottom>
              Executive Memo
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Download a Markdown executive memo summarizing the analysis and top initiatives.
            </Typography>
            <Button
              variant="contained"
              startIcon={loadingMemo ? <CircularProgress size={20} /> : <DownloadIcon />}
              onClick={downloadMemo}
              disabled={loadingMemo}
            >
              Download Memo (Markdown)
            </Button>
          </Box>

          <Box>
            <Typography variant="h6" gutterBottom>
              PowerPoint Deck
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Download a PowerPoint presentation with charts and analysis overview.
            </Typography>
            <Button
              variant="contained"
              startIcon={loadingDeck ? <CircularProgress size={20} /> : <DownloadIcon />}
              onClick={downloadDeck}
              disabled={loadingDeck}
            >
              Download Deck (PPTX)
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  )
}

export default ReportsPage


