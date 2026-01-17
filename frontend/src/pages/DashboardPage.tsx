import React, { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Alert,
  CircularProgress,
} from '@mui/material'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import client from '../api/client'
import { PnLRecord } from '../types'

const DashboardPage: React.FC = () => {
  const [pnlData, setPnlData] = useState<PnLRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const response = await client.post('/analyze/pnl')
        setPnlData(response.data.pnl || [])
        setError(null)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load P&L data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>
  }

  if (pnlData.length === 0) {
    return (
      <Alert severity="info">
        No P&L data available. Please upload data first.
      </Alert>
    )
  }

  const latest = pnlData[pnlData.length - 1]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Financial Dashboard
      </Typography>

      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 2, mb: 4 }}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Revenue (Latest)
          </Typography>
          <Typography variant="h5">
            ${(latest.revenue / 1000000).toFixed(2)}M
          </Typography>
        </Paper>
        <Paper sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary">
            EBITDA (Latest)
          </Typography>
          <Typography variant="h5">
            ${(latest.ebitda / 1000000).toFixed(2)}M
          </Typography>
        </Paper>
        <Paper sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary">
            EBITDA Margin
          </Typography>
          <Typography variant="h5">
            {latest.ebitda_margin_pct.toFixed(1)}%
          </Typography>
        </Paper>
        <Paper sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Gross Margin
          </Typography>
          <Typography variant="h5">
            {latest.gross_margin_pct.toFixed(1)}%
          </Typography>
        </Paper>
      </Box>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Revenue and EBITDA Trend
        </Typography>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={pnlData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip formatter={(value: number) => `$${(value / 1000).toFixed(0)}K`} />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="revenue"
              stroke="#1976d2"
              name="Revenue"
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="ebitda"
              stroke="#2e7d32"
              name="EBITDA"
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          EBITDA Margin Trend
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={pnlData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
            <Legend />
            <Line
              type="monotone"
              dataKey="ebitda_margin_pct"
              stroke="#dc004e"
              name="EBITDA Margin %"
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>
    </Box>
  )
}

export default DashboardPage


