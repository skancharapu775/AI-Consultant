import React, { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
} from '@mui/material'
import client from '../api/client'
import { Initiative } from '../types'

const InitiativesPage: React.FC = () => {
  const [initiatives, setInitiatives] = useState<Initiative[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedInitiative, setSelectedInitiative] = useState<Initiative | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  const fetchInitiatives = async () => {
    try {
      setLoading(true)
      // Try to get from latest run first
      const runResponse = await client.post('/run/full')
      if (runResponse.data.initiatives) {
        setInitiatives(runResponse.data.initiatives)
      }
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load initiatives')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchInitiatives()
  }, [])

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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Improvement Initiatives
        </Typography>
        <Button variant="contained" onClick={fetchInitiatives} disabled={loading}>
          Refresh
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {initiatives.length === 0 && !loading && (
        <Alert severity="info">
          No initiatives found. Run the full analysis pipeline first.
        </Alert>
      )}

      {initiatives.length > 0 && (
        <TableContainer component={Paper}>
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

export default InitiativesPage


