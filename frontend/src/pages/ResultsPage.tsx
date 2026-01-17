import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Button,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import DownloadIcon from '@mui/icons-material/Download'
import client from '../api/client'
import { Initiative } from '../types'

const ResultsPage: React.FC = () => {
  const [initiatives, setInitiatives] = useState<Initiative[]>([])
  const [loading, setLoading] = useState(false)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedInitiative, setSelectedInitiative] = useState<Initiative | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [loadingMemo, setLoadingMemo] = useState(false)
  const [loadingDeck, setLoadingDeck] = useState(false)
  const [runId, setRunId] = useState<string | null>(null)

  const runAnalysis = async () => {
    try {
      setRunning(true)
      setError(null)
      const response = await client.post('/run/full')
      setInitiatives(response.data.initiatives || [])
      setRunId(response.data.run_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to run analysis')
    } finally {
      setRunning(false)
    }
  }

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

  const handleRowClick = (initiative: Initiative) => {
    setSelectedInitiative(initiative)
    setDialogOpen(true)
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'Low':
        return 'success'
      case 'Med':
        return 'warning'
      case 'High':
        return 'error'
      default:
        return 'default'
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Analysis Results
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={running ? <CircularProgress size={20} /> : <PlayArrowIcon />}
          onClick={runAnalysis}
          disabled={running}
        >
          {running ? 'Running Analysis...' : 'Run Analysis'}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {runId && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Analysis completed successfully. Run ID: {runId}
        </Alert>
      )}

      {runId && initiatives.length === 0 && !running && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Analysis completed but no initiatives were generated. This may be due to incomplete data or LLM API issues. 
          You can still download the executive memo and PowerPoint deck using the buttons below.
        </Alert>
      )}

      {!runId && initiatives.length === 0 && !running && !error && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Click "Run Analysis" to execute the full pipeline and generate initiatives.
        </Alert>
      )}

      {runId && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Download Reports
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Download the executive memo (Markdown) and presentation deck (PowerPoint) with your analysis results.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <Button
              variant="contained"
              startIcon={loadingMemo ? <CircularProgress size={20} /> : <DownloadIcon />}
              onClick={downloadMemo}
              disabled={loadingMemo}
            >
              Download Memo (Markdown)
            </Button>
            <Button
              variant="contained"
              startIcon={loadingDeck ? <CircularProgress size={20} /> : <DownloadIcon />}
              onClick={downloadDeck}
              disabled={loadingDeck}
            >
              Download Deck (PPTX)
            </Button>
          </Box>
        </Paper>
      )}

      {initiatives.length > 0 && (
        <>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Ranked Initiatives
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Rank</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Impact (Annual)</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Time</TableCell>
                    <TableCell>Risk</TableCell>
                    <TableCell>Score</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {initiatives.map((init, idx) => (
                    <TableRow
                      key={idx}
                      hover
                      onClick={() => handleRowClick(init)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell>{init.rank || idx + 1}</TableCell>
                      <TableCell>{init.title}</TableCell>
                      <TableCell>{init.category}</TableCell>
                      <TableCell>
                        ${(init.impact_low / 1000).toFixed(0)}K - ${(init.impact_high / 1000).toFixed(0)}K
                      </TableCell>
                      <TableCell>{(init.confidence * 100).toFixed(0)}%</TableCell>
                      <TableCell>{init.time_to_value_weeks} weeks</TableCell>
                      <TableCell>
                        <Chip
                          label={init.risk_level}
                          color={getRiskColor(init.risk_level) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{(init.weighted_score || 0).toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Download Reports
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button
                variant="contained"
                startIcon={loadingMemo ? <CircularProgress size={20} /> : <DownloadIcon />}
                onClick={downloadMemo}
                disabled={loadingMemo}
              >
                Download Memo (Markdown)
              </Button>
              <Button
                variant="contained"
                startIcon={loadingDeck ? <CircularProgress size={20} /> : <DownloadIcon />}
                onClick={downloadDeck}
                disabled={loadingDeck}
              >
                Download Deck (PPTX)
              </Button>
            </Box>
          </Paper>
        </>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        {selectedInitiative && (
          <>
            <DialogTitle>{selectedInitiative.title}</DialogTitle>
            <DialogContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Category: {selectedInitiative.category} | Owner: {selectedInitiative.owner || 'TBD'}
              </Typography>
              <Typography variant="body1" paragraph sx={{ mt: 2 }}>
                {selectedInitiative.description}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2">Impact:</Typography>
                <Typography variant="body2">
                  ${(selectedInitiative.impact_low / 1000).toFixed(0)}K - ${(selectedInitiative.impact_high / 1000).toFixed(0)}K annually
                </Typography>
              </Box>
              <Box sx={{ mt: 1 }}>
                <Typography variant="subtitle2">Implementation Cost:</Typography>
                <Typography variant="body2">
                  ${(selectedInitiative.implementation_cost_estimate / 1000).toFixed(0)}K
                </Typography>
              </Box>
              <Box sx={{ mt: 1 }}>
                <Typography variant="subtitle2">Time to Value:</Typography>
                <Typography variant="body2">
                  {selectedInitiative.time_to_value_weeks} weeks
                </Typography>
              </Box>
              {selectedInitiative.assumptions && selectedInitiative.assumptions.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2">Assumptions:</Typography>
                  <ul>
                    {selectedInitiative.assumptions.map((assumption, idx) => (
                      <li key={idx}>
                        <Typography variant="body2">{assumption}</Typography>
                      </li>
                    ))}
                  </ul>
                </Box>
              )}
              {selectedInitiative.next_steps && selectedInitiative.next_steps.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2">Next Steps:</Typography>
                  <ul>
                    {selectedInitiative.next_steps.map((step, idx) => (
                      <li key={idx}>
                        <Typography variant="body2">{step}</Typography>
                      </li>
                    ))}
                  </ul>
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDialogOpen(false)}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  )
}

export default ResultsPage
