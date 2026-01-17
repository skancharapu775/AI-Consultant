export interface PnLRecord {
  month: string
  revenue: number
  cogs: number
  gross_margin: number
  gross_margin_pct: number
  total_opex: number
  ebitda: number
  ebitda_margin_pct: number
}

export interface Initiative {
  id?: number
  title: string
  category: string
  owner?: string
  description: string
  data_evidence?: string[]
  impact_low: number
  impact_high: number
  time_to_value_weeks: number
  implementation_cost_estimate: number
  risk_level: string
  confidence: number
  assumptions?: string[]
  next_steps?: string[]
  rank?: number
  weighted_score?: number
}

export interface Diagnostics {
  fixed_vs_variable?: Record<string, {
    fixed_pct: number
    variable_pct: number
    confidence: number
  }>
  outliers?: {
    vendor_spikes?: Array<{ month: string; amount: number; z_score: number }>
    opex_spikes?: Array<{ month: string; total_opex: number; z_score: number }>
    revenue_declines?: Array<{ month: string; prev_revenue: number; current_revenue: number; decline_pct: number }>
  }
  trends?: Record<string, {
    slope: number
    direction: string
    r_squared: number
  }>
  data_completeness?: {
    total_months: number
    missing_gl_months: string[]
    missing_payroll_months: string[]
    payroll_cost_coverage: number
  }
}

export interface CompanyContext {
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


