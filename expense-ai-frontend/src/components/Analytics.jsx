import { useState, useEffect } from 'react'
import { ArrowLeft, BarChart3, PieChart, Calendar, TrendingUp } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts'

const Analytics = () => {
  const [selectedMonth, setSelectedMonth] = useState('August 2025')
  
  // Mock data for analytics
  const monthlySpendingData = [
    { day: '1', amount: 0 },
    { day: '2', amount: 0 },
    { day: '3', amount: 0 },
    { day: '4', amount: 0 },
    { day: '5', amount: 0 },
    { day: '6', amount: 0 },
    { day: '7', amount: 0 },
    { day: '8', amount: 245 },
    { day: '9', amount: 245 },
    { day: '10', amount: 298 },
    { day: '11', amount: 298 },
    { day: '12', amount: 388 },
    { day: '13', amount: 388 },
    { day: '14', amount: 417 },
    { day: '15', amount: 429 },
    { day: '16', amount: 429 },
    { day: '17', amount: 429 },
    { day: '18', amount: 429 },
    { day: '19', amount: 429 },
    { day: '20', amount: 429 },
    { day: '21', amount: 429 },
    { day: '22', amount: 429 },
    { day: '23', amount: 429 },
    { day: '24', amount: 429 },
    { day: '25', amount: 429 },
    { day: '26', amount: 429 },
    { day: '27', amount: 429 },
    { day: '28', amount: 429 },
    { day: '29', amount: 429 },
    { day: '30', amount: 429 },
    { day: '31', amount: 429 }
  ]

  const categoryBreakdownData = [
    { name: 'Accommodation', value: 245, color: '#ec4899' },
    { name: 'Office Supplies', value: 90, color: '#10b981' },
    { name: 'Software Subscriptions', value: 53, color: '#3b82f6' },
    { name: 'Transportation', value: 29, color: '#8b5cf6' },
    { name: 'Meals Dining', value: 12, color: '#f59e0b' }
  ]

  const merchantSpendingData = [
    { merchant: 'Marriott Hotels', amount: 245 },
    { merchant: 'Office Depot', amount: 90 },
    { merchant: 'Adobe Systems', amount: 53 },
    { merchant: 'Uber Technologies', amount: 29 },
    { merchant: 'Starbucks Coffee', amount: 12 }
  ]

  const COLORS = ['#ec4899', '#10b981', '#3b82f6', '#8b5cf6', '#f59e0b']

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">{`Day ${label}`}</p>
          <p className="text-purple-600">
            {`Amount: $${payload[0].value.toFixed(2)}`}
          </p>
        </div>
      )
    }
    return null
  }

  const PieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">{payload[0].name}</p>
          <p className="text-purple-600">
            {`$${payload[0].value.toFixed(2)}`}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Expense Analytics</h1>
          <p className="text-gray-600 mt-1">Visualize your spending habits and identify trends</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Total Spending (Current Month)</h3>
            <Calendar className="w-5 h-5 text-gray-400" />
          </div>
          <div className="text-3xl font-bold text-gray-900">$0.00</div>
          <div className="text-sm text-gray-600">Total amount spent this month</div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Total Receipts (Current Month)</h3>
            <BarChart3 className="w-5 h-5 text-gray-400" />
          </div>
          <div className="text-3xl font-bold text-gray-900">0</div>
          <div className="text-sm text-gray-600">Total number of expenses logged</div>
        </div>
      </div>

      {/* Monthly Spending Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Monthly Spending</h3>
          <select 
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="August 2025">August 2025</option>
            <option value="July 2025">July 2025</option>
            <option value="June 2025">June 2025</option>
          </select>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={monthlySpendingData}>
              <defs>
                <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="day" 
                stroke="#6b7280"
                fontSize={12}
              />
              <YAxis 
                stroke="#6b7280"
                fontSize={12}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="amount"
                stroke="#8b5cf6"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorAmount)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Category Breakdown</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={categoryBreakdownData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {categoryBreakdownData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<PieTooltip />} />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-2">
            {categoryBreakdownData.map((category, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: category.color }}
                  ></div>
                  <span className="text-sm text-gray-700">{category.name}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">${category.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Merchants */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Top 10 Merchants by Spending</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={merchantSpendingData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  type="number" 
                  stroke="#6b7280"
                  fontSize={12}
                  tickFormatter={(value) => `$${value}`}
                />
                <YAxis 
                  type="category" 
                  dataKey="merchant" 
                  stroke="#6b7280"
                  fontSize={12}
                  width={100}
                />
                <Tooltip 
                  formatter={(value) => [`$${value}`, 'Amount']}
                  labelStyle={{ color: '#374151' }}
                />
                <Bar 
                  dataKey="amount" 
                  fill="#8b5cf6"
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Summary Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">$429.18</div>
            <div className="text-sm text-gray-600">Total Expenses</div>
            <div className="flex items-center justify-center mt-1">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">12.5%</span>
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">5</div>
            <div className="text-sm text-gray-600">Total Receipts</div>
            <div className="flex items-center justify-center mt-1">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">15.3%</span>
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">$85.84</div>
            <div className="text-sm text-gray-600">Avg per Receipt</div>
            <div className="flex items-center justify-center mt-1">
              <TrendingUp className="w-4 h-4 text-red-500 mr-1 transform rotate-180" />
              <span className="text-sm text-red-600">3.1%</span>
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">5</div>
            <div className="text-sm text-gray-600">Categories Used</div>
            <div className="flex items-center justify-center mt-1">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">25%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics

