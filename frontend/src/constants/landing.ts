export const API_DOCS_URL = 'http://localhost:8000/docs'
export const API_REDOC_URL = 'http://localhost:8000/redoc'
export const GITHUB_URL = 'https://github.com/DmytroHryhorashenko/photoshare-api'

export const STATS = [
  { value: 184, suffix: '+', label: 'Tests Passed' },
  { value: 94, suffix: '%', label: 'Coverage' },
  { value: 0, label: 'JWT Authentication', display: 'JWT' },
  { value: 0, label: 'Cloudinary Integration', display: 'Cloudinary' },
  { value: 0, label: 'Docker Ready', display: 'Docker' },
] as const

export const FEATURES = [
  {
    title: 'Photo Upload',
    description: 'Multipart uploads with validation, stored securely on Cloudinary.',
    icon: 'upload',
  },
  {
    title: 'Cloudinary',
    description: 'Enterprise-grade CDN delivery and on-the-fly transformations.',
    icon: 'cloud',
  },
  {
    title: 'Tags',
    description: 'Organize photos with up to 5 normalized tags per upload.',
    icon: 'tag',
  },
  {
    title: 'Comments',
    description: 'Threaded discussions with owner edit and moderator moderation.',
    icon: 'message',
  },
  {
    title: 'Ratings',
    description: 'Five-star ratings with aggregate summaries per photo.',
    icon: 'star',
  },
  {
    title: 'QR Codes',
    description: 'Share transformed images via scannable QR code links.',
    icon: 'qr',
  },
  {
    title: 'Transformations',
    description: 'Resize, crop, rotate, and apply effects to any photo.',
    icon: 'wand',
  },
  {
    title: 'Search',
    description: 'Filter by keyword, tag, rating, and sort by date or score.',
    icon: 'search',
  },
  {
    title: 'Profiles',
    description: 'Public profiles with upload counts and private account settings.',
    icon: 'user',
  },
  {
    title: 'Admin Panel',
    description: 'Ban users, manage roles, and moderate platform content.',
    icon: 'shield',
  },
  {
    title: 'JWT Security',
    description: 'Bearer tokens, blacklist on logout, and role-based access.',
    icon: 'lock',
  },
  {
    title: 'Docker',
    description: 'Containerized API, database, and optional frontend stack.',
    icon: 'container',
  },
] as const

export const ARCHITECTURE = [
  'React Frontend',
  'FastAPI',
  'SQLAlchemy',
  'PostgreSQL',
  'Cloudinary',
  'QR Generator',
] as const

export const TECH_STACK = [
  'Python',
  'FastAPI',
  'React',
  'TypeScript',
  'Tailwind',
  'PostgreSQL',
  'SQLAlchemy',
  'Docker',
  'JWT',
  'Cloudinary',
  'Pytest',
] as const

export const API_ENDPOINTS = [
  { method: 'GET', path: '/api/v1/photos/search', color: 'text-emerald-400' },
  { method: 'POST', path: '/api/v1/photos', color: 'text-violet-400' },
  { method: 'POST', path: '/api/v1/auth/login', color: 'text-cyan-400' },
  { method: 'GET', path: '/api/v1/users/me', color: 'text-amber-400' },
] as const

export const METRICS = [
  { label: '184 Tests', icon: 'tests' },
  { label: '94% Coverage', icon: 'coverage' },
  { label: 'REST API', icon: 'api' },
  { label: 'Swagger', icon: 'swagger' },
  { label: 'Docker', icon: 'docker' },
  { label: 'PostgreSQL', icon: 'database' },
  { label: 'Cloudinary', icon: 'cloud' },
] as const

export const SCREENSHOTS = [
  { title: 'Swagger UI', gradient: 'from-violet-600/40 to-indigo-900/60' },
  { title: 'Gallery', gradient: 'from-cyan-600/40 to-blue-900/60' },
  { title: 'Upload Photo', gradient: 'from-fuchsia-600/40 to-purple-900/60' },
  { title: 'Admin Panel', gradient: 'from-emerald-600/40 to-teal-900/60' },
  { title: 'Profile', gradient: 'from-amber-600/40 to-orange-900/60' },
  { title: 'Landing', gradient: 'from-rose-600/40 to-pink-900/60' },
] as const
