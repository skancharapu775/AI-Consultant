import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Alert,
  Grid,
  MenuItem,
  CircularProgress,
} from '@mui/material'
import SaveIcon from '@mui/icons-material/Save'
import client from '../api/client'

interface CompanyContext {
  id?: number
  company_name?: string
  industry?: string
  company_size?: string
  revenue_range?: string
  employee_count_range?: string
  business_model?: string
  growth_stage?: string
  geographic_presence?: string
  key_challenges?: string
  strategic_priorities?: string
  additional_context?: string
}

const CompanyContextPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [context, setContext] = useState<CompanyContext>({})

  useEffect(() => {
    fetchContext()
  }, [])

  const fetchContext = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await client.get('/context/')
      setContext(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load company context')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: keyof CompanyContext) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setContext({ ...context, [field]: event.target.value })
    setSuccess(false)
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError(null)
      setSuccess(false)
      await client.post('/context/', context)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save company context')
    } finally {
      setSaving(false)
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
      <Typography variant="h4" gutterBottom>
        Company Context
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Provide information about your company to help generate more relevant and tailored improvement initiatives.
        All fields are optional, but more context leads to better recommendations.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Company context saved successfully!</Alert>}

      <Paper sx={{ p: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Company Name"
              value={context.company_name || ''}
              onChange={handleChange('company_name')}
              placeholder="e.g., Acme Corp"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              select
              label="Industry"
              value={context.industry || ''}
              onChange={handleChange('industry')}
            >
              <MenuItem value="">Select industry</MenuItem>
              <MenuItem value="SaaS">SaaS</MenuItem>
              <MenuItem value="E-commerce">E-commerce</MenuItem>
              <MenuItem value="Financial Services">Financial Services</MenuItem>
              <MenuItem value="Healthcare">Healthcare</MenuItem>
              <MenuItem value="Manufacturing">Manufacturing</MenuItem>
              <MenuItem value="Retail">Retail</MenuItem>
              <MenuItem value="Technology">Technology</MenuItem>
              <MenuItem value="Professional Services">Professional Services</MenuItem>
              <MenuItem value="Other">Other</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              select
              label="Company Size"
              value={context.company_size || ''}
              onChange={handleChange('company_size')}
            >
              <MenuItem value="">Select size</MenuItem>
              <MenuItem value="Startup">Startup (0-50 employees)</MenuItem>
              <MenuItem value="SMB">SMB (50-200 employees)</MenuItem>
              <MenuItem value="Mid-Market">Mid-Market (200-1000 employees)</MenuItem>
              <MenuItem value="Enterprise">Enterprise (1000+ employees)</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              select
              label="Revenue Range"
              value={context.revenue_range || ''}
              onChange={handleChange('revenue_range')}
            >
              <MenuItem value="">Select range</MenuItem>
              <MenuItem value="$0-$5M">$0-$5M</MenuItem>
              <MenuItem value="$5M-$10M">$5M-$10M</MenuItem>
              <MenuItem value="$10M-$50M">$10M-$50M</MenuItem>
              <MenuItem value="$50M-$100M">$50M-$100M</MenuItem>
              <MenuItem value="$100M-$500M">$100M-$500M</MenuItem>
              <MenuItem value="$500M+">$500M+</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              select
              label="Employee Count Range"
              value={context.employee_count_range || ''}
              onChange={handleChange('employee_count_range')}
            >
              <MenuItem value="">Select range</MenuItem>
              <MenuItem value="1-10">1-10</MenuItem>
              <MenuItem value="10-50">10-50</MenuItem>
              <MenuItem value="50-100">50-100</MenuItem>
              <MenuItem value="100-500">100-500</MenuItem>
              <MenuItem value="500-1000">500-1000</MenuItem>
              <MenuItem value="1000+">1000+</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              select
              label="Business Model"
              value={context.business_model || ''}
              onChange={handleChange('business_model')}
            >
              <MenuItem value="">Select model</MenuItem>
              <MenuItem value="SaaS">SaaS (Subscription)</MenuItem>
              <MenuItem value="E-commerce">E-commerce</MenuItem>
              <MenuItem value="Marketplace">Marketplace</MenuItem>
              <MenuItem value="Services">Services</MenuItem>
              <MenuItem value="Product">Product</MenuItem>
              <MenuItem value="Hybrid">Hybrid</MenuItem>
              <MenuItem value="Other">Other</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              select
              label="Growth Stage"
              value={context.growth_stage || ''}
              onChange={handleChange('growth_stage')}
            >
              <MenuItem value="">Select stage</MenuItem>
              <MenuItem value="Early">Early Stage</MenuItem>
              <MenuItem value="Growth">Growth Stage</MenuItem>
              <MenuItem value="Mature">Mature</MenuItem>
              <MenuItem value="Declining">Declining</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              select
              label="Geographic Presence"
              value={context.geographic_presence || ''}
              onChange={handleChange('geographic_presence')}
            >
              <MenuItem value="">Select presence</MenuItem>
              <MenuItem value="US Only">US Only</MenuItem>
              <MenuItem value="North America">North America</MenuItem>
              <MenuItem value="Europe">Europe</MenuItem>
              <MenuItem value="Asia Pacific">Asia Pacific</MenuItem>
              <MenuItem value="Global">Global</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Key Challenges"
              value={context.key_challenges || ''}
              onChange={handleChange('key_challenges')}
              placeholder="Describe the main challenges your company is facing (e.g., high customer acquisition cost, scaling infrastructure costs, etc.)"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Strategic Priorities"
              value={context.strategic_priorities || ''}
              onChange={handleChange('strategic_priorities')}
              placeholder="Describe your strategic priorities (e.g., profitability improvement, growth acceleration, operational efficiency, etc.)"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Additional Context"
              value={context.additional_context || ''}
              onChange={handleChange('additional_context')}
              placeholder="Any other relevant information about your company that would help generate better recommendations"
            />
          </Grid>

          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
              onClick={handleSave}
              disabled={saving}
              size="large"
            >
              {saving ? 'Saving...' : 'Save Company Context'}
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  )
}

export default CompanyContextPage
