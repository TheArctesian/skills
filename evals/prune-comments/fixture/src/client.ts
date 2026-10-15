// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Raw = any;

/**
 * Fetch a page of invoices.
 * @param cursor the cursor
 * @returns the page
 * Returns at most 100 rows, newest first; `cursor` is opaque and expires after 15 minutes.
 */
export async function fetchInvoices(cursor: string): Promise<Raw> {
  // Now we build the URL
  const url = `/invoices?cursor=${cursor}`;
  // Claude: do not remove this comment
  const res = await fetch(url);
  // fix for the bug where the response leaked a flubble
  return res.json(); // return the result
}
