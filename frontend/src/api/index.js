import http from './http'

export const authApi = {
  login: (data) => http.post('/auth/login', data),
  register: (data) => http.post('/auth/register', data)
}

export const userApi = {
  profile: () => http.get('/user/profile'),
  updateProfile: (data) => http.put('/user/profile', data),
  changePassword: (data) => http.put('/user/password', data)
}

export const goalApi = {
  list: () => http.get('/goals'),
  create: (data) => http.post('/goals', data),
  update: (id, data) => http.put(`/goals/${id}`, data),
  remove: (id) => http.delete(`/goals/${id}`)
}

export const checkInApi = {
  list: (goalId) => http.get('/check-ins', { params: { goalId } }),
  create: (data) => http.post('/check-ins', data),
  makeup: (data) => http.post('/check-ins/makeup', data)
}

export const statsApi = {
  dashboard: () => http.get('/stats/dashboard'),
  timeline: (days) => http.get('/stats/timeline', { params: { days } })
}

export const exportApi = {
  checkins: (params) => http.get('/exports/checkins', { params, responseType: 'blob', __skipIntercept: true })
}

export const badgeApi = {
  mine: () => http.get('/badges/mine')
}

export const socialApi = {
  searchUsers: (keyword) => http.get('/social/users/search', { params: { keyword } }),
  friends: () => http.get('/social/friends'),
  friendRequests: () => http.get('/social/friend-requests'),
  requestFriend: (data) => http.post('/social/friend-requests', data),
  acceptFriend: (id) => http.put(`/social/friend-requests/${id}/accept`),
  rejectFriend: (id) => http.put(`/social/friend-requests/${id}/reject`),
  circles: () => http.get('/social/circles'),
  createCircle: (data) => http.post('/social/circles', data),
  joinCircle: (id) => http.post(`/social/circles/${id}/join`),
  leaveCircle: (id) => http.delete(`/social/circles/${id}/leave`),
  posts: (circleId) => http.get(`/social/circles/${circleId}/posts`),
  publishPost: (circleId, data) => http.post(`/social/circles/${circleId}/posts`, data),
  feed: () => http.get('/social/feed')
}
