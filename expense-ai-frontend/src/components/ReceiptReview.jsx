import { useState, useEffect } from 'react'
import { 
  ArrowLeft, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Edit3,
  Eye,
  Calendar,
  DollarSign,
  Building,
  Tag,
  FileText,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const ReceiptReview = ({ receiptId, onClose, onApprove, onReject }) => {
  const [receipt, setReceipt] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [reviewedData, setReviewedData] = useState({})
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (receiptId) {
      loadReceiptDetails()
    }
  }, [receiptId])

  const loadReceiptDetails = async () => {
    try {
      setLoading(true)
      const response = await fetch(`http://localhost:8081/api/receipt-review/${receiptId}`)
      if (response.ok) {
        const data = await response.json()
        setReceipt(data)
        setReviewedData(data.reviewed_data || data.extracted_data || {})
      }
    } catch (error) {
      console.error('Error loading receipt details:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async () => {
    try {
      setSubmitting(true)
      const response = await fetch(`http://localhost:8081/api/receipt-review/${receiptId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          reviewed_data: reviewedData
        })
      })

      if (response.ok) {
        onApprove && onApprove()
        onClose && onClose()
      }
    } catch (error) {
      console.error('Error approving receipt:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const handleReject = async () => {
    try {
      setSubmitting(true)
      const response = await fetch(`http://localhost:8081/api/receipt-review/${receiptId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        onReject && onReject()
        onClose && onClose()
      }
    } catch (error) {
      console.error('Error rejecting receipt:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const handleUpdateData = async () => {
    try {
      const response = await fetch(`http://localhost:8081/api/receipt-review/${receiptId}/update`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          reviewed_data: reviewedData
        })
      })

      if (response.ok) {
        setEditing(false)
        loadReceiptDetails()
      }
    } catch (error) {
      console.error('Error updating receipt data:', error)
    }
  }

  const handleFieldChange = (field, value) => {
    setReviewedData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
            <span>Loading receipt details...</span>
          </div>
        </div>
      </div>
    )
  }

  if (!receipt) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" onClick={onClose}>
                <ArrowLeft className="w-4 h-4" />
              </Button>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Receipt Review</h2>
                <p className="text-gray-600">Review and approve AI-extracted data</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                receipt.review_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                receipt.review_status === 'approved' ? 'bg-green-100 text-green-800' :
                'bg-red-100 text-red-800'
              }`}>
                {receipt.review_status === 'pending' && <Clock className="w-4 h-4 mr-1" />}
                {receipt.review_status === 'approved' && <CheckCircle className="w-4 h-4 mr-1" />}
                {receipt.review_status === 'rejected' && <XCircle className="w-4 h-4 mr-1" />}
                {receipt.review_status.charAt(0).toUpperCase() + receipt.review_status.slice(1)}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
          {/* Receipt Image */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Receipt Image</h3>
            <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
              {receipt.file_path ? (
                <img 
                  src={`http://localhost:8081${receipt.file_path}`}
                  alt="Receipt"
                  className="w-full h-auto rounded-lg shadow-sm"
                />
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-500">
                  <div className="text-center">
                    <FileText className="w-12 h-12 mx-auto mb-2" />
                    <p>Receipt image not available</p>
                  </div>
                </div>
              )}
            </div>
            
            <div className="text-sm text-gray-600">
              <p><strong>Filename:</strong> {receipt.filename}</p>
              <p><strong>File Type:</strong> {receipt.file_type?.toUpperCase()}</p>
              <p><strong>Uploaded:</strong> {new Date(receipt.created_at).toLocaleString()}</p>
            </div>
          </div>

          {/* Extracted Data */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Extracted Data</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setEditing(!editing)}
              >
                <Edit3 className="w-4 h-4 mr-2" />
                {editing ? 'Cancel' : 'Edit'}
              </Button>
            </div>

            <div className="space-y-4">
              {/* Merchant */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Building className="w-4 h-4 inline mr-1" />
                  Merchant
                </label>
                {editing ? (
                  <input
                    type="text"
                    value={reviewedData.merchant || ''}
                    onChange={(e) => handleFieldChange('merchant', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                ) : (
                  <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded-md">
                    {reviewedData.merchant || 'Not extracted'}
                  </p>
                )}
              </div>

              {/* Amount */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <DollarSign className="w-4 h-4 inline mr-1" />
                  Amount
                </label>
                {editing ? (
                  <input
                    type="number"
                    step="0.01"
                    value={reviewedData.amount || ''}
                    onChange={(e) => handleFieldChange('amount', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                ) : (
                  <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded-md">
                    ${reviewedData.amount || '0.00'}
                  </p>
                )}
              </div>

              {/* Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Date
                </label>
                {editing ? (
                  <input
                    type="date"
                    value={reviewedData.date || ''}
                    onChange={(e) => handleFieldChange('date', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                ) : (
                  <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded-md">
                    {reviewedData.date || 'Not extracted'}
                  </p>
                )}
              </div>

              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Tag className="w-4 h-4 inline mr-1" />
                  Category
                </label>
                {editing ? (
                  <select
                    value={reviewedData.category || ''}
                    onChange={(e) => handleFieldChange('category', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">Select category</option>
                    {receipt.available_categories?.map(cat => (
                      <option key={cat.id} value={cat.name}>{cat.name}</option>
                    ))}
                  </select>
                ) : (
                  <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded-md">
                    {reviewedData.category || 'Not categorized'}
                  </p>
                )}
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <FileText className="w-4 h-4 inline mr-1" />
                  Description
                </label>
                {editing ? (
                  <textarea
                    value={reviewedData.description || ''}
                    onChange={(e) => handleFieldChange('description', e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                ) : (
                  <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded-md">
                    {reviewedData.description || 'No description'}
                  </p>
                )}
              </div>

              {editing && (
                <Button
                  onClick={handleUpdateData}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  Save Changes
                </Button>
              )}
            </div>

            {/* AI Confidence */}
            {receipt.extracted_data?.confidence && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-medium text-blue-800">
                    AI Confidence: {Math.round(receipt.extracted_data.confidence * 100)}%
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        {receipt.review_status === 'pending' && (
          <div className="p-6 border-t border-gray-200 bg-gray-50">
            <div className="flex justify-end space-x-4">
              <Button
                variant="outline"
                onClick={handleReject}
                disabled={submitting}
                className="text-red-600 border-red-300 hover:bg-red-50"
              >
                <XCircle className="w-4 h-4 mr-2" />
                Reject
              </Button>
              <Button
                onClick={handleApprove}
                disabled={submitting}
                className="bg-green-600 hover:bg-green-700"
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                {submitting ? 'Processing...' : 'Approve & Create Expense'}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ReceiptReview

