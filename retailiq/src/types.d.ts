declare module 'sql.js' {
  interface SqlJsStatic {
    Database: new (data?: ArrayLike<number>) => Database;
  }
  interface Database {
    run(sql: string, params?: unknown[]): void;
    exec(sql: string): { columns: string[]; values: (string | number | null)[][] }[];
    prepare(sql: string): Statement;
    close(): void;
  }
  interface Statement {
    run(params?: unknown[]): void;
    free(): void;
  }
  export default function initSqlJs(config?: Record<string, unknown>): Promise<SqlJsStatic>;
  export type { SqlJsStatic, Database, Statement };
}

declare module 'jspdf-autotable' {
  import type jsPDF from 'jspdf';
  namespace autoTable {
    function autoTable(doc: jsPDF, options: { startY?: number; head: string[][]; body: (string | number)[][] }): void;
  }
  export default autoTable;
}
