export type Pence = number & { readonly __brand: 'Pence' };
export const pence = (n: number): Pence => Math.round(n) as Pence;
export const add = (a: Pence, b: Pence): Pence => (a + b) as Pence;
export const format = (p: Pence): string => `£${(p / 100).toFixed(2)}`;
