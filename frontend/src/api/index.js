import { api } from '../stores/auth'

// 图书 API
export const bookApi = {
  getBooks(params) {
    return api.get('/books', { params })
  },
  getBook(id) {
    return api.get(`/books/${id}`)
  },
  createBook(data) {
    return api.post('/books', data)
  },
  updateBook(id, data) {
    return api.put(`/books/${id}`, data)
  },
  deleteBook(id) {
    return api.delete(`/books/${id}`)
  }
}

// 读者 API
export const readerApi = {
  getReaders(params) {
    return api.get('/readers', { params })
  },
  getReader(id) {
    return api.get(`/readers/${id}`)
  },
  createReader(data) {
    return api.post('/readers', data)
  },
  updateReader(id, data) {
    return api.put(`/readers/${id}`, data)
  },
  deleteReader(id) {
    return api.delete(`/readers/${id}`)
  }
}

// 借阅 API
export const borrowingApi = {
  getBorrowings(params) {
    return api.get('/borrowings', { params })
  },
  borrowBook(data) {
    return api.post('/borrowings', data)
  },
  returnBook(id) {
    return api.put(`/borrowings/${id}/return`)
  }
}

// 统计 API
export const statsApi = {
  getStats() {
    return api.get('/stats')
  }
}
