/* Loan API helpers for creating and closing book loans. */

import { api } from './axios'

export async function getLoans() {
  const response = await api.get('/loans')
  return response.data
}

export async function createLoan(payload) {
  const response = await api.post('/loans', payload)
  return response.data
}

export async function deleteLoan(loanId) {
  const response = await api.delete(`/loans/${loanId}`)
  return response.data
}
