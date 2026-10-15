import { Pence, format, pence } from './money';
import { Result, err, ok } from './result';

export function parsePence(input: string): Result<Pence> {
  return /^\d{1,15}$/.test(input) ? ok(pence(Number(input))) : err(`not a pence amount: ${input}`);
}

export const receiptLine = (sku: string, amount: Pence): string => `${sku}  ${format(amount)}`;
