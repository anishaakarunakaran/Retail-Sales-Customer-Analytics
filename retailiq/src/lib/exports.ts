import Papa from 'papaparse';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import type { Transaction } from './types';

export function exportCSV(data: Record<string, unknown>[], filename: string): void {
  const csv = Papa.unparse(data);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  downloadBlob(blob, filename);
}

export function exportExcel(data: Record<string, unknown>[], filename: string): void {
  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Data');
  const buf = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
  const blob = new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  downloadBlob(blob, filename);
}

export function exportPDF(title: string, headers: string[], rows: (string | number)[][], filename: string, summary?: string[]): void {
  const doc = new jsPDF();
  doc.setFontSize(16);
  doc.text(title, 14, 20);
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 28);

  let y = 35;
  if (summary) {
    doc.setFontSize(9);
    summary.forEach((line) => {
      doc.text(line, 14, y);
      y += 5;
    });
    y += 5;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (doc as any).autoTable({ startY: y, head: [headers], body: rows });
  doc.save(filename);
}

export function exportTransactionsCSV(data: Transaction[], filename: string): void {
  const rows = data.map((r) => ({
    transaction_id: r.transaction_id, transaction_date: r.transaction_date, customer_id: r.customer_id,
    customer_name: r.customer_name, product_name: r.product_name, category: r.category,
    sales_amount: r.sales_amount, quantity: r.quantity, profit_amount: r.profit_amount,
    region: r.region, sales_channel: r.sales_channel,
  }));
  exportCSV(rows, filename);
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
