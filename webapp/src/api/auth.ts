import { api, setToken } from './client';

interface LoginRequest {
  jenkins_url: string;
  username: string;
  api_token: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface UserInfo {
  id: string;
  fullName: string;
  [key: string]: unknown;
}

export async function login(data: LoginRequest): Promise<string> {
  const res = await api.post<LoginResponse>('/auth/login', data);
  setToken(res.access_token);
  return res.access_token;
}

export async function verify(): Promise<{ message: string }> {
  return api.get('/auth/verify');
}

export async function getUser(): Promise<UserInfo> {
  return api.get('/auth/user');
}

export function logout() {
  setToken(null);
}
