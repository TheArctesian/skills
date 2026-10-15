import { Result, err, ok } from './result';

export type Pence = number & { readonly __brand: 'Pence' };

export function toPence(n: number): Result<Pence> {
  return Number.isSafeInteger(n) && n >= 0 ? ok(n as Pence) : err(`not a pence amount: ${n}`);
}

export function parsePence(input: string): Result<Pence> {
  return /^\d{1,15}$/.test(input) ? toPence(Number(input)) : err(`not a pence amount: ${input}`);
}

export const add = (a: Pence, b: Pence): Pence => (a + b) as Pence;
export const format = (p: Pence): string => `£${(p / 100).toFixed(2)}`;
