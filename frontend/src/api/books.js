/* Book and member API helpers used by the catalog and loan form. */

import { api } from './axios'

export async function getBooks() {
  const response = await api.get('/books')
  return response.data
}

export async function getMembers() {
  const response = await api.get('/members')
  return response.data
}
