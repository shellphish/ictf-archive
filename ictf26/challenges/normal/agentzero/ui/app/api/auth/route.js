import { NextResponse } from 'next/server';

const BACKEND = process.env.BACKEND_URL || 'http://backend:3000';

export async function POST(request) {
  const body = await request.text();
  const headers = { 'Content-Type': 'application/json' };
  const cookie = request.headers.get('cookie');
  if (cookie) headers['Cookie'] = cookie;

  const res = await fetch(`${BACKEND}/api/auth`, { method: 'POST', headers, body });
  const data = await res.json();

  const response = NextResponse.json(data, { status: res.status });
  const setCookie = res.headers.get('set-cookie');
  if (setCookie) response.headers.set('set-cookie', setCookie);
  return response;
}
