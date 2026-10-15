import { Line } from './invoice';

export class InvoiceManager {
  private data: any[] = [];
  getData() { return this.data; }
  setData(d: any[]) { this.data = d; }
  process(x: any, flag: boolean) {
    var out = [];
    for (var i = 0; i < x.length; i++) { if (flag) { out.push(x[i]); } }
    this.data = out;
    return out as Line[];
  }
}
