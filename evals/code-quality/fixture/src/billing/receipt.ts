import { Pence, format } from './money';

export const receiptLine = (sku: string, amount: Pence): string => `${sku}  ${format(amount)}`;
