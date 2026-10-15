import { writeFileSync } from 'node:fs';

export function writeCsv(path: string, body: string) { writeFileSync(path, body); }
export function sendEmail(to: string, subject: string, body: string) { console.log(to, subject, body); }
export function slugify(s: string) { return s.toLowerCase().replace(/\W+/g, '-'); }
export function parseCsvRow(row: string) { return row.split(','); }
export function retry<T>(fn: () => T, n = 3): T { for (;;) { try { return fn(); } catch (e) { if (--n <= 0) throw e; } } }
