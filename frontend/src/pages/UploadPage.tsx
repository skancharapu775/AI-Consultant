import React, { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Paper,
  Typography,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  TextField,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  MenuItem,
} from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import SaveIcon from '@mui/icons-material/Save'
import axios from 'axios'
import client from '../api/client'
import { CompanyContext } from '../types'

const UploadPage: React.FC = () => {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [results, setResults] = useState<any[]>([])
  const [context, setContext] = useState<CompanyContext>({})
  const [savingContext, setSavingContext] = useState(false)
  const [contextSaved, setContextSaved] = useState(false)

  useEffect(() => {
    // Load existing context on mount
    const loadContext = async () => {
      try {
        const response = await client.get('/context/')
        setContext(response.data)
      } catch (error) {
        // Context doesn't exist yet, that's fine
      }
    }
    loadContext()
  }, [])

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFiles(Array.from(event.target.files))
    }
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setUploading(true)
    setResults([])

    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })

    try {
      // For FormData, we must NOT set Content-Type header - axios will set it automatically with boundary
      // The default 'application/json' header from client would break multipart/form-data
      // Use axios directly without the client to avoid Content-Type header interference
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await axios.post(`${API_URL}/ingest/upload`, formData)
      
      // Handle both results array and error message
      if (response.data.error) {
        setResults([{
          file_name: 'Upload Error',
          status: 'error',
          error: response.data.error,
        }])
      } else if (response.data.results) {
        setResults(response.data.results)
      } else {
        setResults([{
          file_name: 'Upload Error',
          status: 'error',
          error: 'Unexpected response format',
        }])
      }
    } catch (error: any) {
      // Handle error message extraction - FastAPI returns detail as string, array, or object
      let errorMessage = 'Upload failed'
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail)) {
          // FastAPI validation errors are arrays of {loc: [], msg: string, type: string}
          errorMessage = detail.map(d => {
            if (typeof d === 'string') return d
            if (d.msg) return `${d.loc?.join('.') || ''}: ${d.msg}`.trim()
            return JSON.stringify(d)
          }).join(', ')
        } else if (detail.msg) {
          errorMessage = detail.msg
        } else {
          errorMessage = JSON.stringify(detail)
        }
      } else if (error.response?.data?.error) {
        const err = error.response.data.error
        errorMessage = typeof err === 'string' ? err : JSON.stringify(err)
      } else if (error.message) {
        errorMessage = error.message
      }
      setResults(files.map(file => ({
        file_name: file.name,
        status: 'error',
        error: errorMessage,
      })))
    } finally {
      setUploading(false)
    }
  }

  const handleContextChange = (field: keyof CompanyContext, value: string) => {
    setContext((prev) => ({ ...prev, [field]: value }))
    setContextSaved(false)
  }

  const handleSaveContext = async () => {
    setSavingContext(true)
    try {
      await client.post('/context/', context)
      setContextSaved(true)
      setTimeout(() => setContextSaved(false), 3000)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to save company context')
    } finally {
      setSavingContext(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload Financial Data
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload CSV files. <strong>gl_pnl_monthly.csv is required</strong>. Other files are optional but improve analysis confidence.
      </Typography>
      <Alert severity="info" sx={{ mb: 2 }}>
        Required: gl_pnl_monthly.csv | Optional: payroll_summary.csv, vendor_spend.csv, revenue_by_segment.csv
      </Alert>

      {/* Company Context Section */}
      <Accordion sx={{ mb: 3 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Company Context (Optional)</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" color="text.secondary" paragraph>
            Provide company context to help generate more relevant and tailored initiatives. This information is optional but improves the quality of recommendations.
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Company Name"
                value={context.company_name || ''}
                onChange={(e) => handleContextChange('company_name', e.target.value)}
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Industry"
                value={context.industry || ''}
                onChange={(e) => handleContextChange('industry', e.target.value)}
                size="small"
                placeholder="e.g., SaaS, E-commerce, Healthcare"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Company Size"
                value={context.company_size || ''}
                onChange={(e) => handleContextChange('company_size', e.target.value)}
                size="small"
              >
                <MenuItem value="">Not specified</MenuItem>
                <MenuItem value="Startup">Startup</MenuItem>
                <MenuItem value="SMB">SMB</MenuItem>
                <MenuItem value="Mid-Market">Mid-Market</MenuItem>
                <MenuItem value="Enterprise">Enterprise</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Revenue Range"
                value={context.revenue_range || ''}
                onChange={(e) => handleContextChange('revenue_range', e.target.value)}
                size="small"
                placeholder="e.g., $10M-$50M"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Employee Count Range"
                value={context.employee_count_range || ''}
                onChange={(e) => handleContextChange('employee_count_range', e.target.value)}
                size="small"
                placeholder="e.g., 50-100"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Business Model"
                value={context.business_model || ''}
                onChange={(e) => handleContextChange('business_model', e.target.value)}
                size="small"
                placeholder="e.g., SaaS, E-commerce, Services"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Growth Stage"
                value={context.growth_stage || ''}
                onChange={(e) => handleContextChange('growth_stage', e.target.value)}
                size="small"
              >
                <MenuItem value="">Not specified</MenuItem>
                <MenuItem value="Early">Early</MenuItem>
                <MenuItem value="Growth">Growth</MenuItem>
                <MenuItem value="Mature">Mature</MenuItem>
                <MenuItem value="Declining">Declining</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Geographic Presence"
                value={context.geographic_presence || ''}
                onChange={(e) => handleContextChange('geographic_presence', e.target.value)}
                size="small"
                placeholder="e.g., US Only, North America, Global"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Key Challenges"
                value={context.key_challenges || ''}
                onChange={(e) => handleContextChange('key_challenges', e.target.value)}
                placeholder="Describe current business challenges..."
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Strategic Priorities"
                value={context.strategic_priorities || ''}
                onChange={(e) => handleContextChange('strategic_priorities', e.target.value)}
                placeholder="Describe strategic priorities and goals..."
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Additional Context"
                value={context.additional_context || ''}
                onChange={(e) => handleContextChange('additional_context', e.target.value)}
                placeholder="Any other relevant information about the company..."
              />
            </Grid>
          </Grid>

          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            {contextSaved && (
              <Alert severity="success" sx={{ flex: 1 }}>
                Company context saved successfully!
              </Alert>
            )}
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSaveContext}
              disabled={savingContext}
            >
              {savingContext ? 'Saving...' : 'Save Context'}
            </Button>
          </Box>
        </AccordionDetails>
      </Accordion>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Box sx={{ mb: 3 }}>
          <input
            accept=".csv"
            style={{ display: 'none' }}
            id="file-upload"
            type="file"
            multiple
            onChange={handleFileChange}
          />
          <label htmlFor="file-upload">
            <Button
              variant="outlined"
              component="span"
              startIcon={<CloudUploadIcon />}
              sx={{ mr: 2 }}
            >
              Select Files
            </Button>
          </label>
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={files.length === 0 || uploading}
            sx={{ mr: 2 }}
          >
            Upload
          </Button>
          {files.length > 0 && (
            <Typography variant="body2" color="text.secondary" component="span">
              {files.length} file(s) selected
            </Typography>
          )}
        </Box>

        {uploading && <LinearProgress sx={{ mb: 2 }} />}

        {results.length > 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Upload Results
            </Typography>
            <List>
              {results.map((result, idx) => (
                <ListItem key={idx}>
                  <ListItemText
                    primary={result.file_name || 'Unknown file'}
                    secondary={
                      result.status === 'valid' ? (
                        `✓ Uploaded successfully (${result.row_count} rows)`
                      ) : (
                        `✗ Error: ${result.error || result.errors?.join(', ') || 'Unknown error'}`
                      )
                    }
                  />
                  {result.status === 'valid' && (
                    <Alert severity="success" sx={{ ml: 2 }}>
                      Valid
                    </Alert>
                  )}
                  {result.status === 'invalid' && (
                    <Alert severity="error" sx={{ ml: 2 }}>
                      Invalid
                    </Alert>
                  )}
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </Paper>
    </Box>
  )
}

export default UploadPage


