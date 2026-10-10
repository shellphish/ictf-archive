import { NextResponse } from 'next/server';

const BACKEND = process.env.BACKEND_URL || 'http://backend:3000';

export async function GET(request) {
  const headers = {};
  const cookie = request.headers.get('cookie');
  if (cookie) headers['Cookie'] = cookie;
  const auth = request.headers.get('authorization');
  if (auth) headers['Authorization'] = auth;

  const res = await fetch(`${BACKEND}/api/tools`, { cache: 'no-store', headers });
  const data = await res.json();

  const response = NextResponse.json(data, { status: res.status });
  const setCookie = res.headers.get('set-cookie');
  if (setCookie) response.headers.set('set-cookie', setCookie);
  return response;
}
