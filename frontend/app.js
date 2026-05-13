// configuracao Auth0 e backend
// API_BASE vazio = mesma origem do front (Flask serve os dois)
const API_BASE = '';
const AUTH0_DOMAIN = 'dev-fa0at04h4b7wjopr.us.auth0.com';
const AUTH0_CLIENT_ID = 'BxckTffhcBLwjPCuLLyWZStHdLapilAs';
const AUTH0_AUDIENCE = 'https://dev-fa0at04h4b7wjopr.us.auth0.com/api/v2/';

// cria o cliente Auth0 (singleton)
let _auth0 = null;
async function getAuth0() {
  if (_auth0) return _auth0;
  _auth0 = await window.auth0.createAuth0Client({
    domain: AUTH0_DOMAIN,
    clientId: AUTH0_CLIENT_ID,
    authorizationParams: {
      audience: AUTH0_AUDIENCE,
      redirect_uri: window.location.origin,
      scope: 'openid email profile',
    },
    cacheLocation: 'localstorage',
  });
  return _auth0;
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

async function authHeaders() {
  const auth0 = await getAuth0();
  const token = await auth0.getTokenSilently();
  return { Authorization: 'Bearer ' + token };
}

async function apiGet(path) {
  const headers = await authHeaders();
  const res = await fetch(API_BASE + path, { method: 'GET', headers });
  return handleResponse(res);
}

async function apiPost(path, body) {
  const headers = await authHeaders();
  const res = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

async function apiDelete(path) {
  const headers = await authHeaders();
  const res = await fetch(API_BASE + path, { method: 'DELETE', headers });
  return handleResponse(res);
}
