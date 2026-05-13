// configuracao
// API_BASE vazio = mesma origem do front (Flask serve os dois)
const API_BASE = '';
const AUTH0_DOMAIN = 'dev-fa0at04h4b7wjopr.us.auth0.com';
const AUTH0_CLIENT_ID = 'BxckTffhcBLwjPCuLLyWZStHdLapilAs';
const AUTH0_CLIENT_SECRET = 'bgZk8F2geXhf8oZePf6DQTnDKKtXsxcYyIT4ptmG8W5eM_ynIt0hHAJvNJxGS689';
const AUTH0_AUDIENCE = 'https://dev-fa0at04h4b7wjopr.us.auth0.com/api/v2/';

// login via Resource Owner Password Grant
async function login(email, password) {
  const res = await fetch(`https://${AUTH0_DOMAIN}/oauth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      grant_type: 'http://auth0.com/oauth/grant-type/password-realm',
      realm: 'Username-Password-Authentication',
      username: email,
      password: password,
      audience: AUTH0_AUDIENCE,
      scope: 'openid email',
      client_id: AUTH0_CLIENT_ID,
      client_secret: AUTH0_CLIENT_SECRET,
    }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data.error_description || data.error || 'Falha no login';
    throw new Error(msg);
  }
  if (!data.access_token) {
    throw new Error('Resposta sem access_token');
  }
  return data.access_token;
}

// decodifica JWT (parte do meio em base64url) - sem validar assinatura
function decodeJwt(token) {
  if (!token) return null;
  try {
    const parts = token.split('.');
    if (parts.length < 2) return null;
    let payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    while (payload.length % 4) payload += '=';
    const json = atob(payload);
    const decoded = decodeURIComponent(
      json
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(decoded);
  } catch (e) {
    console.error('decodeJwt falhou', e);
    return null;
  }
}

// erro estruturado pra propagar status
class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.status = status;
    this.payload = payload;
  }
}

function authHeaders() {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: 'Bearer ' + token } : {};
}

async function handleResponse(res) {
  if (res.status === 204) return null;
  const text = await res.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch (e) {
      data = { message: text };
    }
  }
  if (!res.ok) {
    const msg = (data && (data.message || data.error)) || ('HTTP ' + res.status);
    throw new ApiError(msg, res.status, data);
  }
  return data;
}

async function apiGet(path) {
  const res = await fetch(API_BASE + path, {
    method: 'GET',
    headers: { ...authHeaders() },
  });
  return handleResponse(res);
}

async function apiPost(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

async function apiDelete(path) {
  const res = await fetch(API_BASE + path, {
    method: 'DELETE',
    headers: { ...authHeaders() },
  });
  return handleResponse(res);
}
