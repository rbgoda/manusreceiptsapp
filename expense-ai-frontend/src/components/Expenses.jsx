import { useState, useEffect } from 'react'
import { 
  Search, 
  Filter, 
  ArrowLeft, 
  Settings, 
  Trash2,
  CheckCircle,
  Clock,
  AlertCircle,
  Eye,
  FileText
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import ReceiptReview from './ReceiptReview'

const Expenses = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [showReceiptReview, setShowReceiptReview] = useState(false)
  const [selectedReceiptId, setSelectedReceiptId] = useState(null)
  const [pendingReceipts, setPendingReceipts] = useState([])
  const [loadingReceipts, setLoadingReceipts] = useState(false)
  
  useEffect(() => {
    loadPendingReceipts()
  }, [])

  const loadPendingReceipts = async () => {
    try {
      setLoadingReceipts(true)
      const response = await fetch('http://localhost:8081/api/receipt-review/pending')
      if (response.ok) {
        const data = await response.json()
        setPendingReceipts(data.receipts || [])
      }
    } catch (error) {
      console.error('Error loading pending receipts:', error)
    } finally {
      setLoadingReceipts(false)
    }
  }

  const handleReviewReceipt = (receiptId) => {
    setSelectedReceiptId(receiptId)
    setShowReceiptReview(true)
  }

  const handleReceiptApproved = () => {
    loadPendingReceipts()
  }

  const handleReceiptRejected = () => {
    loadPendingReceipts()
  }
  
  const expenses = [
    {
      id: 1,
      merchant: 'Starbucks Coffee',
      amount: 12.45,
      date: '2024-01-15',
      category: 'Meals Dining',
      categoryColor: '#f59e0b',
      reimbursementStatus: 'pending',
      verificationStatus: 'pending'
    },
    {
      id: 2,
      merchant: 'Uber Technologies',
      amount: 28.75,
      date: '2024-01-14',
      category: 'Transportation',
      categoryColor: '#8b5cf6',
      reimbursementStatus: 'pending',
      verificationStatus: 'pending'
    },
    {
      id: 3,
      merchant: 'Office Depot',
      amount: 89.99,
      date: '2024-01-12',
      category: 'Office Supplies',
      categoryColor: '#10b981',
      reimbursementStatus: 'approved',
      verificationStatus: 'pending'
    },
    {
      id: 4,
      merchant: 'Adobe Systems',
      amount: 52.99,
      date: '2024-01-10',
      category: 'Software Subscriptions',
      categoryColor: '#3b82f6',
      reimbursementStatus: 'approved',
      verificationStatus: 'pending'
    },
    {
      id: 5,
      merchant: 'Marriott Hotels',
      amount: 245.00,
      date: '2024-01-08',
      category: 'Accommodation',
      categoryColor: '#ec4899',
      reimbursementStatus: 'reimbursed',
      verificationStatus: 'pending'
    }
  ]

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />
      case 'reimbursed':
        return <CheckCircle className="w-4 h-4 text-blue-500" />
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      reimbursed: 'bg-blue-100 text-blue-800'
    }
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status]}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
  }

  const filteredExpenses = expenses.filter(expense => {
    const matchesSearch = expense.merchant.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || expense.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">All Expenses</h1>
            <p className="text-gray-600 mt-1">Manage, filter, and review all your expenses</p>
            <span className="inline-block mt-2 px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
              App Preview
            </span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Filter by merchant..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>
          <div className="sm:w-48">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="all">All Categories</option>
              <option value="Meals Dining">Meals Dining</option>
              <option value="Transportation">Transportation</option>
              <option value="Office Supplies">Office Supplies</option>
              <option value="Software Subscriptions">Software Subscriptions</option>
              <option value="Accommodation">Accommodation</option>
            </select>
          </div>
        </div>
      </div>

      {/* Pending Receipts Review Section */}
      {pendingReceipts.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <FileText className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-semibold text-gray-900">Pending Receipt Reviews</h3>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                {pendingReceipts.length} pending
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {pendingReceipts.map((receipt) => (
              <div key={receipt.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-gray-900">{receipt.filename}</span>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                    <Clock className="w-3 h-3 mr-1" />
                    Pending
                  </span>
                </div>
                
                {receipt.extracted_data && (
                  <div className="space-y-2 mb-4">
                    <div className="text-sm">
                      <span className="text-gray-600">Merchant:</span>
                      <span className="ml-2 font-medium">{receipt.extracted_data.merchant || 'Unknown'}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">Amount:</span>
                      <span className="ml-2 font-medium">${receipt.extracted_data.amount || '0.00'}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">Date:</span>
                      <span className="ml-2 font-medium">{receipt.extracted_data.date || 'Unknown'}</span>
                    </div>
                  </div>
                )}
                
                <Button
                  onClick={() => handleReviewReceipt(receipt.id)}
                  size="sm"
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Review & Approve
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Expenses Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Merchant
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reimbursement
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Verification
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredExpenses.map((expense) => (
                <tr key={expense.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{expense.merchant}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-gray-900">${expense.amount.toFixed(2)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-gray-900">{expense.date}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span 
                      className="inline-block px-3 py-1 rounded-full text-xs font-medium text-white"
                      style={{ backgroundColor: expense.categoryColor }}
                    >
                      {expense.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(expense.reimbursementStatus)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(expense.verificationStatus)}
                      <span className="text-sm text-gray-600 capitalize">{expense.verificationStatus}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm">
                        <Settings className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{filteredExpenses.length}</div>
            <div className="text-sm text-gray-600">Total Expenses</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              ${filteredExpenses.reduce((sum, expense) => sum + expense.amount, 0).toFixed(2)}
            </div>
            <div className="text-sm text-gray-600">Total Amount</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {filteredExpenses.filter(e => e.reimbursementStatus === 'pending').length}
            </div>
            <div className="text-sm text-gray-600">Pending Reimbursement</div>
          </div>
        </div>
      </div>

      {/* Receipt Review Modal */}
      {showReceiptReview && (
        <ReceiptReview
          receiptId={selectedReceiptId}
          onClose={() => setShowReceiptReview(false)}
          onApprove={handleReceiptApproved}
          onReject={handleReceiptRejected}
        />
      )}
    </div>
  )
}

export default Expenses

