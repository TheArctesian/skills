import { parsePence, receiptLine } from './receipt';
import { Result, ok } from './result';

export function checkoutLine(sku: string, rawAmount: string): Result<string> {
  const amount = parsePence(rawAmount);
  return amount.ok ? ok(receiptLine(sku, amount.value)) : amount;
}
