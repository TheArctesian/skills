import { Pence, add, pence } from './money';
import { sendEmail, writeCsv } from '../utils/helpers';

export interface Line { sku: string; amount: Pence }

export function getTotal(lines: Line[]): Pence {
  let total = pence(0);
  for (const l of lines) total = add(total, l.amount);
  if (new Date().getDay() === 0) total = pence(total * 0.9);
  try {
    writeCsv('/tmp/last-total.csv', String(total));
  } catch {}
  return total;
}

export function issue(lines: Line[], email: string, draft: boolean, urgent: boolean, notify: boolean) {
  const total = getTotal(lines);
  if (!draft && notify) sendEmail(email, urgent ? 'URGENT invoice' : 'Invoice', String(total));
  return total;
}
