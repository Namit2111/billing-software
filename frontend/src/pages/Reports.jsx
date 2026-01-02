import { useState, useEffect } from 'react'
import { reportsAPI } from '../lib/api'
import { useAuthStore } from '../stores/authStore'
import {
  ArrowDownTrayIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

export default function Reports() {
  const { organization } = useAuthStore()
  const [revenueData, setRevenueData] = useState(null)
  const [outstandingData, setOutstandingData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [dateRange, setDateRange] = useState('30days')

  const currency = organization?.currency || 'USD'

  useEffect(() => {
    loadReports()
  }, [dateRange])

  const getDateRange = () => {
    const end = new Date()
    const start = new Date()
    
    switch (dateRange) {
      case '7days':
        start.setDate(start.getDate() - 7)
        break
      case '30days':
        start.setDate(start.getDate() - 30)
        break
      case '90days':
        start.setDate(start.getDate() - 90)
        break
      case 'year':
        start.setFullYear(start.getFullYear() - 1)
        break
      default:
        start.setDate(start.getDate() - 30)
    }

    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0],
    }
  }

  const loadReports = async () => {
    setIsLoading(true)
    try {
      const { start, end } = getDateRange()
      
      const [revenueRes, outstandingRes] = await Promise.all([
        reportsAPI.revenue(start, end),
        reportsAPI.outstanding(),
      ])

      setRevenueData(revenueRes.data.data)
      setOutstandingData(outstandingRes.data.data)
    } catch (error) {
      console.error('Failed to load reports:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      const { start, end } = getDateRange()
      const response = await reportsAPI.exportCsv(start, end)
      
      const blob = new Blob([response.data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `invoices-${start}-to-${end}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-slate-200 rounded w-48" />
        <div className="h-64 bg-slate-200 rounded-xl" />
      </div>
    )
  }

  const chartData = revenueData?.data?.map(item => ({
    date: formatDate(item.date),
    revenue: item.revenue,
  })) || []

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-slate-900">Reports</h1>
          <p className="text-slate-500 mt-1">Analyze your business performance</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Date Range Selector */}
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="input w-auto"
          >
            <option value="7days">Last 7 days</option>
            <option value="30days">Last 30 days</option>
            <option value="90days">Last 90 days</option>
            <option value="year">Last year</option>
          </select>
          
          <button onClick={handleExport} className="btn-secondary">
            <ArrowDownTrayIcon className="w-5 h-5 mr-2" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Revenue Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-6">
          <p className="text-sm text-slate-500">Total Revenue</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">
            {formatCurrency(revenueData?.total_revenue || 0, currency)}
          </p>
        </div>
        <div className="card p-6">
          <p className="text-sm text-slate-500">Paid</p>
          <p className="text-2xl font-bold text-success-600 mt-1">
            {formatCurrency(revenueData?.paid_amount || 0, currency)}
          </p>
        </div>
        <div className="card p-6">
          <p className="text-sm text-slate-500">Outstanding</p>
          <p className="text-2xl font-bold text-warning-600 mt-1">
            {formatCurrency(revenueData?.outstanding_amount || 0, currency)}
          </p>
        </div>
        <div className="card p-6">
          <p className="text-sm text-slate-500">Invoices</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">
            {revenueData?.total_invoices || 0}
          </p>
        </div>
      </div>

      {/* Revenue Chart */}
      <div className="card p-6">
        <h2 className="font-semibold text-slate-900 mb-4">Revenue Over Time</h2>
        {chartData.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  axisLine={{ stroke: '#e2e8f0' }}
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  axisLine={{ stroke: '#e2e8f0' }}
                  tickFormatter={(value) => `$${value}`}
                />
                <Tooltip
                  formatter={(value) => [formatCurrency(value, currency), 'Revenue']}
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#2563eb"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorRevenue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center text-slate-500">
            No data available for the selected period
          </div>
        )}
      </div>

      {/* Outstanding Invoices */}
      <div className="card">
        <div className="p-6 border-b border-slate-100">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-slate-900">Outstanding Invoices</h2>
            <div className="text-right">
              <p className="text-2xl font-bold text-danger-600">
                {formatCurrency(outstandingData?.total_outstanding || 0, currency)}
              </p>
              <p className="text-sm text-slate-500">
                {outstandingData?.invoice_count || 0} invoices
              </p>
            </div>
          </div>
        </div>
        
        {outstandingData?.invoices?.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {outstandingData.invoices.slice(0, 10).map((invoice) => (
              <div key={invoice.id} className="p-4 flex items-center justify-between hover:bg-slate-50">
                <div>
                  <p className="font-medium text-slate-900">{invoice.invoice_number}</p>
                  <p className="text-sm text-slate-500">{invoice.client_name}</p>
                </div>
                <div className="text-right">
                  <p className="font-medium">
                    {formatCurrency(invoice.balance_due, invoice.currency)}
                  </p>
                  {invoice.days_overdue > 0 && (
                    <p className="text-sm text-danger-600">
                      {invoice.days_overdue} days overdue
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-slate-500">
            No outstanding invoices
          </div>
        )}
      </div>
    </div>
  )
}

